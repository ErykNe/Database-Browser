import tkinter
from tkinter import ttk

import sqlite3

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
