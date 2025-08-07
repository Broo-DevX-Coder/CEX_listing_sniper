# 🧠 Overview of Trading Bots
- Projuct status: __finished__

We present **three automated trading bot projects**, each tailored for real-time monitoring and trading on cryptocurrency exchanges. These bots are designed to detect newly listed trading pairs, evaluate market conditions, and optionally execute trades — ideal for early detection and fast execution strategies.

**Disclaimer**
> This project is intended strictly for educational and research purposes only.
Any use of this code for illegal activities — including but not limited to sniping questionable tokens, participating in pump-and-dump schemes, or any activity forbidden under Islamic law (Shariah) — is strictly prohibited.
The author of this project bears no responsibility for any misuse, and users are solely accountable for ensuring compliance with all applicable laws, regulations, and ethical standards.

---

## 1. **LBank Pair Sniper Bot (AsyncClient-Based)**  
*Monitoring Exchange: LBank | Language: Python*

This asynchronous bot detects **newly listed trading pairs on the LBank exchange**. When a new pair appears, it:
- Sends alerts via **Telegram**
- Captures live **order book data** at multiple intervals (0.2s, 0.5s, 1s)
- Stores data into structured logs and an **SQLite database**
- Automatically recovers from restarts
- Optionally supports placing **market buy orders**

Built using `uniquant.Lbank.AsyncClient`, this project ensures low-latency response times and robust error handling. It’s perfect for traders aiming to be among the first to enter newly launched tokens.

---

## 2. **Bitget Spot Pair Sniper Bot (with GUI)**  
*Monitoring Exchange: Bitget | Language: Python | Interface: Desktop GUI*

A **desktop-based trading bot with a live graphical interface**, this tool:
- Monitors **new USDT trading pairs** on Bitget
- Evaluates **price trust score** using order book depth
- Can automatically place **limit buy orders** if trust level exceeds a threshold
- Displays status updates and logs in real time via **Tkinter GUI**
- Logs events and sends **Telegram notifications**
- Recovers gracefully after errors or crashes

This bot is ideal for users who want visual feedback while automating early detection and basic trading strategies.

---

## 3. **Bitget Console Trading Bot**  
*Monitoring Exchange: Bitget | Language: Python | Interface: CLI*

A **console-based automation script** that:
- Fetches live trading pairs from Bitget
- Analyzes **price reliability and order book depth**
- Automatically places **buy/sell orders** based on confidence levels
- Logs all activities and sends messages to **Telegram**
- Uses **SQLite** for tracking known trading pairs
- Supports optional integration with cron jobs or daemon processes

This lightweight yet powerful bot is great for headless operation and background monitoring of market opportunities.

---

## 🔐 Security & Best Practices

All projects use environment variables (`.env`) to securely store API keys and Telegram credentials. They also support logging, restart mechanisms, and SQLite-based persistence to ensure continuity across sessions.

---

## 🚀 Who Should Use These Bots?

- **Traders**: Looking to catch newly listed tokens before price spikes.
- **Developers**: Interested in building upon open-source trading logic and exchange integrations.
- **Quantitative Analysts**: Needing raw market data from order books for analysis.
- **Crypto Enthusiasts**: Wanting to automate their trading workflows.

---

## 🛠️ Technologies Used

- Python 3.8+
- Async (`asyncio`, `httpx`) and sync HTTP clients
- Cryptographic libraries (`hmac`, `hashlib`)
- Telegram Bot API integration
- SQLite for local storage
- Tkinter (for GUI version)

---

## 📌 Future Enhancements Across Projects

- Add **sell strategies** and **stop-loss/take-profit** logic
- Integrate **CSV export** or visualization tools
- Support **multi-exchange** monitoring
- Implement **web dashboards** and alert systems

---
---

# 📘 LBank Pair Sniper Bot – Documentation

## 🧠 Overview

