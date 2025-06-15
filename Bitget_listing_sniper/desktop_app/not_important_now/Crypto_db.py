import sqlite3
import requests
import datetime
import os

# الاتصال بقاعدة البيانات (أو إنشائها إذا لم تكن موجودة)
BASE_DIR = os.path.dirname(__file__)

conn = sqlite3.connect(os.path.join(BASE_DIR,'..','Local.db'))
cursor = conn.cursor()

# إنشاء جدول 'new'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        platform TEXT NOT NULL,
        time TEXT NOT NULL
    );
''')

# إنشاء جدول 'binance'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS binance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        status TEXT,
        baseAsset TEXT,
        quoteAsset TEXT,
        addtime TEXT NOT NULL
    );
''')

# إنشاء جدول 'bitget'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bitget (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        status TEXT,
        baseAsset TEXT,
        quoteAsset TEXT,
        addtime TEXT NOT NULL
    );
''')
# حفظ التغييرات وإغلاق الاتصال
conn.commit()
conn.close()

def get_all_trading_pairs() -> list:
    url = 'https://api.bitget.com/api/v2/spot/public/symbols'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        trading_pairs = data.get('data', [])
        pairs_info = [
            {
                'symbol': pair['symbol'],
                'base_coin': pair['baseCoin'],
                'quote_coin': pair['quoteCoin'],
                'status': pair['status'],
                'min_trade_amount': pair['minTradeAmount'],
                'max_trade_amount': pair['maxTradeAmount']
            }
            for pair in trading_pairs if pair['status'] == 'online' and pair['quoteCoin'] == "USDT"
        ]
        return pairs_info
    else:
        print(f"Error: {response.status_code}")
        return []

db = sqlite3.connect("Local.db")
cursor = db.cursor()
all_pairs = get_all_trading_pairs()

for c in all_pairs:
    cursor.execute("INSERT INTO bitget (symbol,status,baseAsset,quoteAsset,addtime) VALUES (?,?,?,?,?)",(str(c["symbol"]),str(c["status"]),str(c["base_coin"]),str(c["quote_coin"]),str(datetime.datetime.now().timestamp())))

db.commit()
db.close()