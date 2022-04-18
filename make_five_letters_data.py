import sqlite3
from collections import Counter

import pandas as pd

# 辞書はこちらからsqliteのものをダウンロードしてください
# https://kujirahand.com/web-tools/EJDictFreeDL.php
DICT_PATH = "/Users/esuji/Downloads/ejdic-hand-sqlite/ejdict.sqlite3"
CSV_PATH = "./five_letters_words_dict.csv"


def count_mucth(text, target):
    count = 0
    for l in list(target):
        if text.lower().find(l) != -1:
            count += 1
    return count


def count_same(text):
    return max([c for c in Counter(text.lower()).values()])


try:
    con = sqlite3.connect(DICT_PATH)
except sqlite3.OperationalError as e:
    print("sqliteファイルが見つかりませんでした。DICT_PATHに正しいパスを設定してください")
    raise (e)
cur = con.cursor()

df = pd.read_sql_query("select * from items;", con)
df5 = df[df.word.apply(lambda x: len(x) == 5 and set(x).isdisjoint(set(list(".- 'éêèïô"))))].drop_duplicates("word")
df5["word"] = df5.word.apply(str.lower)
df5["boin_num"] = df5.word.apply(lambda x: count_mucth(x, "aiueo"))
df5["same_num"] = df5.word.apply(lambda x: count_same(x))
df5 = df5.drop_duplicates("word")
df5.to_csv(CSV_PATH, index=False)
