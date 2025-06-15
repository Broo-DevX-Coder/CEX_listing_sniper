# ===================================================================
import os, subprocess, sys, requests, sqlite3, time ,hmac, hashlib, base64, json, httpx, math
from threading import Thread
from dotenv import load_dotenv
from datetime import datetime
import tkinter as tk
from requests.adapters import HTTPAdapter

# Configuration and Paths ============================================
BASE_DIR = os.path.dirname(__file__)
TELEGRAM_BOT_TOKEN = os.getenv("telegram_bot_token")
TELEGRAM_account_CHAT_ID = os.getenv("telegram_chat_id")

# Get .env file =====================================================
load_dotenv(os.path.join(BASE_DIR,".env"))

# ===================================================================
# Class to fetch data from Bitget ===================================
class BitgetData:
    headers = {'User-Agent': 'Mozilla/5.0'}
    adapters = ["https://api.bitget.com/api/"]
    API_SECRET = ""
    API_KEY = ""
    PASSPHRASE = ""
    API = ""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        ada = HTTPAdapter(pool_connections=100,pool_maxsize=100)
        for i in self.adapters:
            self.session.mount(i,ada)

        self._cached_symbol_data = None
    
    # ==============================================
    # All this just to get * pairs and new pairs ===

    def fetch_symbol_data(self):
        # Request all available trading pairs
        url = 'https://api.bitget.com/api/v2/spot/public/symbols'
        try:
            response = self.session.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                self._cached_symbol_data = data.get('data', [])
                return self._cached_symbol_data, None, None
            else:
                return [], "response_code", str(response.status_code)
        except requests.RequestException as e:
            return [], "request_code", str(e)

    # get all trading pairs from SQLite ============
    def get_all_trading_pairs(self):
        # Get all USDT trading pairs that are online ===============
        trading_pairs, error_type, error_info = self.fetch_symbol_data()
        pairs_info = [
            pair['symbol']
            for pair in trading_pairs if pair['status'] == 'online' and pair['quoteCoin'] == "USDT"
        ]
        return set(pairs_info), error_type, error_info
    
    # Get full information for a specific trading pair ==============
    def get_pair_info(self, symbol: str):
        url = f'https://api.bitget.com/api/v2/spot/public/symbols?symbol={symbol}'
        try:
            response = self.session.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                pairs = data.get('data', [])
                return pairs[0], None, None
            else:
                return None, "response_code", str(response.status_code)
        except requests.RequestException as e:
            return None, "request_code", str(e)

    def get_symboles(self, table_name: str, db):
        # Get all stored symbols from database
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        return set([pair[1] for pair in cursor.fetchall()])
    
    # ===============================================
    # But this to Buy/sell pairs ====================

    # HMAC signature ==================
    def generate_signature(self, timestamp, method, request_path, body=''):
        prehash = f"{timestamp}{method}{request_path}{body}"
        signature = hmac.new(
        self.API_SECRET.encode('utf-8'),
        prehash.encode('utf-8'),
        hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()
    
    # to place Buy/Sell orders ==========================
    def place_order(self, symbol:str, side:str, order_type:str ,quantity:dict ,price:dict=None):
        try:
            url = "https://api.bitget.com/api/v2/spot/trade/place-order"
            method = "POST"
            timestamp = str(int(time.time() * 1000))
            safe_amount = math.floor(float(quantity["amount"]) * (10 ** float(quantity["checkScale"]))) / (10 ** float(quantity["checkScale"]))

            body = {
                    "symbol": symbol,      # مثل "BTCUSDT"
                    "side": side,          # "buy" أو "sell"
                    "orderType": order_type,
                    "size": str(safe_amount)
                }

            if order_type == "limit":
                safe_price = math.floor( float(price["price"]) * (10 ** float(price["checkScale"])) ) / (10 ** float(price["checkScale"]))
                body.update({"force":"gtc","price":str(safe_price)})

            body_str = json.dumps(body)
            sign = self.generate_signature(timestamp, method, "/api/v2/spot/trade/place-order", body_str)

            headers = {
                "Content-Type": "application/json",
                "ACCESS-KEY": self.API_KEY,
                "ACCESS-SIGN": sign,
                "ACCESS-TIMESTAMP": timestamp,
                "ACCESS-PASSPHRASE": self.PASSPHRASE
            }

            response = self.session.post(url, headers=headers, data=body_str,timeout=1)

            if response.status_code == 200:
                data = response.json()
                # استخراج الكمية من رصيد الـ BTC أو أي زوج آخر
                return data,None
            else:
                return None,response.text
            
        except requests.RequestException as e:
            return None,str(e)
        
    # To get accont balanses ===========================
    def get_balance(self):
        try:
            timestamp = str(int(time.time() * 1000))
            method = "GET"
            url = "https://api.bitget.com/api/v2/spot/account/assets"
            sign = self.generate_signature(timestamp, method, "/api/v2/spot/account/assets")
    
    
            response = self.session.get(url, headers={
                "Content-Type": "application/json",
                "ACCESS-KEY": self.API_KEY,
                "ACCESS-SIGN": sign,
                "ACCESS-TIMESTAMP": timestamp,
                "ACCESS-PASSPHRASE": self.PASSPHRASE
            })
    
            if response.status_code == 200:
                data = response.json()
                assests = {
                    str(ass["coin"]):{
                        "amount":str(ass["available"]),
                        "frozen":str(ass["frozen"])
                    } 
                    for ass in data["data"] }
                return assests,None
            else:
                return None,response.text
        except requests.RequestException as e:
            return None,str(e)
        
    # To get symbol's curent price ===================
    def get_current_price(self,symbol):
        try:
            url = f"https://api.bitget.com/api/v2/spot/market/tickers?symbol={symbol}"
            response = self.session.get(url)
    
            if response.status_code == 200:
                data = response.json()
                price = data['data'][0]["lastPr"] # السعر الحالي
                return float(price),None
            else:
                return None,response.text
        except requests.RequestException as e:
            return None,str(e)
        
    # Trust the price ============================================
    def trust_buy_price(self,symbol): # -> weighted_price , trust , error
        try:
            url = f"https://api.bitget.com/api/v2/spot/market/orderbook?symbol={symbol}&limit=5"
            response = self.session.get(url,timeout=3)
            trust = 0
            if response.status_code == 200:
                response = response.json()
                asks = response["data"]["asks"]
                bids = response["data"]["bids"]
                asks_prices = [float(ask[0]) for ask in asks]
                asks_contitys = [float(ask[1]) for ask in asks]
                bids_prices = [float(bid[0]) for bid in bids]
                bids_contitys = [float(bid[1]) for bid in bids]
                sellOne = asks_prices[0]
                buyOne = bids_prices[0]
                spread = sellOne - buyOne
                weighted_price = sum(p*q for p,q in zip(asks_prices,asks_contitys)) / sum(asks_contitys)
                price_testing = (sellOne - weighted_price) / weighted_price
                if sum(asks_contitys) == 0:
                    return None,None,"There is not any asks"
                if price_testing <= 0.03:
                    trust += 50
                if spread <= 0.02:
                    trust += 10
                if sum(bids_contitys) >= 100:
                    trust += 10
                if sum(asks_contitys) >= 100:
                    trust += 30
                return [weighted_price,sellOne],trust,None
        except requests.RequestException as e:
            return None,None,e
        

# ===================================================================
# Main Platform + GUI Controller ====================================
class PlatformBot:
    account = ""
    platform = ""
    platform_data:BitgetData = None
    DB_NAME = ""

    def __init__(self):
        self.DB_DIR = os.path.join(BASE_DIR, self.DB_NAME)
        self.firt_time_run = True
        self.cash_pairs = None
        self.cash_pairs_ok = False

        # Create GUI window
        self.root = tk.Tk()
        self.root.title(f"Status Window -{self.account}- -{self.platform}-")
        self.root.geometry("600x300")
        self.root.resizable(True, False)
        self.root.configure(bg="#f0f0f0")

        self.platform_status = tk.Label(self.root, text="Platform Status: ---", font=("Arial", 14), bg="#f0f0f0")
        self.platform_status.pack(pady=5)

        self.platform_status_speed = tk.Label(self.root, text="Request in: ---", font=("Arial", 14), bg="#f0f0f0")
        self.platform_status_speed.pack(pady=5)

        self.new_listbox = tk.Listbox(self.root, font=("Arial", 12), fg="green", height=10)
        self.new_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Restart the script after r seconds ============
    def restart_script(self, r: int = 5):
        self.insert_log(f"Restarting after {r}", "SYSTEM", "orange")
        time.sleep(r)
        subprocess.Popen([sys.executable] + sys.argv)
        os._exit(0)

    # Insert message into the GUI log ================
    def insert_log(self, msg: str, log_type: str, color: str = "black"):
        
        now = datetime.now().strftime("%m/%d %H:%M:%S")
        self.new_listbox.insert(0, f"[{log_type}: {now}] {msg}")
        self.new_listbox.itemconfig(0, {'fg': color})

        with open(os.path.join(BASE_DIR, "logs.txt"), "a", encoding="utf-8") as f:
            f.write(f"\n[{log_type}: {now}] {msg}")

    # Send a Telegram message =============
    def insert_status(self, msg: str, log_type: str):
        text = f"[{log_type}] {msg}"
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {"chat_id": TELEGRAM_account_CHAT_ID, "text": text}
        try:
            with httpx.Client() as client:
                client.get(url=url, params=params)
        except:
            pass

    # Compare new fetched pairs with those in the database =================
    def compare_data(self, db):
        new_pairs, error_type, error_info = self.platform_data.get_all_trading_pairs()

        if self.cash_pairs_ok == False:
            old_pairs = self.platform_data.get_symboles("bitget", db=db)
            self.cash_pairs = old_pairs
            self.cash_pairs_ok = True
        else:
            old_pairs = self.cash_pairs

        if error_type is None:
            return new_pairs - old_pairs
        else:
            self.insert_log(f"TYPE: {error_type}", "ERROR", "red")
            self.insert_log(f"INFO: {error_info}", "ERROR", "red")
            error_text = f"There is an error: `{error_type}` with info `{error_info}` in `compare_data`"
            Thread(target=self.insert_status, args=(error_text, "ERROR")).start()
            self.restart_script()

    def add_piars(self, cursor, symbol):
        # Add a newly detected pair to the database
        pair_info, error_type, error_info = self.platform_data.get_pair_info(symbol)

        if error_type is not None:
            self.insert_log(f"TYPE: {error_type}", "ERROR", "red")
            self.insert_log(f"INFO: {error_info}", "ERROR", "red")
            error_text = f"There is an error: `{error_type}` with info `{error_info}` in `add_piars`"
            Thread(target=self.insert_status, args=(error_text, "ERROR")).start()
            self.restart_script()
        else:
            cursor.execute("INSERT INTO new (symbol, platform, time) VALUES (?, ?, ?)",
                           (str(symbol), "bitget", str(datetime.now().timestamp())))
            cursor.execute("INSERT INTO bitget (symbol, status, baseAsset, quoteAsset, addtime) VALUES (?, ?, ?, ?, ?)",
                           (pair_info["symbol"], pair_info["status"], pair_info["baseCoin"],
                            pair_info["quoteCoin"], str(datetime.now().timestamp())))
            self.insert_log(f"🆕 Added {symbol}", "NOTIFICATION", "green")
            self.cash_pairs_ok = False

    def buy_and_sell_pair(self, symbol:str):
        __ = datetime.now().timestamp()
        symbol_info,____,evv = self.platform_data.get_pair_info(symbol)

        trust = 0
        ranged = datetime.now().timestamp() - __
        ev = 4446464444

        # Get trust ===========================
        while trust < 60 and ranged <= 0.5:
            trust_price,trust,ev = self.platform_data.trust_buy_price(symbol)
            ranged = datetime.now().timestamp() - __

        if ev == None:
            self.insert_log(f"Trust in the pair `{symbol}` is --{trust}%--  ", "USERNOTIF", "black")
            # get symbol info =========================
            print("fine get symbole")
            if evv == None:

                if trust >= 60:
                    # Buy symbol ==========================
                    data_buying,error_buying = self.platform_data.place_order(
                        symbol,
                        "buy",
                        "limit",
                        {"amount":2/trust_price[0],"checkScale":symbol_info["quantityPrecision"]},
                        {"price":trust_price[0],"checkScale":symbol_info["pricePrecision"]},
                        )
                else:
                    Thread(target=self.insert_status, args=(f"Not buyed {symbol} \n Not trusted price", "Error")).start()
                    self.insert_log(f"Not buyed {symbol} --> Not trusted price", "NOTIFICATION", "red")

                
                if error_buying == None:
                    Thread(target=self.insert_status, args=(f"Buyed {symbol} in `{datetime.now().timestamp() - __}` In price {trust_price[0]}", "NOTIFICATION")).start()
                    self.insert_log(f"Buyed {symbol} in {datetime.now().timestamp() - __}", "NOTIFICATION", "green")
                else:
                    Thread(target=self.insert_status, args=(f"Not buyed {symbol} \n {error_buying}", "Error")).start()
                    self.insert_log(f"Not buyed {symbol} --> {error_buying}", "ERROR", "red")
            else:
                Thread(target=self.insert_status, args=(f"Not geted info for {symbol} \n {evv}", "Error")).start()
                self.insert_log(f"Not geted info for {symbol} --> {evv}", "ERROR", "red")
        else:
            Thread(target=self.insert_status, args=(f"Not geted trust for {symbol} \n {ev}", "Error")).start()
            self.insert_log(f"Not geted trust for {symbol} --> {ev}", "ERROR", "red")
        """
        Or you need just do this code ` data_buying,error_buying = self.platform_data.place_order(symbol,"buy","limit",{"amount":xxAmount(USDT)/trust_price[0],"checkScale":4},)` If you dont want to do very data analitics if tour server is slowly
        But this very danger if you don't want to lose your money
        """

    def platform_crypto(self):
        # Main bot logic loop
        time.sleep(1)
        self.insert_log("Start the bot", "SYSTEM")
        self.insert_log(f"Selected Platform: {self.platform}", "USER", "#7AE2CF")
        self.insert_log(f"Account in use: {self.account}", "USER", "#3A59D1")

        db = sqlite3.connect(self.DB_DIR, autocommit=True)
        cursor = db.cursor()

        while True:
            try:
                time_start = datetime.now().timestamp()
                compare_pairs = self.compare_data(db)
                request_in = datetime.now().timestamp() - time_start
                if request_in > 1.5:
                    self.firt_time_run = True

                if compare_pairs:
                    new_pairs = list(compare_pairs)
                    new_pair = new_pairs[0]
                    print(f"new {new_pairs}")


                    if not self.firt_time_run:
                        # If ther is more than pair ==================================================
                        # ============================================================================
                        if len(new_pairs) > 1:
                            self.buy_and_sell_pair(new_pair)
                            text = f"🆕 Detected"
                            for i in new_pairs:
                                self.insert_log(f"🆕 Detected {new_pair}", "NOTIFICATION", "blue")
                                text += f"\n-{i}"
                            Thread(target=self.insert_status, args=(text, "NOTIFICATION")).start()
                            for i in new_pairs:
                                self.add_piars(cursor, i)
                        # If ther is JUST ONE pair ==================================================
                        # ============================================================================
                        else:
                            self.insert_log(f"🆕 Detected {new_pair}", "NOTIFICATION", "blue")
                            self.buy_and_sell_pair(new_pair)
                            text = f"🆕 Detected `{new_pair}`"
                            Thread(target=self.insert_status, args=(text, "NOTIFICATION")).start()
                            self.add_piars(cursor, new_pair)
                    else:
                        for i in new_pairs:
                            self.insert_log(f"🆕 Detected {i}", "NOTIFICATION", "blue")
                            self.add_piars(cursor, i)
                        self.firt_time_run = False
                        
                    text = f"🆕 Detected `{new_pair}`"
                    Thread(target=self.insert_status, args=(text, "NOTIFICATION")).start()

                self.firt_time_run = False
                self.platform_status_speed.config(text=f"Request in: {request_in:.4f}s",
                                                  fg="green" if request_in <= 1 else "orange")
                self.platform_status.config(text="Platform Status: Success", fg="green")

            except Exception as e:
                self.platform_status.config(text="Platform Status: Error", fg="red")
                self.platform_status_speed.config(text="Request in: Error !!", fg="red")
                self.insert_log(f"{e}", "ERROR", "red")
                text = f"There is an error: `{e}` in `infinity loop`"
                Thread(target=self.insert_status, args=(text, "NOTIFICATION")).start()
                self.restart_script()

    def run(self):
        # Start the logic loop and GUI
        local = Thread(target=self.platform_crypto, daemon=True)
        local.start()
        self.root.mainloop()

# ===================================================================
# Example: A Local account config ===================================
class LocalBot(PlatformBot):

    class PlatAccont(BitgetData):
        API_SECRET = str(os.getenv("API_SECREAT"))
        API_KEY = str(os.getenv("API_KEY"))
        PASSPHRASE = str(os.getenv("API_PASS"))

    account = "Local"
    platform = "Bitget"
    platform_data = PlatAccont()
    DB_NAME = "Local.db"

def start_local():
    LocalBot().run()

# ===================================================================
# Entry point ========================================================
if __name__ == "__main__":
    start_local()