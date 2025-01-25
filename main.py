import csv
import os
import tkinter
from tkinter import filedialog, Menu
from tkinter import messagebox
from tkinter import *
from tkinter import ttk
import sqlite3
from tkinter import simpledialog
import xml.etree.ElementTree as ET

sqlite = None  
kursor = None  

def export_db():
    if not sqlite:
        messagebox.showerror("Error", "No connection identified")
        return

    # Create the export window
    export_window = Toplevel(m)
    export_window.title("Export database")
    export_window.geometry("650x270")
    
    # File Details LabelFrame
    label_frame = LabelFrame(export_window, text="File Details: ")
    label_frame.pack(fill='x', padx=10, pady=10)
    
    # File name input
    file_name_label = Label(label_frame, text="File name:")
    file_name_label.pack(side='left', padx=10, pady=10, anchor='n')
    file_name_var = StringVar(value="name")
    delimiter_entry = Entry(label_frame, textvariable=file_name_var)
    delimiter_entry.pack(side='left', padx=10, pady=10, anchor='n')
    
    # File path label
    file_src_label = Label(label_frame, text="File path:")
    file_src_label.pack(side='left', padx=10, pady=10, anchor='n')
    
    # Function to handle combobox selection
    def on_selection(event):
        if combo_var.get() == "Other...":
            folder_path = filedialog.askdirectory(parent=export_window)  # Open folder dialog to select a directory
            if folder_path:  # If a folder is selected
                combo_var.set(folder_path)  # Set the selected folder path in the combobox

    # Set the default value to Desktop
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # Create the combobox
    combo_var = StringVar()
    options = [desktop_path, "Other..."]
    combobox = ttk.Combobox(label_frame, textvariable=combo_var, values=options, state="normal")
    combobox.pack(fill='x', padx=10, pady=10, anchor='n')
    combobox.bind("<<ComboboxSelected>>", on_selection)  # Bind selection event

    # Set default path to desktop
    combobox.set(desktop_path)

    checkbox_frame = LabelFrame(export_window, text="File Type:")
    checkbox_frame.pack(fill='x', padx=10, pady=10)

    # File type variables
    db_var = BooleanVar(value=False)
    sql_var = BooleanVar(value=False)
    xml_var = BooleanVar(value=False)

    # Checkboxes
    db_checkbox = Checkbutton(checkbox_frame, text=".db", variable=db_var)
    db_checkbox.pack(side='left', padx=10, pady=10)

    sql_checkbox = Checkbutton(checkbox_frame, text=".sql", variable=sql_var)
    sql_checkbox.pack(side='left', padx=10, pady=10)

    xml_checkbox = Checkbutton(checkbox_frame, text=".xml", variable=xml_var)
    xml_checkbox.pack(side='left', padx=10, pady=10)
    
    def export_db_to_db_file(file_name, selected_path):
        print("exporting to db file")
        
    def export_db_to_sql_file(file_name, selected_path):
        print("exporting to sql file")
    
    def export_db_to_xml_file(file_name, selected_path):
        print("exporting to xml file")        

    # Confirm Button
    def confirm_export():
        selected_path = combo_var.get()
        file_name = file_name_var.get()
        file_types = []
        if db_var.get():
            file_types.append(".db")
        if sql_var.get():
            file_types.append(".sql")
        if xml_var.get():
            file_types.append(".xml")
        
        if not os.path.isdir(selected_path):
            messagebox.showerror("Error", "Please select a valid directory.")
            return
        if not file_name.strip():
            messagebox.showerror("Error", "File name cannot be empty.")
            return
        if not file_types:
            messagebox.showerror("Error", "Please select at least one file type.")
            return

        # Export logic here
        selected_types = ", ".join(file_types)
        print(selected_types, file_types)
        for file_type in file_types:
            match file_type:
                case '.db':
                    export_db_to_db_file(file_name, selected_path)
                case '.sql':
                    export_db_to_sql_file(file_name, selected_path)
                case '.xml':
                    export_db_to_xml_file(file_name, selected_path)
        messagebox.showinfo("Success", f"Database exported to:\n{os.path.join(selected_path, file_name)}\nFile types: {selected_types}")

    confirm_button = Button(export_window, text="Export", command=confirm_export, width=18)
    confirm_button.pack(pady=20,padx=10, side='left', anchor='n')
    

