import requests
import argparse
import re

import streamlit as st
from langchain.globals import set_debug
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from bs4 import BeautifulSoup


template = """英語の研究論文の一部を日本語で要約するタスクを行います。
これは「{paper_title}」というタイトルの論文の「{section_title}」というセクションの文章です。
以下のルールに従ってください。

・リスト形式で出力する (先頭は - を使う)
・タブによるインデントを使って論理的な構造を表現する
・不明な単語や人名，専門用語と思われるものは英語のまま表示する
・最後に文章に含まれる重要な数式を日本語で丁寧にリスト形式で説明する
・タブでインデントした後に数式に現れる記号や変数の意味を説明する
・数式はmarkdown形式で記述し，$で括る

それでは開始します。

英語の論文の一部:
{section_text}

日本語で要約した文章:"""


def fetch_paper(url):
    url = url.replace('arxiv', 'ar5iv')   
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    try:
        paper_title = soup.find("h1").text
    except AttributeError:
        print("タイトルが見つかりませんでした")
        paper_title = "不明なタイトル"

    sections = []
    for section_element in soup.find_all("section", class_="ltx_section"):
        try:
            section_title = section_element.find("h2").text.strip()
        except AttributeError:
            print("セクションタイトルが見つかりませんでした")
            section_title = "不明なセクション"
        section_text = ""
        for paragraph_element in section_element.find_all("div"):
            section_text += paragraph_element.text + "\n"
        section_text = section_text.strip()
        sections.append((section_title, section_text))
    
    return paper_title, sections


def parse_paper(url):
    paper_path = url.replace("file://", "")
    response = requests.post(
        "http://localhost:8070/api/processFulltextDocument", 
        files=[("input", (open(paper_path, "rb")))]
    )
    soup = BeautifulSoup(response.text, features="xml")
    paper_title = soup.find("title").text
    
    sections = []
    for head in soup.find_all("head", n=re.compile("^\d+$")):
        section_title = head.text
        section_element = head.parent
        section_text = ""
        for paragraph_element in section_element.find_all("p"):
            section_text += paragraph_element.text + "\n"
        section_text = section_text.strip()
        sections.append((section_title, section_text))
    
    return paper_title, sections


def summarize_section(paper_title, section_title, section_text, model_name):
    model = ChatOpenAI(model_name=model_name)
    prompt = ChatPromptTemplate.from_template(template)
    output_parser = StrOutputParser()
    chain = prompt | model | output_parser

    result = chain.invoke({
        "paper_title": paper_title, 
        "section_title": section_title, 
        "section_text": section_text
    })

    return result


def main():
    url = st.text_input('Enter URL')
    paper_type = st.radio(label='形式を指定してください',
                    options=('ar5iv', 'pdf'),
                    index=0,
                    horizontal=True,
    )

    if st.button('Summarize'):
        if paper_type == 'ar5iv':
            paper_title, sections = fetch_paper(url)
        elif paper_type == 'pdf':
            paper_title, sections = parse_paper(url)
        else:
            st.write('Error')
            return

        st.write("## " + paper_title)

        for section_title, section_text in sections:
            section_summary = summarize_section(paper_title, section_title, section_text, "gpt-3.5-turbo")
            st.write("### " + section_title)
            st.write(section_summary)
            st.write("---")
        
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    load_dotenv()
    set_debug(args.debug)
    main()