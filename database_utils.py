import sqlite3

def get_connection():
    return sqlite3.connect('contacts_mira.db')

def init_db():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                address TEXT,
                email TEXT UNIQUE,
                phone TEXT UNIQUE
            )
        ''')

def add_contact(fn, ln, addr, email, phone):
    try:
        with get_connection() as conn:
            conn.execute('INSERT INTO contacts (first_name, last_name, address, email, phone) VALUES (?,?,?,?,?)', 
                      (fn, ln, addr, email, phone))
        return True, "Contact saved successfully!"
    except sqlite3.IntegrityError as e:
        if "email" in str(e).lower():
            return False, "Error: This Email ID is already registered."
        return False, "Error: This Phone Number is already registered."

def get_all_contacts():
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row  
        cursor = conn.execute("SELECT * FROM contacts")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

# UPDATED: This now updates ALL fields
def update_contact(cid, fn, ln, addr, email, phone):
    try:
        with get_connection() as conn:
            conn.execute('''UPDATE contacts SET first_name=?, last_name=?, address=?, email=?, phone=? 
                         WHERE id=?''', (fn, ln, addr, email, phone, cid))
        return True, "Update Successful"
    except sqlite3.IntegrityError:
        return False, "Update Failed: Email or Phone already exists."

def delete_contact(cid):
    with get_connection() as conn:
        conn.execute('DELETE FROM contacts WHERE id=?', (cid,))