def create_table():
    create_window = Toplevel(m)
    create_window.title("Create Table")
    create_window.geometry("700x325")
    

    label_frame = LabelFrame(create_window, text="Table Name: ")
    label_frame.pack(fill='x')
    delimiter_var = StringVar(value="name")
    delimiter_entry = Entry(label_frame, textvariable=delimiter_var)
    delimiter_entry.pack(side='top', anchor='w', padx=10, pady=10)
    
    columns = ('Name', 'Type', 'NN', 'PK', 'AI', 'Default')
    tree = ttk.Treeview(create_window, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    # Always visible widgets setup
    widget_refs = []
    variables_refs = []

    def add_row():
        row_id = tree.insert('', 'end', values=["" for _ in columns])
        row_widgets = []
        variables = []
        for col_index, col_name in enumerate(columns):
            x, y, width, height = tree.bbox(row_id, f"#{col_index+1}")

            if col_name == 'Type':
                var = StringVar()
                widget = ttk.Combobox(create_window, textvariable=var, values=["INTEGER", "TEXT", "BLOB", "REAL", "NUMERIC"])
            elif col_name in ['NN', 'PK', 'AI']:
                var = BooleanVar()
                widget = Checkbutton(create_window, variable=var)
            else:
                var = StringVar()
                widget = Entry(create_window, textvariable=var)

            widget.place(x=x + tree.winfo_rootx() - create_window.winfo_rootx(),
                         y=y + tree.winfo_rooty() - create_window.winfo_rooty(),
                         width=width, height=height)

            row_widgets.append(widget)
            variables.append(var)

        widget_refs.append((row_widgets))
        variables_refs.append(variables)

    def remove_row():
        selected_item = tree.selection()
        if selected_item:
            tree.delete(selected_item)
            for idx, widgets in enumerate(widget_refs):  # No unpacking of `rid`
                if tree.get_children()[idx] == selected_item[0]:  # Match by treeview item ID
                    for widget in widgets:
                        widget.destroy()
                    widget_refs.pop(idx)
                    variables_refs.pop(idx)  # Remove corresponding variables
                    break
        elif tree.get_children():
            last_item = tree.get_children()[-1]
            tree.delete(last_item)
            widgets = widget_refs.pop()  # No `rid` here, just the widget list
            variables_refs.pop()  # Remove corresponding variables
            for widget in widgets:
                widget.destroy()

    def execute_create_table_query():
        print(widget_refs)
        print(variables_refs)
        query = f"CREATE TABLE {delimiter_entry.get()} ("

        for variables in variables_refs:
            column_name = variables[0].get().strip()
            column_type = variables[1].get().strip()
            is_nn = "NOT NULL" if variables[2].get() == 1 else ""
            is_pk = "PRIMARY KEY" if variables[3].get() == 1 else ""
            is_ai = "AUTOINCREMENT" if variables[4].get() == 1 and variables[3].get() != 1 else ""
            default_value = f"DEFAULT '{variables[5].get()}'" if variables[5].get() != "" else ""

            column_definition = f"{column_name} {column_type} {is_nn} {is_pk} {is_ai} {default_value}".strip()

            query += column_definition + ", "

        query = query.rstrip(", ") + ");"

        print(query)
        try:
            kursor.execute(query)
            sqlite.commit()
            messagebox.showinfo("Success", f"Successfully created table '{delimiter_entry.get()}'.")
            combo['values'] = [delimiter_entry.get()] + list(combo['values'])
            combo.set(delimiter_entry.get())
            create_window.destroy()
            get_database_structure()
        except sqlite3.Error as e:
            messagebox.showerror("Error",f"Error creating table: {e}")
            

    
    tree.pack(anchor='w', fill='x')
    
    Button(create_window, text="Add Row", command=add_row).pack(side='left', padx=5, pady=5, anchor='n')
    Button(create_window, text="Remove Row", command=remove_row).pack(side='left', padx=5, pady=5, anchor='n')
    Button(create_window, text="Create Table", command=execute_create_table_query).pack(side='left', padx=5, pady=5, anchor='n')
        

    
    

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
    tables = kursor.execute(query_table_names).fetchall()
    sqlite.commit()
    
    
    for table in tables:
        name = str(table[0])
        schema = str(table[2]).replace("\n", " ")
        
        if(longest_schema_length < len(schema)):
            longest_schema_length = len(schema)
        
        child_1 = tree.insert(table_node, "end", text=name, open=False, values=("", schema))
        query_pragma = f"PRAGMA table_info({name});"
        table_struct = kursor.execute(query_pragma).fetchall()
        sqlite.commit()
        for struct in table_struct:
            result = f'"{struct[1]}" {struct[2]} {"NOT NULL " if struct[3] == 1 else ""} {"PRIMARY KEY" if struct[5] == 1 else ""}'
            child_2 = tree.insert(child_1, "end", text=str(struct[1]), values=(str(struct[2]), result))
            
            if struct[5] == 1:
                tree.item(child_2, tags=("underline",))
            
    view_node = tree.insert("", "end", text="Views", open=True)
    
    query_view_names = "SELECT name, type, sql FROM sqlite_master WHERE type='view'"
    views = kursor.execute(query_view_names).fetchall()
    sqlite.commit()
    
    for view in views:
        name = str(view[0])
        schema = str(view[2]).replace("\n", " ")
        
        if(longest_schema_length < len(schema)):
            longest_schema_length = len(schema)
            
        child_1 = tree.insert(view_node, "end", text=name, open=False, values=("", schema))
        query_pragma = f"PRAGMA table_info({name});"
        table_struct = kursor.execute(query_pragma).fetchall()
        sqlite.commit()
        for struct in table_struct:
            result = f'"{struct[1]}" {struct[2]} {"NOT NULL " if struct[3] == 1 else ""} {"PRIMARY KEY" if struct[5] == 1 else ""}'
            tree.insert(child_1, "end", text=str(struct[1]), values=(str(struct[2]), result))
    
    trigger_node = tree.insert("", "end", text="Triggers", open=True)
    
    query_triggers_names = "SELECT name, type, sql FROM sqlite_master WHERE type='trigger'"
    triggers = kursor.execute(query_triggers_names).fetchall()   
    sqlite.commit()
    
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
            menu.add_command(label="Add Table", command=create_table)
            menu.post(event.x_root, event.y_root)

    tree.bind("<Button-3>", on_right_click)
    
    
            
        

def switch_tables(event):
    global combo, sqlite, kursor, label_browse_data, label_treedata
    
    selection = combo.get()
    query = f"SELECT * FROM {selection}"
    
    result = kursor.execute(query).fetchall()
    sqlite.commit()
    columns = [description[1] for description in kursor.execute(f"PRAGMA table_info({selection})").fetchall()]
    sqlite.commit(
        
        
    )
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
        tree.column(col, width=max(max_lengths[i] * 10, 100), anchor="center", stretch=False)  
    
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
    global sqlite, kursor, inputtxt, outputtxt, printButton, combo, m, label_treedata, result_label

    db_path = filedialog.askopenfilename(
        title="Select a .db file",
        filetypes=[("SQLite Database", "*.db")]
    )
    
    os.chmod(db_path, 0o666)
    
    if db_path:  
        try:
            if(sqlite):
                sqlite.close()
            
            sqlite = sqlite3.connect(db_path, check_same_thread=False, uri=True)
            kursor = sqlite.cursor()
            result = kursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [str(table[0]) for table in result.fetchall()]

            combo.set("Select table")
            combo.config(values=tables)
            m.title("SQLite Database Manager - " + str(db_path))
            
            printButton.pack(side='top', pady=5, anchor='w')

            # Use grid to place inputtxt and result_label next to each other
            inputtxt.pack(side='top', pady=5, anchor='w', fill='x')  # 'ew' stretches inputtxt horizontally
            result_label.pack(anchor='w',fill='both')  # 'ew' stretches result_label horizontally
            children = result_label.winfo_children()
            if len(children) > 2:
                children[2].destroy()
                
            tree = ttk.Treeview(result_label, xscrollcommand=h3.set, yscrollcommand=v3.set)
            tree.pack(anchor='w', side='top',fill='both')
            outputtxt.pack(side='top', pady=5, anchor='w', fill='both')

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

def import_table_from_csv():
    global sqlite, kursor, inputtxt, outputtxt, printButton, combo, m, label_treedata

    db_path = filedialog.askopenfilename(
        title="Select a .csv file",
        filetypes=[("Comma-Separated Values Files", "*.csv")]
    )  
    if db_path:  
        import_window = Toplevel(m)
        import_window.title("Import CSV Options")

        Label(import_window, text="Delimiter: ").grid(row=0, column=0)
        delimiter_var = StringVar(value=",")
        delimiter_entry = Entry(import_window, textvariable=delimiter_var)
        delimiter_entry.grid(row=0, column=1)

        Label(import_window, text="Quote Character: ").grid(row=1, column=0)
        quote_char_var = StringVar(value='"')
        quote_char_entry = Entry(import_window, textvariable=quote_char_var)
        quote_char_entry.grid(row=1, column=1)

        Label(import_window, text="Encoding: ").grid(row=2, column=0)
        encoding_var = StringVar(value="UTF-8")
        encoding_entry = Entry(import_window, textvariable=encoding_var)
        encoding_entry.grid(row=2, column=1)

        header_var = BooleanVar(value=True)
        header_check = Checkbutton(import_window, text="Column names in first row", variable=header_var)
        header_check.grid(row=3, columnspan=2)

        def start_import():
            table_name = os.path.splitext(os.path.basename(db_path))[0]
            try:
                with open(db_path, 'r', encoding=encoding_var.get()) as f:
                    reader = csv.reader(f, delimiter=delimiter_var.get(), quotechar=quote_char_var.get())

                    if header_var.get():
                        headers = next(reader)
                        columns = ', '.join([f'"{header}" TEXT' for header in headers])
                        kursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns});')
                    else:
                        headers = [f"Column{i+1}" for i in range(len(next(reader)))]
                        columns = ', '.join([f'"{header}" TEXT' for header in headers])
                        kursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns});')
                        f.seek(0)

                    for row in reader:
                        placeholders = ', '.join(['?'] * len(row))
                        kursor.execute(f'INSERT INTO "{table_name}" VALUES ({placeholders});', row)

                    sqlite.commit()
                    messagebox.showinfo("Success", f"Data imported into table '{table_name}'.")
                    
                    # Update the table list in the combobox
                    combo['values'] = [table_name] + list(combo['values'])
                    combo.set(table_name)
            
                    # Update the database structure
                    get_database_structure()

            except Exception as e:
                messagebox.showerror("Error", f"Error importing CSV data: {e}")

            import_window.destroy()

        Button(import_window, text="Import", command=start_import).grid(row=4, columnspan=2)


            
