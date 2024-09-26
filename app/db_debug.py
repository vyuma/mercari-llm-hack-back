import sqlite3

# SQLiteデータベースに接続
conn = sqlite3.connect('regulations.db')
cursor = conn.cursor()

# テーブルのスキーマを取得
cursor.execute("PRAGMA table_info(regulations)")
columns = cursor.fetchall()

# 各カラムの名前を表示
for column in columns:
    print(column[1])


# データを取得して表示
cursor.execute("SELECT * FROM regulations LIMIT 5")
rows = cursor.fetchall()

# データを表示
for row in rows:
    print(row)





# # テーブルのスキーマを取得
# cursor.execute("PRAGMA table_info(transactions)")
# columns = cursor.fetchall()

# # 各カラムの名前を表示
# for column in columns:
#     print(column[1])


# # データを取得して表示
# cursor.execute("SELECT * FROM transactions LIMIT 5")
# rows = cursor.fetchall()

# # データを表示
# for row in rows:
#     print(row)





conn.close()
