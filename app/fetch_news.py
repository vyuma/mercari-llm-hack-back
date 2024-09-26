from newsapi import NewsApiClient
import sqlite3
import datetime
from dotenv import load_dotenv
import os

# 環境変数の読み込み
load_dotenv()

# NewsAPIの初期化
news_api_key = os.getenv('NEWS_API_KEY')
newsapi = NewsApiClient(api_key=news_api_key)

# SQLiteデータベースに接続
conn = sqlite3.connect('regulations.db')
cursor = conn.cursor()

# 規制情報のためのテーブルを作成
cursor.execute('''
CREATE TABLE IF NOT EXISTS regulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country TEXT,
    item TEXT,
    title TEXT,
    description TEXT,
    url TEXT,
    published_at TEXT
)
''')

# ニュースを取得しデータベースに保存
def fetch_and_store_regulation_news(keyword, country):
    # 今日の日付を取得
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    print(f"Fetching top headlines for {country} and keyword {keyword}...")
    
    # トップヘッドラインを取得
    try:
        top_headlines = newsapi.get_top_headlines(
            country=country.lower(),  # 例: 'jp' は日本
            page_size=10  # 最大10件取得
        )

        # APIレスポンスをデバッグ表示
        print(f"API Response: {top_headlines}")

        if top_headlines['status'] == 'ok' and top_headlines['totalResults'] > 0:
            # ニュースをデータベースに格納
            for article in top_headlines['articles']:
                print(f"Inserting article: {article['title']}")  # 挿入する記事タイトルを表示
                cursor.execute('''
                    INSERT INTO regulations (country, item, title, description, url, published_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (country, keyword, article['title'], article['description'], article['url'], article['publishedAt']))

            conn.commit()
        else:
            print(f"No news found for {country} and keyword {keyword}.")
    except Exception as e:
        print(f"Error fetching or inserting news for {country}: {e}")

# メイン処理
if __name__ == "__main__":
    # 特定のキーワードや国に関連するニュースを取得
    items = ['Restriction']  # 規制情報
    # List of countries (Japan, Southeast Asia, East Asia. ベトナム除外)
    countries = ['JP', 'CN', 'KR', 'TH', 'MY', 'ID', 'PH', 'US']

    for item in items:
        for country in countries:
            fetch_and_store_regulation_news(item, country)

# コミットして接続を閉じる
conn.close()
