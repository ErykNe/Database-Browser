import tkinter
from tkinter import filedialog, Menu
from tkinter import messagebox
from tkinter import *
import sqlite3

sqlite = None  
kursor = None  

def switch_view(view):
    global m, nav_db_struct, nav_browse_data, nav_sql, label_sql
    
    match(view):
        case "1":
            nav_db_struct.config(bg=m.cget("bg"))
            nav_browse_data.config(bg='lightgray')
            nav_sql.config(bg='lightgray')
            
            label_sql.pack_forget()
        case "2":
            nav_db_struct.config(bg='lightgray')
            nav_browse_data.config(bg=m.cget("bg"))
            nav_sql.config(bg='lightgray')
            
            label_sql.pack_forget()
        case "3":
            nav_db_struct.config(bg='lightgray')
            nav_browse_data.config(bg='lightgray')
            nav_sql.config(bg=m.cget("bg"))
            
            label_sql.pack(fill='x', pady=(2, 0))  # 2px margin above the frame
    

            

def import_db():
    global sqlite, kursor, inputtxt, printButton, m

    db_path = filedialog.askopenfilename(
        title="Select a .db file",
        filetypes=[("SQLite Database", "*.db")]
    )
    
    if db_path:  
        try:
            sqlite = sqlite3.connect(db_path)
            kursor = sqlite.cursor()
            kursor.execute("PRAGMA schema_version;") # execute test
            
            # Show the Text box and Button only if the connection is successful
            m.title("SQLite Database Manager - " + str(db_path))
            inputtxt.pack()
            printButton.pack()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error connecting to database: {e}")
            import_db()

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
importmenu.add_command(label="Database")
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


inputtxt = tkinter.Text(label_sql, height=5, width=50)
printButton = tkinter.Button(label_sql, text="Enter Query", command=execute_query)

m.mainloop()