import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "links.db")


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS links (
            discord_id TEXT PRIMARY KEY,
            roblox_id TEXT NOT NULL,
            roblox_username TEXT,
            linked_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # pending state table to tie an OAuth callback back to the Discord user who started it
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pending_states (
            state TEXT PRIMARY KEY,
            discord_id TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_link(discord_id: str, roblox_id: str, roblox_username: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO links (discord_id, roblox_id, roblox_username)
        VALUES (?, ?, ?)
        ON CONFLICT(discord_id) DO UPDATE SET
            roblox_id=excluded.roblox_id,
            roblox_username=excluded.roblox_username
    """, (discord_id, roblox_id, roblox_username))
    conn.commit()
    conn.close()


def get_link(discord_id: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT roblox_id, roblox_username FROM links WHERE discord_id = ?", (discord_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"roblox_id": row[0], "roblox_username": row[1]}
    return None


def save_pending_state(state: str, discord_id: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO pending_states (state, discord_id) VALUES (?, ?)", (state, discord_id))
    conn.commit()
    conn.close()


def pop_pending_state(state: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT discord_id FROM pending_states WHERE state = ?", (state,))
    row = cur.fetchone()
    if row:
        cur.execute("DELETE FROM pending_states WHERE state = ?", (state,))
        conn.commit()
    conn.close()
    return row[0] if row else None