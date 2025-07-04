import sqlite3
import numpy as np

DB_PATH = 'face_db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        encoding BLOB
    )''')
    conn.commit()
    conn.close()

def insert_face(name, encoding):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    encoding_blob = encoding.tobytes()
    c.execute('INSERT INTO faces (name, encoding) VALUES (?, ?)', (name, encoding_blob))
    conn.commit()
    conn.close()

def get_all_faces():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, encoding FROM faces')
    rows = c.fetchall()
    conn.close()
    faces = [(name, np.frombuffer(encoding, dtype=np.float64)) for name, encoding in rows]
    return faces 