This bot continuously monitors new trading pairs on the **LBank** exchange using the `AsyncClient` from the `uniquant.Lbank` library. When a new pair is detected, the bot:

* Sends a notification to a Telegram channel.
* Starts collecting live order book data for the pair.
* Saves all collected data into structured logs.
* Manages discovered pairs using SQLite.
* Automatically recovers unprocessed pairs after restarts.

## 📁 Project Structure

```
project/
│
├── main.py                  # Main bot script
├── .env                     # Environment variables (API keys, Telegram config)
├── db.db                    # SQLite database storing discovered & recovered pairs
├── logs/
│   ├── all/                 # Main runtime logs
│   ├── data.log             # Logs of saved market data
│   ├── pairs.log            # Logs of discovered pairs
│   └── data/                # Order book snapshots per symbol
└── requirements.txt         # Dependencies list
```

## 🔐 Environment Variables (.env)

```ini
API_key=your_lbank_api_key
secret_key=your_lbank_secret_key
telegram_bot_teken=your_telegram_bot_token
telegram_chat_id=your_telegram_chat_id
```

## 🧩 Components Breakdown

### ✅ `insert_log(msg, log_type, color)`

Prints colored logs to the console and saves to file.

### ✅ `sand_to_tlg(msg)`

Asynchronously sends a message to your Telegram channel.

### ✅ `from_db(cursor)`

Reads existing pairs from the database to avoid duplicates.

### ✅ `compire_data(client, cursor)`

Fetches current pairs from the API, compares with stored ones, and returns new ones.

### ✅ `when_new(symbol, client, cursor)`

Handles a newly discovered trading pair:

* Sends a Telegram notification.
* Collects market data for 0.2s, 0.5s, and 1s intervals.
* Logs and saves it.

### ✅ Data Collection Functions

* `get_orderBook_data_02`
* `get_orderBook_data_05`
* `get_orderBook_data_1`

Each collects 10 snapshots of the order book at different intervals and writes to log files.

### ✅ Database Functions

* `add_pair(cursor, pair)` → Adds a new pair to the database.
* `__in_recovred(type, symbol, cursor)` → Manages the `recovred` table to track unfinished pairs.

### ✅ `restart_script(seconds)`

Restarts the Python script with a delay (used for self-recovery in case of critical errors).

## 🧪 Main Execution Flow: `main()`

1. Connects to SQLite and initializes API client.
2. Loads any unprocessed pairs (`recovred`) and starts them.
3. In a loop:

   * Compares current pairs with DB.
   * On discovery:

     * Logs & stores the pair.
     * Starts async tasks to gather its data.
   * On error:

     * Logs and restarts the bot.

## 💡 Features

* 🔁 Auto restart on failure.
* 🧠 Intelligent recovery of unfinished work.
* 💾 Raw order book snapshots stored for analysis.
* 📬 Telegram alerts.
* 📚 SQLite-based storage.

## 📦 Requirements (`requirements.txt`)

```txt
httpx
python-dotenv
rich
```

## 🧱 Database Schema

### Table: `pairs`

| Column    | Type | Description                |
| --------- | ---- | -------------------------- |
| timestamp | TEXT | UNIX timestamp of insert   |
| pair      | TEXT | Symbol of the trading pair |

### Table: `recovred`

| Column | Type | Description             |
| ------ | ---- | ----------------------- |
| time   | TEXT | Time of detection       |
| pair   | TEXT | Symbol pending recovery |

## 🧪 Example: Add a Pair

```python
await add_pair(cursor, "LTC_USDT")
```

## 🛠️ TODO Ideas

* Add buying logic using `client.buy_market(...)`
* Add data visualizations or export to CSV
* Add filtering rules (e.g., only USDT pairs)
* Improve error handling granularity

Would you like me to generate this as a downloadable `README.md` file?

---

# 📘 **Project: LBank Pair Sniper Bot (AsyncClient-Based)**

