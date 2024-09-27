# mercariハッカソンバックエンド用リポジトリ

## ディレクトリの説明

preprocess/
- Mercari_hackathon.ipynb : ダミーデータ生成のためのnotebook

static/
- dummy_data.csv : 生成されたダミーデータ

app/
- app.py : 本体
- csv_to_db.py : csvからdbにデータを送り込むスクリプト
- db_debug.py : デバッグ用
- dummy_data.db : データ格納用データベース


## Usage

開発時は環境はvenvでやってた  

1. requirements.txtで必要物をインストール
2. appディレクトリ直下で`python3 app.py`で起動

こんな感じでアクセスする．


### 買い手が商品の値段の推移のチャートを見るとき(get_purchase_price)
クエリ
```
http://127.0.0.1:5000/get_purchase_price?Item=Pins/Badges&Buyer%20Country=Japan
```

返り値
<img width="259" alt="スクリーンショット 2024-09-27 10 11 21" src="https://github.com/user-attachments/assets/b084405c-95dc-4f91-a2d7-f617e5b73e7b">
<img width="359" alt="スクリーンショット 2024-09-27 10 12 07" src="https://github.com/user-attachments/assets/05f9697e-9063-4e36-8e86-88b4e0da3cb9">


Itemは以下  
    'Pins/Badges', 'Figures (Comic/Anime)', 'Plush Toys', 'Acrylic Stands',
    'Digital Camera', 'K-POP/Asia Goods', 'Idol Goods', 'Character Keychains',
    'Ladies’ Bags', 'Pokemon Cards'

Buyer Countryは以下  
'Japan', 'China', 'South Korea', 'Vietnam', 'Thailand', 'Malaysia', 'Indonesia', 'Philippines'

機能:過去の同一(類似)商品の値段の推移を国別に可視化

### 売り手がトレンドの商品を見たい時(get_ranking)
クエリ
```
http://127.0.0.1:5000/get_ranking
```

返り値
<img width="401" alt="スクリーンショット 2024-09-27 10 12 54" src="https://github.com/user-attachments/assets/7fd19227-d085-48e2-a579-b386de6b8970">




機能:国別の急上昇ランキングを表示(過去1ヶ月の購買数 / 過去半年間の1ヶ月あたりの平均購買数)

### 買い手が商品を買えるかバリデーション(is_eligible_to_buy)
クエリ
```
curl -X POST http://127.0.0.1:5000/is_eligible_to_buy \
     -H "Content-Type: application/json" \
     -d '{
           "User Country": "Japan",
           "Item": "Alcohol",
           "Description": "A high-quality bottle of Japanese whiskey."
         }'
```

返り値
```
{
  "eligible": true,
  "message": "You are eligible to buy this item."
}
```

機能:商品が規制に引っかかってないかLLMが判断した結果を返してくれる、T/F+理由

### 売り手が出品する商品のバリデーション(is_proper_to_sell)

```
curl -X POST http://127.0.0.1:5000/is_proper_to_sell \
     -H "Content-Type: application/json" \
     -d '{
           "Title": "Japanese Whiskey",
           "Description": "A high-quality bottle of Japanese whiskey.",
           "Image": "whiskey_image.jpg",
           "Areas": ["Japan", "USA", "China"]
         }'
```

返り値
```
{
  "message": "This item can be sold in all specified countries."
}
```

機能:売る際の商品説明やタイトルがどこかの国の規制に引っかかるかをLLMが判断


todo
同一商品とは？画像認識で類似性が閾値以上？
NewsApiより多く各国のニュースをスクレイピングするスクリプト




