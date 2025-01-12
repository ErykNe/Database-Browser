import tkinter
from tkinter import ttk
from tkinter import filedialog

import sqlite3


def import_db():
    # Open file dialog and allow the user to select a .db file
    db_path = filedialog.askopenfilename(
        title="Select a .db file",
        filetypes=[("SQLite Database", "*.db")]
    )
    
    if db_path:  
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            conn.close()
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")


m = tkinter.Tk()
m.title("Sqlite test")

sqlite = sqlite3.connect('sql.sql')
kursor = sqlite.cursor()

query = "SELECT * FROM users;"

kursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        age INTEGER
    );
''')

kursor.executemany('''
    INSERT INTO users (username, email, age)
    VALUES (?, ?, ?)
''', [
    ('Alice', 'alice@example.com', 30),
    ('Bob', 'bob@example.com', 25),
    ('Charlie', 'charlie@example.com', 35)
])

kursor.execute(query)
result = kursor.fetchall()

tree = ttk.Treeview(m)

tree['columns'] = ('Name', 'Email', 'Age')

tree.heading('#0', text='Index')
tree.heading('Name', text='Name')
tree.heading('Email', text='Email')
tree.heading('Age', text='Age')


for row in result:
    tree.insert('', 'end', text=row[0], values=row[1:])


tree.pack(expand=True, fill='both')

m.mainloop()
