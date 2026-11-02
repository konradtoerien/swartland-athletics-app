import sqlite3
import pandas as pd
import streamlit as st

# Check for Supabase secrets
SUPABASE_URL = st.secrets.get("SUPABASE_URL", None)
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", None)

if SUPABASE_URL and SUPABASE_KEY:
    from supabase import create_client
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase_client = None

def get_local_connection():
    return sqlite3.connect("athletics.db", check_same_thread=False)

def init_db():
    """Initializes local SQLite database tables if Supabase is not connected."""
    if not supabase_client:
        conn = get_local_connection()
        cursor = conn.cursor()
        
        # Athletes Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS athletes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                school TEXT NOT NULL,
                gender TEXT NOT NULL,
                age_group TEXT NOT NULL,
                events TEXT NOT NULL
            )
        ''')
        
        # Records Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                gender TEXT NOT NULL,
                age_group TEXT NOT NULL,
                record_value REAL NOT NULL,
                holder TEXT NOT NULL,
                year INTEGER NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

init_db()

def insert_athletes(df: pd.DataFrame):
    """Inserts a DataFrame of athletes into the database."""
    if supabase_client:
        records = df.to_dict(orient="records")
        supabase_client.table("athletes").insert(records).execute()
    else:
        conn = get_local_connection()
        df.to_sql("athletes", conn, if_exists="append", index=False)
        conn.close()

def fetch_athletes(filters=None):
    """Fetches athlete records based on optional field filters."""
    if supabase_client:
        query = supabase_client.table("athletes").select("*")
        if filters:
            for k, v in filters.items():
                if v:
                    query = query.eq(k, v)
        res = query.execute()
        return pd.DataFrame(res.data)
    else:
        conn = get_local_connection()
        query = "SELECT * FROM athletes WHERE 1=1"
        params = []
        if filters:
            for k, v in filters.items():
                if v:
                    query += f" AND {k} = ?"
                    params.append(v)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df