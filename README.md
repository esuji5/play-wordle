# play-wordle
solve and play Wordle
Python3.7で動作確認をしていますが、playwrightが動けばそれ以上でもおそらく動作します

## prepare
- `pip install -r requirements.txt` （必須）
- 辞書の準備（必須）
    - こちらからsqlite形式の辞書をダウンロード・解凍してください https://kujirahand.com/web-tools/EJDictFreeDL.php
    - `make_five_letters_data.py` を開きDICT_PATHを設定してから実行してください
    - `five_letters_words_dict.csv` が作成されていれば完了
- Slackへの投稿準備（オプション）
    - 投稿用のWebhook URLを用意し、exportコマンドや.envファイルなどで `SLACK_POST_CHANNEL_URL` に設定してください

## play wordle in browser
- ブラウザを表示して実行
    - `python main.py main False`
- ブラウザを非表示で実行(headless)
    - `python main.py main True`
