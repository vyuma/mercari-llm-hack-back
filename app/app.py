from flask import Flask, request, jsonify
import sqlite3
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import openai

# 環境変数の読み込み
load_dotenv()

# Flaskアプリケーションの初期化
app = Flask(__name__)

# ChatGPT APIキーの設定
openai.api_key = os.getenv('CHATGPT_API_KEY')

# SQLiteデータベース接続関数（可変DB対応）
def query_db(database, query, args=(), one=False):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row  # 名前ベースで結果を扱えるようにする
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# ニュースをRAGで取得する関数
def get_related_news(database, item):
    query = '''
    SELECT title, description
    FROM regulations
    WHERE item LIKE ?
    LIMIT 5
    '''
    result = query_db(database, query, [f"%{item}%"])
    return result


# ChatGPT APIを使う．規制情報を判断する関数
def ask_chatgpt(role_instruction, prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": role_instruction},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response['choices'][0]['message']['content']
        return answer
    except Exception as e:
        print(f"Error using ChatGPT API: {e}")
        return None


# 購入可能かどうかを確認するエンドポイント
@app.route('/is_eligible_to_buy', methods=['POST'])
def is_eligible_to_buy():
    data = request.get_json()
    user_country = data.get('User Country')
    item = data.get('Item')
    description = data.get('Description')

    # 規制情報をデータベースから取得
    query = '''
    SELECT * FROM regulations
    WHERE country = ? AND item = ?
    '''
    result = query_db('regulations.db', query, [user_country, item])

    if result:
        # ChatGPT APIに投げるプロンプト
        role_instruction = "You are an assistant that checks for item restrictions."
        prompt = f"The following item is being considered for purchase in {user_country}. Is there any restriction on purchasing this item?\n\nItem: {item}\nDescription: {description}\nRegulation Info: {result}"
        chatgpt_response = ask_chatgpt(role_instruction, prompt)
        return jsonify({"eligible": False, "message": chatgpt_response}), 200
    else:
        return jsonify({"eligible": True, "message": "You are eligible to buy this item."}), 200

# 出品可能かどうかを確認するエンドポイント
@app.route('/is_proper_to_sell', methods=['POST'])
def is_proper_to_sell():
    data = request.get_json()
    title = data.get('Title')
    description = data.get('Description')
    image = data.get('Image')
    areas = data.get('Areas')  # 対象となる販売エリア

    restricted_countries = []

    # 各販売エリアに対して規制情報をチェック
    for country in areas:
        query = '''
        SELECT * FROM regulations
        WHERE country = ? AND ? LIKE '%' || item || '%'
        '''
        result = query_db('regulations.db', query, [country, description])

        if result:
            restricted_countries.append(country)

    if restricted_countries:
        # ChatGPT APIに投げるプロンプト
        role_instruction = "You are an assistant that checks for item restrictions."
        prompt = f"The following item is being considered for sale in {', '.join(areas)}. Are there any restrictions for selling this item in the listed countries?\n\nItem: {title}\nDescription: {description}\nRegulation Info: {restricted_countries}"
        chatgpt_response = ask_chatgpt(role_instruction, prompt)
        return jsonify({
            "message": chatgpt_response,
            "restricted_countries": restricted_countries
        }), 200
    else:
        return jsonify({
            "message": "This item can be sold in all specified countries."
        }), 200








# 1ヶ月および6ヶ月の期間のデータを取得するクエリ
def get_sales_data_for_period(database, days):
    query = '''
    SELECT Item, Buyer_Country, COUNT(*) as count
    FROM transactions
    WHERE Date >= ?
    GROUP BY Item, Buyer_Country
    '''
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    result = query_db(database, query, [cutoff_date])
    return result

# アイテムの伸び率を計算
def calculate_growth_rate(database):
    # 直近1ヶ月のデータ取得
    recent_sales = get_sales_data_for_period(database, 30)
    # 過去6ヶ月のデータ取得
    past_sales = get_sales_data_for_period(database, 180)
    # 平均を取るための日数の比
    days_ratio = 180 / 30

    # データフレームに変換
    recent_df = pd.DataFrame(recent_sales, columns=['Item', 'Buyer_Country', 'count'])
    past_df = pd.DataFrame(past_sales, columns=['Item', 'Buyer_Country', 'count'])

    # 全期間でデータをマージ（外部結合して、データがないアイテムの伸び率を0にする）
    merged_df = pd.merge(recent_df, past_df, on=['Item', 'Buyer_Country'], how='outer', suffixes=('_recent', '_past')).fillna(0)

    # 伸び率を計算 ((最近の頻度 - 過去の頻度) / 過去の頻度)
    merged_df['growth_rate'] = (merged_df['count_recent'] - (merged_df['count_past'] / days_ratio)) / (merged_df['count_past'].replace(0, 1) / days_ratio)

    return merged_df

# 伸び率に基づくTOP10ランキングを取得
def get_top_10_ranking_by_growth(database):
    # 伸び率計算
    merged_df = calculate_growth_rate(database)

    # Buyer Countryごとのランキング
    buyer_country_ranking = merged_df.groupby('Buyer_Country').apply(lambda x: x.nlargest(10, 'growth_rate')).reset_index(drop=True)

    # 全体でのランキング
    overall_ranking = merged_df.nlargest(10, 'growth_rate')

    # 各商品の国ごとのスコア（売れ行きのスコア）
    country_sales_scores = merged_df.groupby(['Item', 'Buyer_Country'])['count_recent'].sum().reset_index()

    return buyer_country_ranking, overall_ranking, country_sales_scores


# 売れそうランキングTOP10を返すエンドポイント
@app.route('/get_ranking', methods=['GET'])
def get_ranking():
    database = 'dummy_data.db'  # データベース名
    # Buyer CountryごとのTOP10と全体のTOP10を取得
    buyer_country_ranking, overall_ranking, country_sales_scores = get_top_10_ranking_by_growth(database)

    # レスポンス形式に変換
    buyer_country_ranking_response = buyer_country_ranking.groupby('Buyer_Country').apply(
        lambda x: [{"Item": row['Item'], "Growth Rate": row['growth_rate']} for _, row in x.iterrows()]
    ).to_dict()

    # Growth Rateは率なので * 100すると何%の成長率かが出る．
    overall_ranking_response = [{"Item": row['Item'], "Growth Rate": row['growth_rate']} for _, row in overall_ranking.iterrows()]

    # 各商品の国ごとの売れ行きスコア
    country_sales_scores_response = country_sales_scores.groupby('Item').apply(
        lambda x: [{"Country": row['Buyer_Country'], "Sales Score": row['count_recent']} for _, row in x.iterrows()]
    ).to_dict()

    # レスポンスを返す
    return jsonify({
        "BuyerCountryRanking": buyer_country_ranking_response,
        "OverallRanking": overall_ranking_response,
        "CountrySalesScores": country_sales_scores_response
    })



@app.route('/predict_ranking', methods=['GET'])
def predict_ranking():
    database = 'dummy_data.db'
    
    # まずランキングを取得
    _, overall_ranking, country_sales_scores = get_top_10_ranking_by_growth(database)
    
    # トップ5のアイテムを取得
    top_5_items = overall_ranking['Item'][:5].tolist()

    # アイテムに関連するニュースをRAGで取得
    ranking_with_news = []
    for item in top_5_items:
        related_news = get_related_news('regulations.db', item)  # ニュースデータベース
        country_scores = country_sales_scores[country_sales_scores['Item'] == item]
        ranking_with_news.append({
            "item": item,
            "related_news": related_news,
            "country_scores": [{"Country": row['Buyer_Country'], "Sales Score": row['count_recent']} for _, row in country_scores.iterrows()]
        })

    # ChatGPTに投げるプロンプトを作成
    prompt = "Here is the top 5 ranking of items, related news, and country-wise sales scores:\n\n"
    for rank, entry in enumerate(ranking_with_news, 1):
        prompt += f"Rank {rank}: {entry['item']}\n"
        prompt += "Related News:\n"
        for news in entry['related_news']:
            prompt += f"- Title: {news['title']}, Description: {news['description']}\n"
        prompt += "Country-wise Sales Scores:\n"
        for score in entry['country_scores']:
            prompt += f"- {score['Country']}: {score['Sales Score']} sales\n"
        prompt += "\n"

    prompt += "Based on this information, which item would you recommend as the best item to sell right now?"

    # ChatGPT APIに投げる
    role_instruction = "You are an expert analyst who provides advice on the best items to sell based on current sales trends and news."
    chatgpt_response = ask_chatgpt(role_instruction, prompt)

    # 結果を返す
    return jsonify({
        "ranking": ranking_with_news,
        "chatgpt_recommendation": chatgpt_response
    })




# ItemとBuyer Countryを指定されたら、該当するItemのDate, Purchase Price in {Buyer Country}をSeller Country別に返す機能
@app.route('/get_purchase_price', methods=['GET'])
def get_purchase_price():
    database = 'dummy_data.db'  # データベース名
    # クエリパラメータからItem、Buyer Country、Seller Countryを取得
    item = request.args.get('Item')
    buyer_country = request.args.get('Buyer Country')
    seller_country = request.args.get('Seller Country')  # Optional: 追加のSeller Country指定
    
    # 購入国の通貨コードを取得
    currency_codes = {
        'Japan': 'JPY',
        'China': 'CNY',
        'South Korea': 'KRW',
        'Vietnam': 'VND',
        'Thailand': 'THB',
        'Malaysia': 'MYR',
        'Indonesia': 'IDR',
        'Philippines': 'PHP'
    }
    buyer_currency = currency_codes.get(buyer_country)

    if not buyer_currency:
        return jsonify({"error": "Invalid Buyer Country"}), 400

    # SQLクエリで該当するアイテムと国のデータを取得
    if seller_country:
        query = f'''
        SELECT Seller_Country, Date, Purchase_Price_in_{buyer_currency}
        FROM transactions
        WHERE Item = ? AND Buyer_Country = ? AND Seller_Country = ?
        '''
        result = query_db(database, query, [item, buyer_country, seller_country])
    else:
        query = f'''
        SELECT Seller_Country, Date, Purchase_Price_in_{buyer_currency}
        FROM transactions
        WHERE Item = ? AND Buyer_Country = ?
        '''
        result = query_db(database, query, [item, buyer_country])

    if not result:
        return jsonify({"error": "No data found for the specified Item and Buyer Country"}), 404

    # Seller Countryごとにデータをグループ化
    grouped_data = {}
    for row in result:
        seller = row['Seller_Country']
        if seller not in grouped_data:
            grouped_data[seller] = []
        grouped_data[seller].append({
            "Date": row['Date'],
            f"Purchase Price in {buyer_currency}": row[f"Purchase_Price_in_{buyer_currency}"]
        })

    # レスポンス形式に変換
    response = [{"SellerCountry": seller, "Prices": prices} for seller, prices in grouped_data.items()]
    
    return jsonify(response)




@app.route('/recommend_purchase', methods=['GET'])
def recommend_purchase():
    database = 'dummy_data.db'  # データベース名
    
    # クエリパラメータからItem、Buyer Country、Seller Countryを取得
    item = request.args.get('Item')
    buyer_country = request.args.get('Buyer Country')
    seller_country = request.args.get('Seller Country')  # Optional: 追加のSeller Country指定
    
    # 過去の価格データを取得
    past_prices_query = f'''
    SELECT Seller_Country, Date, Purchase_Price_in_{buyer_country}
    FROM transactions
    WHERE Item = ? AND Buyer_Country = ?
    '''
    if seller_country:
        past_prices_query += ' AND Seller_Country = ?'
        past_prices = query_db(database, past_prices_query, [item, buyer_country, seller_country])
    else:
        past_prices = query_db(database, past_prices_query, [item, buyer_country])

    if not past_prices:
        return jsonify({"error": "No past price data found for the specified item and buyer country"}), 404

    # 価格変動データを整理
    price_history = [{"Date": row["Date"], "Price": row[f"Purchase_Price_in_{buyer_country}"]} for row in past_prices]

    # ニュースデータをRAGで取得
    related_news = get_related_news('regulations.db', item)

    # 価格変動とニュース情報をChatGPTに投げて、買うべきかを判断
    price_trend = "The price trend of this item shows the following fluctuations:\n"
    for price in price_history:
        price_trend += f"- {price['Date']}: {price['Price']} {buyer_country}\n"

    news_info = "Here are some related news articles:\n"
    for news in related_news:
        news_info += f"- Title: {news['title']}, Description: {news['description']}\n"

    # ChatGPTに投げるプロンプトを作成
    prompt = price_trend + "\n" + news_info
    prompt += "\nConsidering this information, would you recommend buying this item now, or should we wait?"

    # ChatGPT APIを使用して意思決定
    role_instruction = "You are an expert market analyst. Your task is to advise buyers whether they should purchase an item now based on price trends and market news."
    chatgpt_response = ask_chatgpt(role_instruction, prompt)

    # 結果を返す
    return jsonify({
        "price_history": price_history,
        "related_news": related_news,
        "chatgpt_recommendation": chatgpt_response
    })





# Flaskサーバを実行
if __name__ == '__main__':
    app.run(debug=True)
