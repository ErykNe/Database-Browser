import tkinter
from tkinter import ttk
from tkinter import filedialog
from tkinter import Menu

import sqlite3

sqlite = sqlite3.connect('db.db')


def import_db():
    # Open file dialog and allow the user to select a .db file
    db_path = filedialog.askopenfilename(
        title="Select a .db file",
        filetypes=[("SQLite Database", "*.db")]
    )
    
    if db_path:  
        try:
            # Connect to the SQLite database
            sqlite = sqlite3.connect(db_path)
            if(sqlite):
                print("Successfuly connected with database")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")


m = tkinter.Tk()
m.title("Sqlite test")
m.geometry("1000x500")

navbar = Menu(m)
filemenu = Menu(navbar, tearoff=0)
filemenu.add_command(label="Open Database", command=import_db)
navbar.add_cascade(label="File", menu=filemenu)


m.config(menu=navbar)
kursor = sqlite.cursor()


m.mainloop()
