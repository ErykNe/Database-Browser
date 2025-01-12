import os
import tkinter
from tkinter import filedialog, Menu
from tkinter import messagebox
from tkinter import *
from tkinter import ttk
import sqlite3
import xml.etree.ElementTree as ET

sqlite = None  
kursor = None  

def switch_tables(event):
    global combo, sqlite, kursor, label_browse_data
    
    selection = combo.get()
    query = f"SELECT * FROM {selection}"
    
    result = sqlite.execute(query).fetchall()
    columns = [description[1] for description in sqlite.execute(f"PRAGMA table_info({selection})").fetchall()]
    
    print(columns)
    
    children = label_browse_data.winfo_children()
    
    if len(children) > 1:
        a = 0
        for child in children:
            if(a != 0):
                child.destroy()
            a+=1    
    
    h = tkinter.Scrollbar(label_browse_data, orient = 'horizontal')
    h.pack(side = BOTTOM, fill = X)
    v = tkinter.Scrollbar(label_browse_data)
    v.pack(side = RIGHT, fill = Y)

    tree = ttk.Treeview(label_browse_data,
                 xscrollcommand = h.set, 
                 yscrollcommand = v.set)
    
    h.config(command=tree.xview)
  

    v.config(command=tree.yview)
    
    tree["columns"] = columns
    tree["show"] = "headings"
    
    max_lengths = [len(col) for col in columns]  
    
    for row in result:
        for i, value in enumerate(row):
            max_lengths[i] = max(max_lengths[i], len(str(value))) 
    
    for i, col in enumerate(columns):
        tree.heading(col, text=col)
        tree.column(col, width=max(max_lengths[i] * 10, 100), anchor="center")  
    
    for row in result:
        tree.insert('', 'end', values=row)
        
    tree.pack()
    

def switch_view(view):
    global m, nav_db_struct, nav_browse_data, nav_sql, label_sql, label_browse_data
    match(view):
        case "1":
            nav_db_struct.config(bg=m.cget("bg"))
            nav_browse_data.config(bg='lightgray')
            nav_sql.config(bg='lightgray')
            
            label_browse_data.pack_forget()
            label_sql.pack_forget()
        case "2":
            nav_db_struct.config(bg='lightgray')
            nav_browse_data.config(bg=m.cget("bg"))
            nav_sql.config(bg='lightgray')
            label_browse_data.place(x=0)
            label_browse_data.pack(side='left', fill='both')
            label_sql.pack_forget()
        case "3":    
            nav_db_struct.config(bg='lightgray')
            nav_browse_data.config(bg='lightgray')
            nav_sql.config(bg=m.cget("bg"))
            
            label_browse_data.pack_forget()
            label_sql.pack(fill='x', pady=(2, 0))  # 2px margin above the frame
    
def create_db_from_sql(sql_file):
    global sqlite, kursor
    
    try:
        
        if os.path.exists("temp.db"):
            os.remove("temp.db")

        sqlite = sqlite3.connect("temp.db")
        kursor = sqlite.cursor()
        
        with open(sql_file, 'r') as f:
            sql = f.read()
            
        kursor.executescript(sql)
        sqlite.commit()

    except sqlite3.Error as e:
        messagebox.showerror("Error","Error creating database: {e}")
        

def import_db():
    global sqlite, kursor, inputtxt, printButton, combo, m

    db_path = filedialog.askopenfilename(
        title="Select a .db file",
        filetypes=[("SQLite Database", "*.db")]
    )
    
    if db_path:  
        try:
            sqlite = sqlite3.connect(db_path)
            kursor = sqlite.cursor()
            result = kursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [str(table[0]) for table in result.fetchall()]

            combo.set("Select table")
            combo.config(values=tables)
            m.title("SQLite Database Manager - " + str(db_path))
            
            inputtxt.pack()
            printButton.pack()
            combo.place(x=0)
            combo.pack(side='top')
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error connecting to database: {e}")
            import_db()
            
def import_db_from_sql():    
    global sqlite, kursor, inputtxt, printButton, m

    db_path = filedialog.askopenfilename(
        title="Select a .sql file",
        filetypes=[("SQL Database", "*.sql")]
    )
    
    if db_path:  
        try:
            create_db_from_sql(db_path)
            result = kursor.execute("SELECT sql FROM sqlite_master WHERE type='table';") # execute test
            
            print(result.fetchall())
            
            # Show the Text box and Button only if the connection is successful
            m.title("SQLite Database Manager - " + str(db_path))
            inputtxt.pack()
            printButton.pack()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error connecting to database: {e}")
            import_db_from_sql()       

                        
     

def execute_query():
    if sqlite:
        query = inputtxt.get(1.0, "end-1c")  
        try:
            kursor.execute(query)
            sqlite.commit()
            print(kursor.fetchall())
        except sqlite3.Error as e:
             messagebox.showerror("Error", f"Error executing query: {e}")


m = tkinter.Tk()
m.title("SQLite Database Manager")
m.geometry("1000x500")


menuBar = Menu(m)
filemenu = Menu(menuBar, tearoff=0)
filemenu.add_command(label="Open Database", command=import_db)
menuBar.add_cascade(label="File", menu=filemenu)

importmenu = Menu(menuBar, tearoff=0)

database_submenu = Menu(importmenu, tearoff=0)
database_submenu.add_command(label="From SQL File", command=import_db_from_sql)

importmenu.add_cascade(label="Database", menu=database_submenu)

importmenu.add_command(label="Table(s)")
menuBar.add_cascade(label="Import", menu=importmenu)

exportmenu = Menu(menuBar, tearoff=0)
exportmenu.add_command(label="Database")
menuBar.add_cascade(label="Export", menu=exportmenu)

menuBar.add_cascade(label="View")

m.config(menu=menuBar)


navbar = tkinter.Frame(m, bg='lightgray', padx=5, pady=0)
navbar.pack(fill='x', side='top')


nav_db_struct = tkinter.Button(navbar, text="Database structure", borderwidth=0, relief="flat", bg=m.cget("bg"), command=lambda: switch_view("1"))
nav_db_struct.pack(side="left")

nav_browse_data = tkinter.Button(navbar, text="Browse data", borderwidth=0, relief="flat", bg='lightgray', command=lambda: switch_view("2"))
nav_browse_data.pack(side="left")

nav_sql = tkinter.Button(navbar, text="Execute SQL", borderwidth=0, relief="flat", bg='lightgray', command=lambda: switch_view("3"))
nav_sql.pack(side="left")

label_sql = tkinter.Frame(m, padx=5, pady=5)
label_browse_data = tkinter.Frame(m, padx=5, pady=5)
    


inputtxt = tkinter.Text(label_sql, height=5, width=50)
printButton = tkinter.Button(label_sql, text="Enter Query", command=execute_query)

combo = ttk.Combobox(
    label_browse_data,
    state="readonly"
)
combo.bind("<<ComboboxSelected>>", switch_tables)

m.mainloop()