def import_db_from_sql():    
    global sqlite, kursor, inputtxt, printButton, m

    db_path = filedialog.askopenfilename(
        title="Select a .sql file",
        filetypes=[("SQL Database", "*.sql")]
    )
    
    if db_path:  
        try:
            if(sqlite):
                sqlite.close()
            
            create_db_from_sql(db_path)
            result = kursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [str(table[0]) for table in result.fetchall()]

            combo.set("Select table")
            combo.config(values=tables)
            m.title("SQLite Database Manager - " + str(db_path))
            
            printButton.pack(side='top', pady=5, anchor='w')

            # Use grid to place inputtxt and result_label next to each other
            inputtxt.pack(side='top', pady=5, anchor='w', fill='x')  # 'ew' stretches inputtxt horizontally
            result_label.pack(anchor='w',fill='both')  # 'ew' stretches result_label horizontally
            children = result_label.winfo_children()
            if len(children) > 2:
                children[2].destroy()
                
            tree = ttk.Treeview(result_label, xscrollcommand=h3.set, yscrollcommand=v3.set)
            tree.pack(anchor='w', side='top',fill='both')
            outputtxt.pack(side='top', pady=5, anchor='w', fill='both')

            combo.pack(side='top', pady=0, padx=0, anchor='w')
            label_treedata.pack(side='top', padx=0, pady=0, fill='both', expand=True)
            label_db_struct.config(bg='white')
            get_database_structure()
            children = label_treedata.winfo_children()
            if len(children) > 2:
                children[2].destroy() 
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error connecting to database: {e}")
            import_db_from_sql()       

