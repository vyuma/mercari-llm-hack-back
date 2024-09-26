import sqlite3

# SQLiteデータベースに接続
conn = sqlite3.connect('dummy_data.db')
cursor = conn.cursor()

# テーブルのスキーマを取得
cursor.execute("PRAGMA table_info(transactions)")
columns = cursor.fetchall()

# 各カラムの名前を表示
for column in columns:
    print(column[1])

conn.close()
