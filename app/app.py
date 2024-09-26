from flask import Flask, request, jsonify
import sqlite3

# Flaskアプリケーションの初期化
app = Flask(__name__)

# SQLiteデータベースに接続する関数
def query_db(query, args=(), one=False):
    conn = sqlite3.connect('dummy_data.db')
    conn.row_factory = sqlite3.Row  # 名前ベースで結果を扱えるようにする
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

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

    # SQLクエリで該当するアイテムと国のデータを取得
    price_column = f"Purchase_Price_in_{buyer_currency}"  
    query = f'''
    SELECT Date, {price_column}
    FROM transactions
    WHERE Item = ? AND Buyer_Country = ?
    '''
    
    result = query_db(query, [item, buyer_country])

    if not result:
        return jsonify({"error": "No data found for the specified Item and Buyer Country"}), 404

    # 結果を辞書に変換
    result_list = [{"Date": row["Date"], f"Purchase Price in {buyer_currency}": row[price_column]} for row in result]
    
    # JSON形式で返す
    return jsonify(result_list)

# Flaskサーバを実行
if __name__ == '__main__':
    app.run(debug=True)
