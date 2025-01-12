import tkinter
from tkinter import filedialog, Menu
from tkinter import messagebox
import sqlite3

sqlite = None  
kursor = None  

def import_db():
    global sqlite, kursor, inputtxt, printButton

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
m.title("SQLite Test")
m.geometry("1000x500")


navbar = Menu(m)
filemenu = Menu(navbar, tearoff=0)
filemenu.add_command(label="Open Database", command=import_db)
navbar.add_cascade(label="File", menu=filemenu)
m.config(menu=navbar)


inputtxt = tkinter.Text(m, height=5, width=50)
printButton = tkinter.Button(m, text="Enter Query", command=execute_query)

m.mainloop()