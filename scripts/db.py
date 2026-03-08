#!/usr/bin/env python3
"""CRM Database manager - SQLite backend for Agent Office"""
import sqlite3
import json
import sys
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'crm.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            company TEXT,
            role TEXT,
            source TEXT DEFAULT 'manual',
            notes TEXT,
            tags TEXT DEFAULT '[]',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER REFERENCES contacts(id),
            title TEXT NOT NULL,
            status TEXT DEFAULT 'new',
            priority TEXT DEFAULT 'medium',
            value REAL DEFAULT 0,
            source TEXT,
            notes TEXT,
            assigned_agent TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS scrape_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            content TEXT,
            data TEXT DEFAULT '{}',
            status TEXT DEFAULT 'pending',
            agent TEXT DEFAULT 'Gemini',
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS scripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL,
            language TEXT DEFAULT 'python',
            last_run TEXT,
            last_result TEXT,
            status TEXT DEFAULT 'idle',
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS agent_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_agent TEXT NOT NULL,
            to_agent TEXT NOT NULL,
            message TEXT NOT NULL,
            context TEXT DEFAULT '{}',
            read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()

def query(sql, params=(), fetchone=False):
    conn = get_db()
    cur = conn.execute(sql, params)
    if sql.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE')):
        conn.commit()
        result = {'lastrowid': cur.lastrowid, 'rowcount': cur.rowcount}
    elif fetchone:
        row = cur.fetchone()
        result = dict(row) if row else None
    else:
        result = [dict(r) for r in cur.fetchall()]
    conn.close()
    return result

# CLI interface
if __name__ == '__main__':
    init_db()
    if len(sys.argv) < 2:
        print(json.dumps({"status": "ok", "db": DB_PATH}))
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == 'init':
        print(json.dumps({"status": "initialized", "db": DB_PATH}))

    elif cmd == 'add-contact':
        name = sys.argv[2] if len(sys.argv) > 2 else 'Unknown'
        email = sys.argv[3] if len(sys.argv) > 3 else ''
        company = sys.argv[4] if len(sys.argv) > 4 else ''
        r = query("INSERT INTO contacts (name, email, company) VALUES (?, ?, ?)", (name, email, company))
        print(json.dumps({"status": "added", "id": r['lastrowid']}))

    elif cmd == 'list-contacts':
        rows = query("SELECT * FROM contacts ORDER BY created_at DESC LIMIT 50")
        print(json.dumps(rows, default=str))

    elif cmd == 'add-lead':
        title = sys.argv[2] if len(sys.argv) > 2 else 'New Lead'
        source = sys.argv[3] if len(sys.argv) > 3 else ''
        r = query("INSERT INTO leads (title, source) VALUES (?, ?)", (title, source))
        print(json.dumps({"status": "added", "id": r['lastrowid']}))

    elif cmd == 'list-leads':
        rows = query("SELECT * FROM leads ORDER BY created_at DESC LIMIT 50")
        print(json.dumps(rows, default=str))

    elif cmd == 'add-scrape':
        url = sys.argv[2] if len(sys.argv) > 2 else ''
        r = query("INSERT INTO scrape_results (url) VALUES (?)", (url,))
        print(json.dumps({"status": "queued", "id": r['lastrowid']}))

    elif cmd == 'list-scrapes':
        rows = query("SELECT * FROM scrape_results ORDER BY created_at DESC LIMIT 50")
        print(json.dumps(rows, default=str))

    elif cmd == 'send-message':
        from_a = sys.argv[2] if len(sys.argv) > 2 else ''
        to_a = sys.argv[3] if len(sys.argv) > 3 else ''
        msg = sys.argv[4] if len(sys.argv) > 4 else ''
        r = query("INSERT INTO agent_messages (from_agent, to_agent, message) VALUES (?, ?, ?)", (from_a, to_a, msg))
        print(json.dumps({"status": "sent", "id": r['lastrowid']}))

    elif cmd == 'get-messages':
        agent = sys.argv[2] if len(sys.argv) > 2 else ''
        rows = query("SELECT * FROM agent_messages WHERE to_agent=? AND read=0 ORDER BY created_at DESC", (agent,))
        print(json.dumps(rows, default=str))

    elif cmd == 'mark-read':
        msg_id = sys.argv[2] if len(sys.argv) > 2 else '0'
        query("UPDATE agent_messages SET read=1 WHERE id=?", (msg_id,))
        print(json.dumps({"status": "read"}))

    elif cmd == 'stats':
        contacts = query("SELECT COUNT(*) as c FROM contacts", fetchone=True)
        leads = query("SELECT COUNT(*) as c FROM leads", fetchone=True)
        scrapes = query("SELECT COUNT(*) as c FROM scrape_results", fetchone=True)
        messages = query("SELECT COUNT(*) as c FROM agent_messages WHERE read=0", fetchone=True)
        print(json.dumps({"contacts": contacts['c'], "leads": leads['c'], "scrapes": scrapes['c'], "unread_messages": messages['c']}))

    elif cmd == 'query':
        sql = sys.argv[2] if len(sys.argv) > 2 else ''
        try:
            rows = query(sql)
            print(json.dumps(rows, default=str))
        except Exception as e:
            print(json.dumps({"error": str(e)}))

    else:
        print(json.dumps({"error": f"Unknown command: {cmd}"}))