def execute_query():
    global h3, v3
    if sqlite:
        query = inputtxt.get(1.0, "end-1c").strip()  
        try:
            # Execute the query
            kursor.execute(query)

            # Check if it’s a SELECT query
            if query.lower().startswith("select"):
                result = kursor.fetchall()

                # Clear existing Treeview if any
                for child in result_label.winfo_children():
                    child.destroy()

                if result:
                    outputtxt.config(state='normal')
                    outputtxt.delete(1.0, "end")
                    outputtxt.insert("insert", f"Execution finished without errors.\n{query}\n")
                    outputtxt.config(state='disabled')
                    # Display the results in Treeview
                    columns = [desc[0] for desc in kursor.description]  # Get column names

                    # Create Treeview widget
                    tree = ttk.Treeview(result_label, xscrollcommand=h3.set, yscrollcommand=v3.set)
                    tree["show"] = "headings"
                    tree["columns"] = columns

                    # Configure columns and headings
                    for col in columns:
                        tree.heading(col, text=col, anchor="center")
                        tree.column(col, width=100, anchor="center", stretch=False)

                    # Insert rows into the Treeview
                    for row in result:
                        tree.insert("", "end", values=row)

                    # Pack the Treeview widget
                    tree.grid(row=0, column=0, sticky="nsew")

                    # Add scrollbars
                    h3 = ttk.Scrollbar(result_label, orient="horizontal", command=tree.xview)
                    v3 = ttk.Scrollbar(result_label, orient="vertical", command=tree.yview)
                    tree.configure(xscrollcommand=h3.set, yscrollcommand=v3.set)

                    # Place scrollbars
                    h3.grid(row=1, column=0, sticky="ew")
                    v3.grid(row=0, column=1, sticky="ns")

                    # Configure grid weights for resizing
                    result_label.grid_rowconfigure(0, weight=1)
                    result_label.grid_columnconfigure(0, weight=1)

                else:
                    # Handle case with no results
                    outputtxt.config(state="normal")
                    outputtxt.delete(1.0, "end")
                    outputtxt.insert("insert", f"No results found for query:\n{query}\n")
                    outputtxt.config(state="disabled")
            else:
                # For non-SELECT queries (like INSERT/UPDATE)
                sqlite.commit()
                get_database_structure()
                outputtxt.config(state='normal')
                outputtxt.delete(1.0, "end")
                outputtxt.insert("insert",f"Execution finished without errors.\nAt line 1:\n{query}\n")
                outputtxt.config(state='disabled')
        except sqlite3.Error as e:
            # Handle SQL errors
            messagebox.showerror("Error", f"Error executing query: {e}")
            outputtxt.config(state='normal')
            outputtxt.delete(1.0, "end")
            outputtxt.config(state='disabled')

