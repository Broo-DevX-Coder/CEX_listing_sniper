import sqlite3
import os 

BASE_DIR = os.path.dirname(__file__)
DB = os.path.join(BASE_DIR,"db.db")

with sqlite3.connect(DB,isolation_level=None) as db:
    cursor = db.cursor()
    cursor.execute(""" CREATE TABLE recovred (
                   time TEXT NOT NULL,
                   pair TEXT NOT NULL)
    """)
    cursor.execute(""" CREATE TABLE pairs (
                   timestamp TEXT NOT NULL,
                   pair TEXT NOT NULL)
    """)