### 🧠 **Purpose:**

This bot continuously monitors new trading pairs listed on the LBank exchange. When a new pair appears, it can optionally place a market buy order using `buy_market`, logs the activity, updates a local SQLite database, and sends alerts to a Telegram channel.

## 📦 **Modules & Dependencies:**

* `uniquant.Lbank.AsyncClient`: Custom LBank API wrapper (assumed).
* `httpx`: Async HTTP client.
* `dotenv`: Loads environment variables from `.env` file.
* `sqlite3`: Used for local persistent storage.
* `rich`: For console logging and styled outputs.
* `logging`: Tracks system and bot events.
* `os`, `sys`, `time`, `subprocess`: System-level utilities.

## 🔐 **.env Requirements:**

The bot expects the following environment variables:

```ini
API_key=your_lbank_api_key
secret_key=your_lbank_secret_key
telegram_bot_teken=your_telegram_bot_token
telegram_chat_id=your_chat_id
```

## 🗃️ **Database Tables:**

### `pairs`

| Column    | Type   | Description            |
| --------- | ------ | ---------------------- |
| timestamp | float  | When the pair was seen |
| pair      | string | Trading pair symbol    |

### `recovred`

| Column | Type   | Description            |
| ------ | ------ | ---------------------- |
| time   | string | Timestamp for recovery |
| pair   | string | Pair being processed   |

## 🧠 **Core Features & Functions:**

### 🔄 `compire_data(client, cursor)`

Fetches the current LBank trading pairs and compares them to what's stored in the DB to find new ones.

### 💾 `add_pair(cursor, pair)`

Inserts a newly discovered pair into the database.

### 🛒 `buy(symbol, client, info, asks)`

Places a `buy_market` order on the specified pair based on the current best ask and quantity limits.

> ⚠️ The `value` sent to `buy_market` is in **quote currency (e.g., USDT)**. It represents how much USDT to spend.

### 📦 `from_db(cursor)`

Retrieves all known trading pairs from the database.

### 🧠 `when_new(symbol, client, cursor)`

Runs logic when a new pair is detected: fetch order book, check validity, and optionally buy it.

### 🔁 `restart_script()`

Restarts the entire script (e.g., on error or by logic trigger).

### 📤 `sand_to_tlg(msg)`

Sends messages to a Telegram chat using the Bot API.

### 🔁 `restart_wen_new(...)`

Re-processes previously interrupted (unrecovered) pairs.

## 🧪 **Main Loop Logic (`main`)**

1. Loads previously unprocessed pairs from DB.
2. Continuously compares current pairs from LBank to DB.
3. If a new pair is found:

   * Logs the discovery.
   * Optionally processes it using `when_new(...)`.
   * Saves it to DB.
4. Sends notifications to Telegram.
5. If an error occurs → log + restart script.


## 📂 **Log Structure:**

Logs are saved to:

```
/logs/all/YYYY-MM-DD HH:MM:SS.log
/logs/pairs.log
/logs/data/  ← for optional JSON/text dumps
```

## ✅ **How to Run:**

1. Create `.env` with correct keys.
2. Make sure DB file (`db.db`) and required tables exist.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
4. Run the script:

   ```bash
   python bot.py
   ```

## 🛠️ **To Do / Improve:**

* [ ] Add retries for failed API calls instead of immediate restart.
* [ ] Add timeout handling for async tasks.
* [ ] Better input sanitization and pair validation.
* [ ] Migrate to `aiosqlite` for full async DB access.


Here’s a polished, English-written **mini documentation** for your Bitget-based trading bot script:

---

# 📘 Project: Bitget Spot Pair Sniper Bot (with GUI)

### 🧠 Purpose

A desktop-based bot that monitors newly listed USDT trading pairs on Bitget, evaluates them using order book metrics, optionally places limit buy orders, logs activity, and sends Telegram alerts—all while displaying a live GUI.

