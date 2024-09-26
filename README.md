# ディレクトリの説明

preprocess
- Mercari_hackathon.ipynb : ダミーデータ生成のためのnotebook
static
- dummy_data.csv : 生成されたダミーデータ
app
- app.py : 本体
- csv_to_db.py : csvからdbにデータを送り込むスクリプト
- db_debug.py : デバッグ用
- dummy_data.db : データ格納用データベース


# Usage

appディレクトリ直下でpython3 app.pyで起動

こんな感じでアクセスする．


## 買い手が値段の推移のチャートを見るとき
```
http://127.0.0.1:5000/get_purchase_price?Item=Pins/Badges&Buyer%20Country=Japan
```

Itemは以下  
    'Pins/Badges', 'Figures (Comic/Anime)', 'Plush Toys', 'Acrylic Stands',
    'Digital Camera', 'K-POP/Asia Goods', 'Idol Goods', 'Character Keychains',
    'Ladies’ Bags', 'Pokemon Cards'

Buyer Countryは以下  
'Japan', 'China', 'South Korea', 'Vietnam', 'Thailand', 'Malaysia', 'Indonesia', 'Philippines'


## 売り手がトレンドの商品を見たい時
to be continued



開発時は環境はvenvでやってた  


