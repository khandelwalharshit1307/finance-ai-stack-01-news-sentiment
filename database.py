import sqlite3
import pandas as pd
import json
from datetime import date

DB_PATH = "sentiment.db"

def save_scores(scores: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Main sentiment table
    c.execute("""
        CREATE TABLE IF NOT EXISTS sentiment (
            date TEXT,
            asset_class TEXT,
            score REAL,
            summary TEXT
        )
    """)

    # Headlines table
    c.execute("""
        CREATE TABLE IF NOT EXISTS headlines (
            date TEXT,
            asset_class TEXT,
            top_bullish TEXT,
            top_bearish TEXT
        )
    """)

    today = str(date.today())
    c.execute("DELETE FROM sentiment WHERE date = ?", (today,))
    c.execute("DELETE FROM headlines WHERE date = ?", (today,))

    for asset_class, data in scores.items():
        c.execute(
            "INSERT INTO sentiment VALUES (?,?,?,?)",
            (today, asset_class, data['score'], data['summary'])
        )
        c.execute(
            "INSERT INTO headlines VALUES (?,?,?,?)",
            (
                today,
                asset_class,
                json.dumps(data['top_bullish']),
                json.dumps(data['top_bearish'])
            )
        )

    conn.commit()
    conn.close()

def load_history():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql(
            "SELECT * FROM sentiment ORDER BY date ASC", conn
        )
    except:
        df = pd.DataFrame(
            columns=['date', 'asset_class', 'score', 'summary']
        )
    conn.close()
    return df

def load_headlines(asset_class=None):
    conn = sqlite3.connect(DB_PATH)
    today = str(date.today())
    try:
        if asset_class:
            df = pd.read_sql(
                "SELECT * FROM headlines WHERE date=? AND asset_class=?",
                conn, params=(today, asset_class)
            )
        else:
            df = pd.read_sql(
                "SELECT * FROM headlines WHERE date=?",
                conn, params=(today,)
            )
    except:
        df = pd.DataFrame()
    conn.close()
    return df