## 📦 Dependencies

```text
requests
httpx
python-dotenv
rich        # If used (optional, not shown in current version)
tkinter     # for the GUI (standard library, may require system install)
```

Additional built-ins: `os`, `sys`, `time`, `hmac`, `hashlib`, `base64`, `json`, `sqlite3`, `threading`, `datetime`, `subprocess`, `math`.

## 🔐 Environment Variables (via `.env`)

```ini
API_KEY=...
API_SECRET=...
API_PASS=...
telegram_bot_token=...
telegram_chat_id=...
```

## 🧩 Main Classes & Their Responsibilities

### `BitgetData`

* Initializes a `requests.Session` with connection pooling.

* **Symbol Fetching**:

  * `fetch_symbol_data()`: Retrieves all trading symbols.
  * `get_all_trading_pairs()`: Filters online USDT pairs.
  * `get_pair_info(symbol)`: Retrieves details for a specific symbol.
  * `get_symboles(table_name, db)`: Fetches previously stored symbols from SQLite.

* **Order & Signature Handling**:

  * `generate_signature(timestamp, method, path, body)`: HMAC SHA256-based authentication.
  * `place_order(symbol, side, order_type, quantity, price=None)`: Places limit or market orders.

* **Account Info**:

  * `get_balance()`: Retrieves account balances.
  * `get_current_price(symbol)`: Fetches the latest ticker price.
  * `trust_buy_price(symbol)`: Computes a weighted average ask, bid-ask spread, and evaluates "trust" score based on order depth.

### `PlatformBot`

Configurable GUI-powered controller for managing monitoring and trading logic.

* **GUI & Logging**:

  * Uses `tkinter` to show status labels and a `Listbox` log window.
  * `insert_log(msg, log_type, color)`: Appends logs to GUI and `logs.txt`.
  * `insert_status(msg, log_type)`: Sends a Telegram notification asynchronously.

* **Bot Workflow**:

  1. **compare\_data(db)**: Retrieves new pairs compared to the saved DB state.
  2. **add\_piars(cursor, symbol)**: Inserts new pairs into `new` and `bitget` tables in the DB.
  3. **buy\_and\_sell\_pair(symbol)**:

     * Checks trust score via `trust_buy_price`.
     * If trust ≥ 60 within 0.5 seconds, places a limit buy order.
     * Notifies via GUI and Telegram whether the order succeeded.
  4. **platform\_crypto()**: Main loop that:

     * Calls `compare_data()`.
     * Handles first-run logic and batch vs single pair detection.
     * Updates GUI status and processing time.
     * Catches errors and triggers restart.

* **restart\_script(r)**: Restarts the script after a pause.

* **run()**: Starts the bot logic in a background thread and launches the GUI.

### `LocalBot(PlatformBot)`

Concrete implementation with credentials from `.env`.

```python
class LocalBot(PlatformBot):
    class PlatAccont(BitgetData):
        API_SECRET = os.getenv("API_SECREAT")
        API_KEY = os.getenv("API_KEY")
        PASSPHRASE = os.getenv("API_PASS")
    account = "Local"
    platform = "Bitget"
    platform_data = PlatAccont()
    DB_NAME = "Local.db"

# Entry point
if __name__ == "__main__":
    LocalBot().run()
```

## 🛠 Setup and Usage

1. Install dependencies:

   ```bash
   pip install requests httpx python-dotenv
   sudo apt install python3-tk  # if tkinter is missing on Linux
   ```

2. Prepare `.env` with required API credentials and Telegram keys.

3. Make sure the SQLite DB file (`Local.db`) and tables (`bitget`, `new`, etc.) exist.

4. Run the bot:

   ```bash
   python bitget_bot.py
   ```

## ✅ Suggestions & Future Enhancements

