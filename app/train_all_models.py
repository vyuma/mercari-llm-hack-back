import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import numpy as np
import pandas as pd

# Currency codes mapping
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

# 保存先ディレクトリの作成
if not os.path.exists('saved_models'):
    os.makedirs('saved_models')

# モデル作成
def create_model(input_shape):
    model = Sequential()
    model.add(LSTM(50, activation='relu', input_shape=input_shape, return_sequences=True))
    model.add(LSTM(50, activation='relu'))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    return model

# モデルのトレーニング
def train_model(df, item, buyer_country, epochs=5):
    df['Date'] = pd.to_datetime(df['Date'])
    df_filtered = df[(df['Item'] == item) & (df['Buyer_Country'] == buyer_country)]
    df_filtered = df_filtered.sort_values(by='Date')

    prices = df_filtered[f'Purchase Price in {currency_codes[buyer_country]}'].values
    X = []
    y = []
    
    for i in range(30, len(prices)):
        X.append(prices[i-30:i])
        y.append(prices[i])
    
    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    model = create_model((X.shape[1], 1))
    model.fit(X, y, epochs=epochs, verbose=1)
    
    return model

# モデルを保存
def save_model(model, item, buyer_country):
    file_name = f'saved_models/model_{item}_{buyer_country}.h5'
    model.save(file_name)
    print(f"Model saved to {file_name}")

# メイン処理
if __name__ == "__main__":
    df = pd.read_csv('dummy_data.csv')  # ダミーデータを読み込む
    
    # アイテムと国のリストを取得
    items = df['Item'].unique()
    buyer_countries = df['Buyer_Country'].unique()

    # 各アイテムと国に対してモデルを学習し、保存
    for item in items:
        for buyer_country in buyer_countries:
            print(f"Training model for {item} and {buyer_country}")
            model = train_model(df, item, buyer_country)
            save_model(model, item, buyer_country)
