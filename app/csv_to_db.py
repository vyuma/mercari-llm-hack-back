import pandas as pd
import sqlite3

# CSVファイルを読み込む
csv_file = 'dummy_data.csv'
df = pd.read_csv(csv_file)

# カラム名のスペースをアンダースコアに置換
df.columns = df.columns.str.replace(' ', '_')

# SQLiteデータベースに接続（存在しない場合は作成されます）
conn = sqlite3.connect('dummy_data.db')
cursor = conn.cursor()

# テーブルを作成（新しいスキーマに基づいて）
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    Date TEXT,
    Item TEXT,
    Buyer_Country TEXT,
    Seller_Country TEXT,
    Sale_Price REAL,
    Purchase_Price REAL,
    Sale_Currency TEXT,
    Purchase_Currency TEXT,
    Product_Description TEXT,
    Product_Image TEXT,
    FX_JPY_to_JPY REAL,
    FX_JPY_to_CNY REAL,
    FX_JPY_to_KRW REAL,
    FX_JPY_to_VND REAL,
    FX_JPY_to_THB REAL,
    FX_JPY_to_MYR REAL,
    FX_JPY_to_IDR REAL,
    FX_JPY_to_PHP REAL,
    Sale_Price_in_JPY REAL,
    Purchase_Price_in_JPY REAL,
    Sale_Price_in_CNY REAL,
    Purchase_Price_in_CNY REAL,
    Sale_Price_in_KRW REAL,
    Purchase_Price_in_KRW REAL,
    Sale_Price_in_VND REAL,
    Purchase_Price_in_VND REAL,
    Sale_Price_in_THB REAL,
    Purchase_Price_in_THB REAL,
    Sale_Price_in_MYR REAL,
    Purchase_Price_in_MYR REAL,
    Sale_Price_in_IDR REAL,
    Purchase_Price_in_IDR REAL,
    Sale_Price_in_PHP REAL,
    Purchase_Price_in_PHP REAL
)
''')

# データをテーブルに挿入
df.to_sql('transactions', conn, if_exists='replace', index=False)

# コミットして接続を閉じる
conn.commit()
conn.close()

print("データベースにデータを挿入しました. スペースがアンダースコアに置換されたカラム名になってるから注意．")
