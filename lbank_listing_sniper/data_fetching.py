from uniquant.Lbank import AsyncClient
import asyncio ,httpx
from dotenv import load_dotenv
from rich.console import Console
from datetime import datetime
import logging , time ,sys ,subprocess , os, sqlite3

console = Console()
BASE_DIR = os.path.dirname(__file__)
load_dotenv(os.path.join(BASE_DIR,".env"))
TLGBOT = os.getenv("telegram_bot_teken")
TLGCHAT = os.getenv("telegram_chat_id")


# logging place ============================================================
logging.basicConfig(
    level=logging.DEBUG,               # Minimum level to log
    filename=os.path.join(BASE_DIR,"logs/","all/",f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.log"),                # File to write logs to
    filemode="w",                      # 'a' (append) or 'w' (overwrite)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S",       # Date/time format
    style='%'                          # Format style (default is '%', can use '{')
)

# INFO only filter ---
class infoOnlyFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO

# The formater of loggers ---
formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Data logger ---
data_logger = logging.getLogger("data_logger")
data_logger.setLevel(logging.DEBUG)
data_handler = logging.FileHandler(os.path.join(BASE_DIR,"logs/","data.log"))
data_handler.setLevel(logging.INFO)
data_handler.addFilter(infoOnlyFilter())
data_logger.addHandler(data_handler)

# Pairs logger ---
pair_logger = logging.getLogger("pair_logger")
pair_logger.setLevel(logging.DEBUG)
pair_handler = logging.FileHandler(os.path.join(BASE_DIR,"logs/","pairs.log"))
pair_handler.setLevel(logging.INFO)
pair_handler.addFilter(infoOnlyFilter())
pair_logger.addHandler(pair_handler)


# system defs =============================================
pairs_cach__ = None
first_time = True

# Restart all program -----
def restart_script(r: int = 5):
        insert_log(f"Restarting after {r}", "SYSTEM", "orange1")
        time.sleep(r)
        subprocess.Popen([sys.executable] + sys.argv)
        os._exit(0)

# Print any thing in console -----
def insert_log(msg: str, log_type: str, color: str = "white"):
        now = datetime.now().strftime("%m/%d %H:%M:%S")
        console.log(f"[{log_type}: {now}] {msg}", style=color)
        logging.info(f"[{log_type}] {msg}")

# send in telegram chanell ------
async def sand_to_tlg(msg: str):
    text = msg
    url = f"https://api.telegram.org/bot{TLGBOT}/sendMessage"
    params = {"chat_id": TLGCHAT, "text": text}
    try:
        async with httpx.AsyncClient() as ac:
            await ac.get(url=url, params=params)
    except Exception as e:
        console.log(f"{e}")

# Program defs ================================================
# Get old pairs from SQL ------
async def from_db(cursor):
    cursor.execute("SELECT * FROM pairs")
    data = cursor.fetchall()
    pairs = [dataf[1] for dataf in data]
    return set(pairs)

# Get the new pairs when deploy ------
async def compire_data(client:AsyncClient,cursor):
    global pairs_cach__
    if pairs_cach__ == None:
        old_pairs = await from_db(cursor)
        pairs_cach__ = old_pairs
    else:
        old_pairs = pairs_cach__
    try:
        curent_pairs = await client.get_all_pairs()
    except Exception as e:
        return e,None
    
    new = curent_pairs - old_pairs
    return None,new

# Add the pair in db ------
async def add_pair(cursor,pair:str):
    cursor.execute("INSERT INTO pairs (timestamp,pair) VALUES (?,?)",(str(datetime.now().timestamp()),pair))

# Fitch data =================================================================
async def wright_in_json(data:str,name:str):
    with open(os.path.join(BASE_DIR,"logs","data",f"{name}.txt"),"w") as file:
        file.write(data)

async def add_in_json(data:str,name:str):
    with open(os.path.join(BASE_DIR,"logs","data",f"{name}.txt"),"a") as file:
        file.write(f"\n{data}")

# ==========================================

# Get data of pair 0.2 S ----------------------
async def get_orderBook_data_02(symbol,client:AsyncClient):
    insert_log(f"Start fetching data for `{symbol}` in 0.2S","SYSTEM")
    await wright_in_json('',f"{symbol}_0.2")

    for i in range(0,10):
        data = await client.order_book(symbol,10)
        ID = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ f":{datetime.now().microsecond // 1000:03d}")
        asyncio.gather(add_in_json(f"[{ID}] {data}",f"{symbol}_0.2"))
        await asyncio.sleep(0.2)

    data_logger.info(f"new data in {symbol}_0.2.txt")

