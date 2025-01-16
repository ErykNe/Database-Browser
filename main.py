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


def get_database_structure():
    global sqlite, kursor, label_db_struct
    
    children = label_db_struct.winfo_children()
    if len(children) > 2:
        children[2].destroy() 
    
    tree = ttk.Treeview(label_db_struct, xscrollcommand = h2.set, yscrollcommand = v2.set)
    
    tree.pack(expand=True, fill="both")
    columns = ["Type", "Schema"]
    
    tree["columns"] = columns
    tree.heading("#0", text="Name", anchor='w')
    tree.heading("Type", text="Type", anchor='w')
    tree.heading("Schema", text="Schema", anchor='w')
    
    
    longest_schema_length = 0

    
    tree.tag_configure("underline", font=("", 9, "underline"))
    
    
    table_node = tree.insert("", "end", text="Tables", open=True)

    query_table_names = "SELECT name, type, sql FROM sqlite_master WHERE type='table'"
    tables = sqlite.execute(query_table_names).fetchall()
    
    
    for table in tables:
        name = str(table[0])
        schema = str(table[2]).replace("\n", " ")
        
        if(longest_schema_length < len(schema)):
            longest_schema_length = len(schema)
        
        child_1 = tree.insert(table_node, "end", text=name, open=False, values=("", schema))
        query_pragma = f"PRAGMA table_info({name});"
        table_struct = sqlite.execute(query_pragma).fetchall()
        for struct in table_struct:
            result = f'"{struct[1]}" {struct[2]} {"NOT NULL " if struct[3] == 1 else ""} {"PRIMARY KEY" if struct[5] == 1 else ""}'
            child_2 = tree.insert(child_1, "end", text=str(struct[1]), values=(str(struct[2]), result))
            
            if struct[5] == 1:
                tree.item(child_2, tags=("underline",))
            
    view_node = tree.insert("", "end", text="Views", open=True)
    
    query_view_names = "SELECT name, type, sql FROM sqlite_master WHERE type='view'"
    views = sqlite.execute(query_view_names).fetchall()
    
    for view in views:
        name = str(view[0])
        schema = str(view[2]).replace("\n", " ")
        
        if(longest_schema_length < len(schema)):
            longest_schema_length = len(schema)
            
        child_1 = tree.insert(view_node, "end", text=name, open=False, values=("", schema))
        query_pragma = f"PRAGMA table_info({name});"
        table_struct = sqlite.execute(query_pragma).fetchall()
        for struct in table_struct:
            result = f'"{struct[1]}" {struct[2]} {"NOT NULL " if struct[3] == 1 else ""} {"PRIMARY KEY" if struct[5] == 1 else ""}'
            tree.insert(child_1, "end", text=str(struct[1]), values=(str(struct[2]), result))
    
    trigger_node = tree.insert("", "end", text="Triggers", open=True)
    
    query_triggers_names = "SELECT name, type, sql FROM sqlite_master WHERE type='trigger'"
    triggers = sqlite.execute(query_triggers_names).fetchall()   
    
    for trigger in triggers:
        name = str(trigger[0])
        schema = str(trigger[2]).replace("\n", " ")
        
        if(longest_schema_length < len(schema)):
            longest_schema_length = len(schema)
            
            
        child_1 = tree.insert(trigger_node, "end", text=name, open=False, values=("", schema))
          
    tree.column("#0", width=max((int(m.winfo_width()/3)), 100), stretch=False)      
    tree.column(columns[0], width=max((int(m.winfo_width()/3)), 100), stretch=False)      
    tree.column(columns[1], width=max((longest_schema_length * 6), 100), anchor='w', stretch=False)      
    
    h2.config(command=tree.xview)
    v2.config(command=tree.yview)    
    
    def on_right_click(event):
        selected_item = tree.identify('item', event.x, event.y)
        if selected_item == table_node:
            tree.selection_set(selected_item)
            menu = tkinter.Menu(m, tearoff=0)
            menu.add_command(label="Add Table")
            menu.post(event.x_root, event.y_root)
        if selected_item == view_node:
            tree.selection_set(selected_item)
            menu = tkinter.Menu(m, tearoff=0)
            menu.add_command(label="Add View")
            menu.post(event.x_root, event.y_root)   
        if selected_item == trigger_node:
            tree.selection_set(selected_item)
            menu = tkinter.Menu(m, tearoff=0)
            menu.add_command(label="Add Trigger")
            menu.post(event.x_root, event.y_root)      
    
    tree.bind("<Button-3>", on_right_click)
    
            
        