m = tkinter.Tk()
m.title("SQLite Database Manager")
m.geometry("1000x500")
m.resizable(False, False)


menuBar = Menu(m)
filemenu = Menu(menuBar, tearoff=0)
filemenu.add_command(label="Open Database", command=import_db)
menuBar.add_cascade(label="File", menu=filemenu)

importmenu = Menu(menuBar, tearoff=0)

database_submenu = Menu(importmenu, tearoff=0)
database_submenu.add_command(label="From SQL File", command=import_db_from_sql)

importmenu.add_cascade(label="Database", menu=database_submenu)

table_submenu = Menu(importmenu, tearoff=0)
table_submenu.add_command(label="From CSV File", command=import_table_from_csv)

importmenu.add_cascade(label="Table(s)", menu=table_submenu)
menuBar.add_cascade(label="Import", menu=importmenu)

exportmenu = Menu(menuBar, tearoff=0)
exportmenu.add_command(label="Database",command=export_db)

export_submenu = Menu(exportmenu, tearoff=0)
export_submenu.add_command(label="From CSV File")

exportmenu.add_cascade(label="Table",menu=export_submenu)

menuBar.add_cascade(label="Export", menu=exportmenu)

menuBar.add_cascade(label="View")

m.config(menu=menuBar)


navbar = tkinter.Frame(m, bg='lightgray', padx=5, pady=0)
navbar.pack(fill='x', side='top')


nav_db_struct = tkinter.Button(navbar, text="Database structure", borderwidth=0, relief="flat", bg=m.cget("bg"), command=lambda: switch_view("1"))
nav_db_struct.pack(side="left")

def on_right_click(event):
    menu = tkinter.Menu(m, tearoff=0)
    menu.add_command(label="Refresh", command=get_database_structure)
    menu.post(event.x_root, event.y_root)

nav_db_struct.bind("<Button-3>", on_right_click)
    

nav_browse_data = tkinter.Button(navbar, text="Browse data", borderwidth=0, relief="flat", bg='lightgray', command=lambda: switch_view("2"))
nav_browse_data.pack(side="left")

nav_sql = tkinter.Button(navbar, text="Execute SQL", borderwidth=0, relief="flat", bg='lightgray', command=lambda: switch_view("3"))
nav_sql.pack(side="left")

label_sql = tkinter.Frame(m, padx=0, pady=0)

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
outputtxt = tkinter.Text(label_sql, width=50)
result_label = tkinter.Frame(label_sql, width=50, height=5, bg='white')

h3 = tkinter.Scrollbar(result_label, orient = 'horizontal')
h3.pack(side = BOTTOM, fill = X)
v3 = tkinter.Scrollbar(result_label)
v3.pack(side = RIGHT, fill = Y)

printButton = tkinter.Button(label_sql, text="Execute Query", command=execute_query)

combo = ttk.Combobox(
    label_browse_data,
    state="readonly"
)
combo.bind("<<ComboboxSelected>>", switch_tables)

m.mainloop()