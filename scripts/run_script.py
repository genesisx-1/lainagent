#!/usr/bin/env python3
"""Execute a Python script stored in the CRM database"""
import sqlite3
import json
import sys
import os
import subprocess
import tempfile

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'crm.db')

def run_script(script_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM scripts WHERE id=?", (script_id,)).fetchone()
    if not row:
        print(json.dumps({"error": "Script not found"}))
        return

    script = dict(row)
    conn.execute("UPDATE scripts SET status='running', last_run=datetime('now') WHERE id=?", (script_id,))
    conn.commit()

    # Write to temp file and execute
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script['code'])
        tmp_path = f.name

    try:
        result = subprocess.run(
            ['python3', tmp_path],
            capture_output=True, text=True, timeout=60,
            cwd=os.path.dirname(DB_PATH)
        )
        output = result.stdout[:2000]
        if result.returncode != 0:
            output += '\nSTDERR: ' + result.stderr[:500]
            status = 'error'
        else:
            status = 'done'

        conn.execute("UPDATE scripts SET status=?, last_result=? WHERE id=?", (status, output, script_id))
        conn.commit()
        print(json.dumps({"status": status, "output": output}))
    except subprocess.TimeoutExpired:
        conn.execute("UPDATE scripts SET status='timeout', last_result='Timed out after 60s' WHERE id=?", (script_id,))
        conn.commit()
        print(json.dumps({"status": "timeout"}))
    except Exception as e:
        conn.execute("UPDATE scripts SET status='error', last_result=? WHERE id=?", (str(e), script_id))
        conn.commit()
        print(json.dumps({"status": "error", "error": str(e)}))
    finally:
        os.unlink(tmp_path)
        conn.close()

def run_code(code):
    """Run arbitrary Python code directly"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name
    try:
        result = subprocess.run(['python3', tmp_path], capture_output=True, text=True, timeout=60)
        output = result.stdout[:2000]
        if result.returncode != 0:
            output += '\nERROR: ' + result.stderr[:500]
        print(output)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        os.unlink(tmp_path)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: run_script.py <script_id> OR run_script.py --code '<code>'"}))
    elif sys.argv[1] == '--code':
        run_code(' '.join(sys.argv[2:]))
    else:
        run_script(int(sys.argv[1]))