* Ensure DB schema is defined before runtime.
* Add retries, backoff, and exception handling in HTTP calls.
* Tune trust threshold, depth logic, and timing.
* Clean up threads during graceful shutdown.
* Refactor global Telegram credentials for clarity.
* Consider migrating to full async (`httpx.AsyncClient`, `aiosqlite`) for non-blocking IO.

---

# Bitget Console Trading Bot Documentation

## Overview

This is a console-based automated trading bot built in Python. It fetches cryptocurrency trading pairs from the Bitget exchange, analyzes trust levels of prices, and automatically places buy/sell orders. It also logs events and sends status messages to a Telegram bot.

## 1. Requirements

* Python 3.8+
* Libraries: `requests`, `httpx`, `rich`, `dotenv`, `sqlite3`, `subprocess`, `hmac`, `hashlib`, `json`, `base64`, `math`, `datetime`, `threading`
* Telegram Bot Token and Chat ID
* `.env` file in project root

## 2. Installation

Before running the bot, make sure to install the required Python libraries. Use the following command:

```bash
pip install requests httpx rich python-dotenv
```

> Note: Some modules such as `sqlite3`, `subprocess`, `hmac`, `hashlib`, etc., are part of the Python Standard Library and do not require installation.

Ensure your file structure looks like this:

```
project_root/
├── desktop_app/
| ├──index.py
| ├──.env
| ├──Local.db
| ├──logs.txt
├── console_app/
| ├──index.py
| ├──.env
| ├──Local.db
| ├──logs.txt
```

## 3. Environment Setup

Create a `.env` file:

```
API_KEY=your_bitget_api_key
API_SECRET=your_bitget_secret
PASSPHRASE=your_bitget_passphrase
```

## 4. Components

### 4.1 `BitgetData` class

Handles all API interactions with Bitget.

#### Methods:

* `fetch_symbol_data()`

  * Returns all available trading pairs

* `get_all_trading_pairs()`

  * Returns only USDT-based and online trading pairs

* `get_pair_info(symbol)`

  * Fetch info for specific trading pair

* `get_symboles(table_name, db)`

  * Return saved symbols from DB

* `generate_signature(...)`

  * Create signature for authenticated API requests

* `place_order(symbol, side, type, quantity, price)`

  * Execute buy/sell order

* `get_balance()`

  * Returns all assets and available balances

* `get_current_price(symbol)`

  * Returns the last market price for a pair

* `trust_buy_price(symbol)`

  * Returns weighted price, best price, and trust percentage

### 4.2 `PlatformBot` class

Handles bot logic, logging, DB interaction, price analysis, and Telegram notifications.

#### Main Attributes:

* `platform_data`: Instance of `BitgetData`
* `DB_NAME`: SQLite DB path

#### Methods:

* `restart_script(r)`

  * Restarts bot after `r` seconds

* `insert_log(msg, type, color)`

  * Log message to console and file

* `insert_status(msg, type)`

  * Send Telegram message

* `compare_data(db)`

  * Compare new symbols with DB and return new ones

* `add_piars(cursor, symbol)`

  * Insert new trading pair into DB

* `buy_and_sell_pair(symbol)`

  * Trust analysis, buying if conditions are met

## 5. Usage Flow

1. Initialize the bot with DB and API keys.
2. Fetch symbols from API.
3. Compare with local DB.
4. Analyze trust score.
5. Place buy order if trust is high.
6. Log and notify via Telegram.

## 6. Notes

* Low trust levels may cause the bot to avoid trades.
* You can run the bot as a daemon or cron job.
* Errors are logged and trigger a restart.

## 7. Security

* Keep `.env` file secure and do not expose API keys.
* Make sure you do proper error handling in production.

## 8. Future Improvements

* Add sell-side strategy
* Add stop-loss and take-profit
* Add UI or Dashboard
* Add multi-account support

## 9. References

* [Bitget Spot API Docs](https://www.bitget.com/api-doc/spot/)
* [Telegram Bot API](https://core.telegram.org/bots/api)
