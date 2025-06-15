import sqlite3,os
import requests
from datetime import datetime

url = 'https://api.bitget.com/api/v2/spot/public/symbols'
headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

BASE_DIR = os.path.dirname(__file__)

db = sqlite3.connect(os.path.join(BASE_DIR,'..','Local.db'))
cursor = db.cursor()

# جلب بيانات الأزواج من Bitget
response = requests.get(url, headers=headers)
data = response.json()

# التحقق من نجاح الاستجابة
if data.get("code") == "00000":
    symbols = data["data"]
    count = 0

    for item in symbols:
        symbol = item["symbol"]
        status = item["status"]
        baseAsset = item["baseCoin"]
        quoteAsset = item["quoteCoin"]
        addtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT INTO bitget (symbol, status, baseAsset, quoteAsset, addtime)
            VALUES (?, ?, ?, ?, ?)
        ''', (symbol, status, baseAsset, quoteAsset, addtime))
        
        count += 1

    db.commit()
    print(f"✅ تم إضافة {count} زوجًا جديدًا إلى قاعدة البيانات.")
else:
    print("❌ فشل في جلب البيانات من API:", data.get("msg"))

db.close()