# Get data of pair 0.5 S ----------------------
async def get_orderBook_data_05(symbol,client:AsyncClient):
    insert_log(f"Start fetching data for `{symbol}` in 0.5S","SYSTEM")
    await wright_in_json('',f"{symbol}_0.5")

    for i in range(0,10):
        data = await client.order_book(symbol,10)
        ID = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ f":{datetime.now().microsecond // 1000:03d}")
        asyncio.gather(add_in_json(f"[{ID}] {data}",f"{symbol}_0.5"))
        await asyncio.sleep(0.5)

    data_logger.info(f"new data in {symbol}_0.5.txt")

# Get data of pair 1 S ----------------------
async def get_orderBook_data_1(symbol,client:AsyncClient):
    insert_log(f"Start fetching data for `{symbol}` in 1S","SYSTEM")
    await wright_in_json('',f"{symbol}_1")


    for i in range(0,10):
        data = await client.order_book(symbol,10)
        ID = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ f":{datetime.now().microsecond // 1000:03d}")
        asyncio.gather(add_in_json(f"[{ID}] {data}",f"{symbol}_1"))
        await asyncio.sleep(1)

    data_logger.info(f"new data in {symbol}_1.txt")  

# ===========================================

async def when_new(symbol:str,client:AsyncClient,cursor):
    insert_log(f"A new thread opened for the symbol `{symbol}` ","SYSTEM","bright_blue")
    asyncio.create_task(sand_to_tlg(f"A new pir:{symbol}"))
    pair_logger.info(f"New symbol > {symbol}_1")

    lenn = 0
    while lenn == 0:
        resp:dict = await client.order_book(symbol,10)
        data:dict = resp.get("data",{})
        asks:list = data.get("asks",[])
        lenn = len(asks)
    else:
        insert_log(f"The task of `{symbol}` finished","SYSTEM","bright_blue")
        await asyncio.gather(get_orderBook_data_02(symbol,client),get_orderBook_data_05(symbol,client),get_orderBook_data_1(symbol,client))
        await asyncio.gather(__in_recovred("del",symbol,cursor))

async def restart_wen_new(symbols:list,client:AsyncClient,cursor):
    insert_log(f"Start recover the unrecovred symbols","SYSTEM","bright_blue")
    for i in symbols:
        await asyncio.create_task(when_new(i,client,cursor))

async def __in_recovred(type__:str,symbol:str,cursor):
    if type__ == "add": 
        cursor.execute("INSERT INTO recovred (time,pair) VALUES (?,?)",(str(datetime.now()),symbol))
    elif type__ == "del":
        cursor.execute("DELETE FROM recovred WHERE pair=?",(symbol,))


# This is the main of all program ======================================================
async def main():
    global first_time,pairs_cach__
    insert_log("Start the bot", "SYSTEM")
    with console.status("[bold yellow]Running...") as status:
        with sqlite3.connect(os.path.join(BASE_DIR,"db.db"),isolation_level=None) as db:
            cursor = db.cursor()
            async with AsyncClient(os.getenv("API_key"),os.getenv("secret_key")) as client:
                try:
                    cursor.execute("SELECT * FROM recovred")
                    recovred = [p[1] for p in cursor.fetchall()]
                    if len(recovred) != 0:
                        restart_wen_new(recovred,client,cursor)
                    while True:
                        __start = datetime.now().timestamp()
                        e,compire_pairs = await compire_data(client,cursor)
                        __end = datetime.now().timestamp() - __start

                        if __end > 3000:
                            first_time = True

                        if e == None:
                            if compire_pairs:
                                if first_time == True:
                                    cmp = list(compire_pairs)
                                    for i in cmp:
                                        insert_log(f"Added new symbol > {i}","NOTIF","blue")
                                        await add_pair(cursor,i)
                                    pairs_cach__ = None
                                    
                                else:
                                    cmp = list(compire_pairs)
                                    insert_log(f"New pair detected > {cmp[0]}","NOTIF","blue")
                                    asyncio.create_task(when_new(cmp[0],client,cursor))
                                    await asyncio.gather(__in_recovred("add",cmp[0],cursor))
                                    for i in cmp:
                                        await add_pair(cursor,i)
                                    pairs_cach__ = None

                        else:
                            insert_log(f"Error from compire_data > {e}","ERROR","red")
                            restart_script()

                        first_time = False

                        status.update(f"[green]Request in: {round(__end,3)*1000}ms | Status: Success")
                except Exception as ee:
                    insert_log(f"{ee}", "ERROR", "red")
                

try:
    asyncio.run(main())
except KeyboardInterrupt:
    insert_log("Finall of program !!", "SYSTEM", "orange1")