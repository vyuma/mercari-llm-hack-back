from flask import Flask, request, jsonify
import pandas as pd

# Flaskアプリケーションの初期化
app = Flask(__name__)

# ダミーデータを読み込む
# 事前にアップロードされたデータファイル "dummy_data.csv" を使用
df = pd.read_csv('dummy_data.csv')

# Date列をdatetime形式に変換
df['Date'] = pd.to_datetime(df['Date'])

# APIエンドポイントの定義
@app.route('/get_purchase_price', methods=['GET'])
def get_purchase_price():
    # クエリパラメータからItemとBuyer Countryを取得
    item = request.args.get('Item')
    buyer_country = request.args.get('Buyer Country')
    
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

    # ItemとBuyer Countryでフィルタリング
    filtered_df = df[(df['Item'] == item)]

    if filtered_df.empty:
        return jsonify({"error": "No data found for the specified Item"}), 404

    # 'Purchase Price in {Buyer Country}'の列名を動的に作成
    price_column = f'Purchase Price in {buyer_currency}'
    
    if price_column not in filtered_df.columns:
        return jsonify({"error": f"No data available for {buyer_country} in the specified item"}), 404

    # 必要な列だけを抽出
    result = filtered_df[['Date', price_column]].to_dict(orient='records')

    # JSON形式で返す
    return jsonify(result)

# Flaskサーバを実行
if __name__ == '__main__':
    app.run(debug=True)