def switch_tables(event):
    global combo, sqlite, kursor, label_browse_data, label_treedata
    
    selection = combo.get()
    query = f"SELECT * FROM {selection}"
    
    result = sqlite.execute(query).fetchall()
    columns = [description[1] for description in sqlite.execute(f"PRAGMA table_info({selection})").fetchall()]
    
    print(columns)
    
    children = label_treedata.winfo_children()
    if len(children) > 2:
        children[2].destroy() 
    

    tree = ttk.Treeview(label_treedata,
                 xscrollcommand = h1.set, 
                 yscrollcommand = v1.set)
    
    h1.config(command=tree.xview)
    v1.config(command=tree.yview)
    
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
        
    tree.pack(padx=0, pady=0, anchor='w')

    

def switch_view(view):
    global m, nav_db_struct, nav_browse_data, nav_sql, label_sql, label_browse_data, label_db_struct
    match(view):
        case "1":
            nav_db_struct.config(bg=m.cget("bg"))
            nav_browse_data.config(bg='lightgray')
            nav_sql.config(bg='lightgray')
            
            label_db_struct.pack(side='left', fill='both', expand=True)
            label_browse_data.pack_forget()
            label_sql.pack_forget()
        case "2":
            nav_db_struct.config(bg='lightgray')
            nav_browse_data.config(bg=m.cget("bg"))
            nav_sql.config(bg='lightgray')

            label_db_struct.pack_forget()
            label_browse_data.pack(side='left', fill='both', expand=True)
            label_sql.pack_forget()
        case "3":    
            nav_db_struct.config(bg='lightgray')
            nav_browse_data.config(bg='lightgray')
            nav_sql.config(bg=m.cget("bg"))
            
            label_db_struct.pack_forget()
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
    global sqlite, kursor, inputtxt, printButton, combo, m, label_treedata

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
            combo.pack(side='top', pady=0, padx=0, anchor='w')
            label_treedata.pack(side='top', padx=0, pady=0, fill='both', expand=True)
            label_db_struct.config(bg='white')
            get_database_structure()
            children = label_treedata.winfo_children()
            if len(children) > 2:
                children[2].destroy() 
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

label_db_struct = tkinter.Frame(m, padx=0, pady=0)
label_db_struct.pack(side='left', fill='both', expand=True)

label_browse_data = tkinter.Frame(m, padx=0, pady=0)
label_treedata = tkinter.Frame(label_browse_data, bg="white", padx=0, pady=0)

h1 = tkinter.Scrollbar(label_treedata, orient = 'horizontal')
h1.pack(side = BOTTOM, fill = X)
v1 = tkinter.Scrollbar(label_treedata)
v1.pack(side = RIGHT, fill = Y)

h2 = tkinter.Scrollbar(label_db_struct, orient = 'horizontal')
h2.pack(side = BOTTOM, fill = X)
v2 = tkinter.Scrollbar(label_db_struct)
v2.pack(side = RIGHT, fill = Y)



inputtxt = tkinter.Text(label_sql, height=5, width=50)
printButton = tkinter.Button(label_sql, text="Enter Query", command=execute_query)

combo = ttk.Combobox(
    label_browse_data,
    state="readonly"
)
combo.bind("<<ComboboxSelected>>", switch_tables)

m.mainloop()
