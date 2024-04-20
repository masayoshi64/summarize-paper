# Summarize Paper with LLM

## アプリの起動
- 以下のコマンドでアプリを起動する
```shell
streamlit run app.py
```
- `--debug`オプションをつけるとデバッグモードで起動する
```shell
streamlit run app.py -- --debug
```
## ArXivの論文を要約する
- 入力欄に`https://arxiv.org/abs/0000.00000`の形式でpdfのパスを入力
## pdfの論文を要約する
- 以下のコマンドでGROBIDのサーバーを起動しておく
```shell
docker run --rm --init --ulimit core=0 -p 8070:8070 lfoppiano/grobid:0.8.0
```

- 入力欄に`file:///path/paper.pdf`の形式でpdfのパスを入力