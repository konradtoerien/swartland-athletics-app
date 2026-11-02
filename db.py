import sqlite3
import pandas as pd
import streamlit as st

SUPABASE_URL = None
SUPABASE_KEY = None

try:
    if "SUPABASE_URL" in st.secrets:
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
    if "SUPABASE_KEY" in st.secrets:
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    pass

if SUPABASE_URL and SUPABASE_KEY:
    from supabase import create_client
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase_client = None

def get_local_connection():
    return sqlite3.connect("athletics.db", check_same_thread=False)

def init_db():
    if not supabase_client:
        conn = get_local_connection()
        cursor = conn.cursor()
        
        # Tabel vir Atlete
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
        
        # Tabel vir Rekords
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                gender TEXT NOT NULL,
                age_group TEXT NOT NULL,
                record_value TEXT NOT NULL,
                holder TEXT NOT NULL,
                year INTEGER NOT NULL
            )
        ''')
        
        # Tabel vir Uitslae
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                gender TEXT NOT NULL,
                age_group TEXT NOT NULL,
                place INTEGER,
                athlete_id INTEGER,
                athlete_name TEXT,
                school TEXT,
                result_value TEXT,
                asa_points INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel vir Program / Tydrooster
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_program (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_no INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                age_group TEXT NOT NULL,
                gender TEXT NOT NULL,
                event_name TEXT NOT NULL,
                venue TEXT NOT NULL,
                status TEXT DEFAULT 'Wagtend'
            )
        ''')
        
        # Auto-migration: Maak seker 'place' kolom bestaan
        cursor.execute("PRAGMA table_info(event_results)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'place' not in columns:
            cursor.execute("ALTER TABLE event_results ADD COLUMN place INTEGER")

        conn.commit()
        conn.close()

init_db()

# ==================== ATLETE ====================
def insert_athletes(df: pd.DataFrame):
    if supabase_client:
        records = df.to_dict(orient="records")
        supabase_client.table("athletes").insert(records).execute()
    else:
        conn = get_local_connection()
        df.to_sql("athletes", conn, if_exists="append", index=False)
        conn.close()

def fetch_athletes(filters=None):
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

# ==================== REKORDS ====================
def insert_records(df: pd.DataFrame):
    conn = get_local_connection()
    df.to_sql("event_records", conn, if_exists="append", index=False)
    conn.close()

def fetch_all_records():
    conn = get_local_connection()
    df = pd.read_sql_query("SELECT * FROM event_records", conn)
    conn.close()
    return df

def delete_record(record_id: int):
    conn = get_local_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM event_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

def fetch_event_record(event_name, gender, age_group):
    conn = get_local_connection()
    query = "SELECT * FROM event_records WHERE event_name = ? AND gender = ? AND age_group = ?"
    df = pd.read_sql_query(query, conn, params=[event_name, gender, age_group])
    conn.close()
    return df.iloc[0].to_dict() if not df.empty else None

# ==================== UITSLAE ====================
def save_event_results(event_name, gender, age_group, results_list):
    conn = get_local_connection()
    cursor = conn.cursor()
    for r in results_list:
        cursor.execute('''
            INSERT INTO event_results (event_name, gender, age_group, place, athlete_id, athlete_name, school, result_value, asa_points)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (event_name, gender, age_group, r.get("place", 0), r["athlete_id"], r["name"], r["school"], r["result_value"], r["asa_points"]))
    conn.commit()
    conn.close()

def fetch_event_results(event_name, gender, age_group):
    conn = get_local_connection()
    query = "SELECT place as Plek, athlete_name as 'Atleet Naam', school as Skool, result_value as Uitslag, asa_points as 'ASA Punte' FROM event_results WHERE event_name = ? AND gender = ? AND age_group = ? ORDER BY place ASC"
    df = pd.read_sql_query(query, conn, params=[event_name, gender, age_group])
    conn.close()
    return df

def fetch_all_results():
    conn = get_local_connection()
    df = pd.read_sql_query("SELECT * FROM event_results ORDER BY timestamp DESC", conn)
    conn.close()
    return df

# ==================== RESET ====================
def reset_database():
    conn = get_local_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM athletes")
    cursor.execute("DELETE FROM event_results")
    cursor.execute("DELETE FROM event_records")
    cursor.execute("DELETE FROM event_program")
    conn.commit()
    conn.close()
