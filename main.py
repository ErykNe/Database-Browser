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

    export_window = Toplevel(m)
    export_window.title("Export database")
    export_window.geometry("650x270")
    
    label_frame = LabelFrame(export_window, text="File Details: ")
    label_frame.pack(fill='x', padx=10, pady=10)
    
    file_name_label = Label(label_frame, text="File name:")
    file_name_label.pack(side='left', padx=10, pady=10, anchor='n')
    file_name_var = StringVar(value="name")
    name_entry = Entry(label_frame, textvariable=file_name_var)
    name_entry.pack(side='left', padx=10, pady=10, anchor='n')
    
    file_src_label = Label(label_frame, text="File path:")
    file_src_label.pack(side='left', padx=10, pady=10, anchor='n')
    

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop") # set the deafult path to desktop
    
    # handle combobox selection
    def on_select(event):
        if var.get() == "Other...":
            folder_path = filedialog.askdirectory(parent=export_window)  # Open folder dialog to select a directory
            if folder_path:  
                var.set(folder_path)  
            else:
                var.set(desktop_path)    


    
    # the combobox that asks for directory
    var = StringVar()
    options = [desktop_path, "Other..."]
    path_combobox = ttk.Combobox(label_frame, textvariable=var, values=options, state="normal")
    path_combobox.pack(fill='x', padx=10, pady=10, anchor='n')
    path_combobox.bind("<<ComboboxSelected>>", on_select) 

    path_combobox.set(desktop_path) # set the deafult path to desktop

    checkbox_frame = LabelFrame(export_window, text="File Type:")
    checkbox_frame.pack(fill='x', padx=10, pady=10)

    # file type variables
    db_var = BooleanVar(value=False)
    sql_var = BooleanVar(value=False)
    xml_var = BooleanVar(value=False)


    db_checkbox = Checkbutton(checkbox_frame, text=".db", variable=db_var)
    db_checkbox.pack(side='left', padx=10, pady=10)

    sql_checkbox = Checkbutton(checkbox_frame, text=".sql", variable=sql_var)
    sql_checkbox.pack(side='left', padx=10, pady=10)

    xml_checkbox = Checkbutton(checkbox_frame, text=".xml", variable=xml_var)
    xml_checkbox.pack(side='left', padx=10, pady=10)
    
    def export_db_to_db_file(file_name, selected_path):
        # ensuring if the connection is valid
        if not sqlite or not kursor:
            messagebox.showerror("Error", "Database connection is not established.")
            return
    
        db_file_path = os.path.join(selected_path, f"{file_name}.db")
    
        try:

            new_connection = sqlite3.connect(db_file_path) # opening new connection to write the .db file
            new_kursor = new_connection.cursor()
            kursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = kursor.fetchall()
        
            for table in tables:
                table_name = table[0]
                kursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                table_query = kursor.fetchone()[0]
                new_kursor.execute(table_query)
                kursor.execute(f"SELECT * FROM {table_name};")
                rows = kursor.fetchall()
                for row in rows:
                    values = ', '.join('?' for _ in row) 
                    insert_query = f"INSERT INTO {table_name} VALUES ({values});"
                    new_kursor.executemany(insert_query, [row])

            kursor.execute("SELECT name, sql FROM sqlite_master WHERE type='view';")
            views = kursor.fetchall()
            for view in views:
                view_name, view_query = view
                new_kursor.execute(view_query)  # creating views in the new file 

            kursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger';")
            triggers = kursor.fetchall()
            for trigger in triggers:
                trigger_name, trigger_query = trigger
                new_kursor.execute(trigger_query)  # creating triggers in the new file 

            new_connection.commit()
            new_connection.close()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export to DB file: {str(e)}")

    def export_db_to_sql_file(file_name, selected_path):
        # ensuring if the connection is valid
        if not sqlite or not kursor:
            messagebox.showerror("Error", "Database connection is not established.")
            return
    
        sql_file_path = os.path.join(selected_path, f"{file_name}.sql")
    
        try:
            # writing the .sql file using built-in .dump method
            with open(sql_file_path, 'w') as sql_file:
                for line in sqlite.iterdump():
                    sql_file.write(f"{line}\n")
        
        except Exception as e: # handling errors
            messagebox.showerror("Error", f"Failed to export to SQL file: {str(e)}")
    
    def export_db_to_xml_file(file_name, selected_path):
        # Ensure that the SQLite connection and cursor are valid
        if not sqlite or not kursor:
            messagebox.showerror("Error", "Database connection is not established.")
            return

        # Determine the file path for the new XML file
        xml_file_path = os.path.join(selected_path, f"{file_name}.xml")

        try:
            # Open the XML file for writing
            with open(xml_file_path, 'w', encoding='utf-8') as xml_file:
                # Write the XML header
                xml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                xml_file.write('<database>\n')

                # Export tables and their data
                kursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = kursor.fetchall()

                for table in tables:
                    table_name = table[0]
                    xml_file.write(f'  <table name="{table_name}">\n')

                    # Get table columns
                    kursor.execute(f"PRAGMA table_info({table_name});")
                    columns = kursor.fetchall()

                    # Write table schema
                    xml_file.write('    <schema>\n')
                    for column in columns:
                        col_name = column[1]
                        col_type = column[2]
                        is_pk = column[5]
                        xml_file.write(f'      <column name="{col_name}" type="{col_type}" primary_key="{is_pk}" />\n')
                    xml_file.write('    </schema>\n')

                    # Write table data
                    kursor.execute(f"SELECT * FROM {table_name};")
                    rows = kursor.fetchall()
                    column_names = [column[1] for column in columns]
                    xml_file.write('    <data>\n')
                    for row in rows:
                        xml_file.write('      <row>\n')
                        for col_name, value in zip(column_names, row):
                            xml_file.write(f'        <{col_name}>{value}</{col_name}>\n')
                        xml_file.write('      </row>\n')
                    xml_file.write('    </data>\n')

                    xml_file.write('  </table>\n')

                # Export views
                kursor.execute("SELECT name, sql FROM sqlite_master WHERE type='view';")
                views = kursor.fetchall()

                for view in views:
                    view_name, view_sql = view
                    xml_file.write(f'  <view name="{view_name}">\n')
                    xml_file.write(f'    <definition>{view_sql}</definition>\n')
                    xml_file.write('  </view>\n')
                    
                # Export triggers
                kursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger';")
                triggers = kursor.fetchall()
                for trigger in triggers:
                    trigger_name, trigger_sql = trigger
                    xml_file.write(f'  <trigger name="{trigger_name}">\n')
                    xml_file.write(f'    <definition>{trigger_sql}</definition>\n')
                    xml_file.write('  </trigger>\n')

                # Close the database XML tag
                xml_file.write('</database>\n')
    

                # Export relationships (foreign keys)
                for table in tables:
                    table_name = table[0]
                    kursor.execute(f"PRAGMA foreign_key_list({table_name});")
                    foreign_keys = kursor.fetchall()
                    if foreign_keys:
                        xml_file.write(f'  <relations table="{table_name}">\n')
                        for fk in foreign_keys:
                            xml_file.write(
                                f'    <foreign_key column="{fk[3]}" references_table="{fk[2]}" references_column="{fk[4]}" />\n'
                            )
                        xml_file.write('  </relations>\n')

                # Close the database XML tag
                xml_file.write('</database>\n')

        # Success message
            messagebox.showinfo("Success", f"Database exported to XML file at: {xml_file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export to XML file: {str(e)}")

    def confirm_export():
        selected_path = var.get()
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

        selected_types = ", ".join(file_types)
        print(selected_types, file_types)
        for file_type in file_types:
            match file_type: # exporting files depending on what the user has selected
                case '.db':
                    export_db_to_db_file(file_name, selected_path) 
                case '.sql':
                    export_db_to_sql_file(file_name, selected_path)
                case '.xml':
                    export_db_to_xml_file(file_name, selected_path)
        messagebox.showinfo("Success", f"Database exported to:\n{os.path.join(selected_path, file_name)}\nFile types: {selected_types}")

    export_button = Button(export_window, text="Export", command=confirm_export, width=18)
    export_button.pack(pady=20,padx=10, side='left', anchor='n')

def create_column(table_name):
    create_column_window = Toplevel(m)
    create_column_window.title("Create Column")

    label_frame = LabelFrame(create_column_window, text="Column Details: ")
    label_frame.pack(fill='x', padx=10, pady=10)

    columns = ('Name', 'Type', 'Default', 'NN', 'PK', 'AI')

    widget_frame = Frame(label_frame) 
    widget_frame.pack(fill='x', padx=10, pady=5)

    row_widgets = []
    variables = []
    
    def create_column_in_db(table_name, variables):
  
        column_name = variables[0].get() 
        column_type = variables[1].get()  
        default_value = variables[2].get()  
        nn = variables[3].get() 
        pk = variables[4].get()  
        ai = variables[5].get() 

        try:
            query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"

            constr = []
            if nn:
                constr.append("NOT NULL")
            if pk:
                constr.append("PRIMARY KEY")
            if ai:
                constr.append("AUTOINCREMENT")
            if constr:
                query += " " + " ".join(constr)
            if default_value:
                query += f" DEFAULT {default_value}"

            kursor.execute(query)
            sqlite.commit()
            get_database_structure()

            messagebox.showinfo("Success", f"Column '{column_name}' added to table '{table_name}'.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add column: {e}")

    # creating some widgets for user to specify column properties
    for col_index, col_name in enumerate(columns):
        if col_name == 'Type':
            widget_label = Label(widget_frame, text=col_name, width=5, anchor="w")
            widget_label.pack(side='left', padx=5, pady=5)
            var = StringVar()
            widget = ttk.Combobox(widget_frame, textvariable=var, values=["INTEGER", "TEXT", "BLOB", "REAL", "NUMERIC"])
        elif col_name in ['NN', 'PK', 'AI']:
            group_frame = Frame(label_frame)
            group_frame.pack(side='left', padx=5, pady=5, anchor='nw')
            widget_label = Label(group_frame, text=col_name, width=5, anchor="nw")
            widget_label.pack(padx=0)  
            var = BooleanVar()
            widget = Checkbutton(group_frame, variable=var)
            widget.pack(side='left', padx=0) 
        else:
            widget_label = Label(widget_frame, text=col_name, width=5, anchor="w")
            widget_label.pack(side='left', padx=5, pady=5)
            var = StringVar()
            widget = Entry(widget_frame, textvariable=var)

        widget.pack(side='left', padx=0, anchor='w')
        row_widgets.append(widget)
        variables.append(var)

    Button(create_column_window, text="Create Column", command=lambda: create_column_in_db(table_name, variables)).pack(side='left', padx=5, pady=10, anchor='n')

def create_table():
    create_window = Toplevel(m)
    create_window.title("Create Table")
    create_window.geometry("700x325")
    

    label_frame = LabelFrame(create_window, text="Table Name: ")
    label_frame.pack(fill='x')
    name_var = StringVar(value="name")
    name_entry = Entry(label_frame, textvariable=name_var)
    name_entry.pack(side='top', anchor='w', padx=10, pady=10)
    
    columns = ('Name', 'Type', 'NN', 'PK', 'AI', 'Default')
    tree = ttk.Treeview(create_window, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    widgets = []
    variables = []

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

        widgets.append((row_widgets))
        variables.append(variables)

    def remove_row():
        selected_item = tree.selection()
        if selected_item:
            tree.delete(selected_item)
            for idx, widgets in enumerate(widgets): 
                if tree.get_children()[idx] == selected_item[0]:  # match by treeview item ID
                    for widget in widgets:
                        widget.destroy()
                    widgets.pop(idx)
                    variables.pop(idx) 
                    break
        elif tree.get_children():
            last_item = tree.get_children()[-1]
            tree.delete(last_item)
            widgets = widgets.pop()  
            variables.pop()  # remove corresponding variables
            for widget in widgets:
                widget.destroy()

    def execute_create_table_query():
        if not widgets or widgets == []:
            messagebox.showerror("Error",f"Error creating table: No columns provided")
            return
        query = f"CREATE TABLE {name_entry.get()} ("

        for variables in variables:
            column_name = variables[0].get().strip()
            column_type = variables[1].get().strip()
            nn = "NOT NULL" if variables[2].get() == 1 else ""
            pk = "PRIMARY KEY" if variables[3].get() == 1 else ""
            ai = "AUTOINCREMENT" if variables[4].get() == 1 and variables[3].get() != 1 else ""
            default_value = f"DEFAULT '{variables[5].get()}'" if variables[5].get() != "" else ""

            column_definition = f"{column_name} {column_type} {nn} {pk} {ai} {default_value}".strip()

            query += column_definition + ", "

        query = query.rstrip(", ") + ");"

        try:
            kursor.execute(query)
            sqlite.commit()
            messagebox.showinfo("Success", f"Successfully created table '{name_entry.get()}'.")
            combo['values'] = [name_entry.get()] + list(combo['values'])
            combo.set(name_entry.get())
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

    # clear any existing child widgets
    children = label_db_struct.winfo_children()
    if len(children) > 2:
        children[2].destroy()

    tree = ttk.Treeview(label_db_struct, xscrollcommand=h2.set, yscrollcommand=v2.set)
    tree.pack(expand=True, fill="both")
    columns = ["Type", "Schema"]

    tree["columns"] = columns
    tree.heading("#0", text="Name", anchor='w')
    tree.heading("Type", text="Type", anchor='w')
    tree.heading("Schema", text="Schema", anchor='w')

    longest_schema_length = 0 # for column lengths adjustement

    # configure underline tag for primary keys
    tree.tag_configure("underline", font=("", 9, "underline"))

    table_node = tree.insert("", "end", text="Tables", open=True, tags=("table_node",))

    query_table_names = "SELECT name, type, sql FROM sqlite_master WHERE type='table'"
    tables = kursor.execute(query_table_names).fetchall()
    sqlite.commit()

    for table in tables:
        name = str(table[0])
        schema = str(table[2]).replace("\n", " ") # making the single-line schema

        if longest_schema_length < len(schema):
            longest_schema_length = len(schema)

        table_item = tree.insert(table_node, "end", text=name, open=False, values=("", schema), tags=("table",))
        table_info = f"PRAGMA table_info({name});"
        table_struct = kursor.execute(table_info).fetchall()
        sqlite.commit()
        for struct in table_struct:
            result = f'"{struct[1]}" {struct[2]} {"NOT NULL " if struct[3] == 1 else ""} {"PRIMARY KEY" if struct[5] == 1 else ""}'
            column_item = tree.insert(table_item, "end", text=str(struct[1]), values=(str(struct[2]), result), tags=("column",))

            if struct[5] == 1:
                tree.item(column_item, tags=("column", "underline"))

    view_node = tree.insert("", "end", text="Views", open=True, tags=("view_node",))

    query_view_names = "SELECT name, type, sql FROM sqlite_master WHERE type='view'"
    views = kursor.execute(query_view_names).fetchall()
    sqlite.commit()

    for view in views:
        name = str(view[0])
        schema = str(view[2]).replace("\n", " ")

        if longest_schema_length < len(schema):
            longest_schema_length = len(schema)

        tree.insert(view_node, "end", text=name, open=False, values=("", schema), tags=("view",))

    trigger_node = tree.insert("", "end", text="Triggers", open=True, tags=("trigger_node",))

    query_triggers_names = "SELECT name, type, sql FROM sqlite_master WHERE type='trigger'"
    triggers = kursor.execute(query_triggers_names).fetchall()
    sqlite.commit()

    for trigger in triggers:
        name = str(trigger[0])
        schema = str(trigger[2]).replace("\n", " ")

        if longest_schema_length < len(schema):
            longest_schema_length = len(schema)

        tree.insert(trigger_node, "end", text=name, open=False, values=("", schema), tags=("trigger",))

    tree.column("#0", width=max((int(m.winfo_width() / 3)), 100), stretch=False)
    tree.column(columns[0], width=max((int(m.winfo_width() / 3)), 100), stretch=False)
    tree.column(columns[1], width=max((longest_schema_length * 6), 100), anchor='w', stretch=False)

    h2.config(command=tree.xview)
    v2.config(command=tree.yview)

    # handling some useful functions under the right click
    def right_click(event):
        selected_item = tree.identify("item", event.x, event.y)
        selected_tags = tree.item(selected_item, "tags")

        if "table_node" in selected_tags:
            tree.selection_set(selected_item)
            menu = tkinter.Menu(m, tearoff=0)
            menu.add_command(label="Add Table", command=create_table)
            menu.post(event.x_root, event.y_root)
        elif "table" in selected_tags:
            tree.selection_set(selected_item)
            table_name = tree.item(selected_item, "text")
            menu = tkinter.Menu(m, tearoff=0)
            menu.add_command(label="Add Column", command=lambda: create_column(table_name))
            menu.post(event.x_root, event.y_root)

    tree.bind("<Button-3>", right_click)
    
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
    match(view): # changing tabs
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
            label_sql.pack(fill='x', pady=(2, 0)) 
    
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

def create_db_from_xml(xml_file):
    global sqlite, kursor
    try:
        # Remove temp.db if it exists
        if os.path.exists("temp.db"):
            os.remove("temp.db")

        # Create a new SQLite database
        sqlite = sqlite3.connect("temp.db")
        kursor = sqlite.cursor()

        # Enable foreign key constraints
        kursor.execute("PRAGMA foreign_keys = ON;")

        # Parse the XML file
        with open(xml_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract content up to the closing </database> tag
        if "</database>" in content:
            valid_xml = content.split("</database>")[0] + "</database>"
        else:
            raise ET.ParseError("Missing closing </database> tag.")

        # Parse the valid portion of the XML
        root = ET.fromstring(valid_xml)

        # Parse relationships for foreign key constraints
        relations = {}
        for relation in root.findall("relations"):
            table_name = relation.get("table")
            foreign_keys = []
            for fk in relation.findall("foreign_key"):
                column = fk.get("column")
                ref_table = fk.get("references_table")
                ref_column = fk.get("references_column")
                foreign_keys.append(f"FOREIGN KEY ({column}) REFERENCES {ref_table}({ref_column})")
            relations[table_name] = foreign_keys

        # Create tables and insert data
        for table in root.findall("table"):
            table_name = table.get("name")

            # Create table schema
            schema = table.find("schema")
            columns = []
            for column in schema.findall("column"):
                col_name = column.get("name")
                col_type = column.get("type")
                is_pk = "PRIMARY KEY" if column.get("primary_key") == "1" else ""
                columns.append(f"{col_name} {col_type} {is_pk}".strip())

            # Add foreign key constraints if any
            if table_name in relations:
                columns += relations[table_name]

            create_table_sql = f"CREATE TABLE {table_name} ({', '.join(columns)});"
            kursor.execute(create_table_sql)

            # Insert table data
            data = table.find("data")
            if data is not None:
                for row in data.findall("row"):
                    col_names = []
                    col_values = []
                    for col in row:
                        col_names.append(col.tag)
                        col_values.append(col.text)

                    insert_sql = f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES ({', '.join(['?' for _ in col_values])});"
                    kursor.execute(insert_sql, col_values)

        # Create views
        for view in root.findall("view"):
            view_name = view.get("name")
            view_definition = view.find("definition").text
            kursor.execute(view_definition)

        # Create triggers
        for trigger in root.findall("trigger"):
            trigger_name = trigger.get("name")
            trigger_definition = trigger.find("definition").text
            kursor.execute(trigger_definition)

        # Commit changes
        sqlite.commit()
        messagebox.showinfo("Success", "Database created successfully from XML file with foreign keys!")

    except sqlite3.Error as e:
        messagebox.showerror("Error", f"SQLite Error: {e}")
    except ET.ParseError as e:
        messagebox.showerror("Error", f"XML Parse Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected Error: {e}") 

def import_db():
    global sqlite, kursor, sql_input_textbox, sql_output_textbox, print_button, combo, m, label_treedata, result_label

    db_path = filedialog.askopenfilename(
        title="Select a .db file",
        filetypes=[("SQLite Database", "*.db")]
    )
    
    os.chmod(db_path, 0o666) # asking for access to edit the .db file
    
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
            
            m.title("SQLite Database Manager - " + str(db_path)) # config all neccesseary things 
            print_button.pack(side='top', pady=5, anchor='w')
            sql_input_textbox.pack(side='top', pady=5, anchor='w', fill='x')  
            result_label.pack(anchor='w',fill='both') 
            children = result_label.winfo_children()
            if len(children) > 2:
                children[2].destroy()
                
            tree = ttk.Treeview(result_label, xscrollcommand=h3.set, yscrollcommand=v3.set)
            tree.pack(anchor='w', side='top',fill='both')
            sql_output_textbox.pack(side='top', pady=5, anchor='w', fill='both')
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

def export_table_to_csv():
    global sqlite, kursor, combo, m

    if not sqlite:
        messagebox.showerror("Error", "No database connection found.")
        return

    
    kursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in kursor.fetchall()]

    if not tables:
        messagebox.showerror("Error", "No tables found in the database.")
        return

    export_window = Toplevel(m)
    export_window.title("Export Table to CSV")

    Label(export_window, text="Select Table: ").grid(row=0, column=0)
    table_var = StringVar()
    table_combo = ttk.Combobox(export_window, textvariable=table_var, values=tables, state="readonly")
    table_combo.grid(row=0, column=1)
    
    Label(export_window, text="Select path:").grid(row=1, column=0)
    

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    
    
    def selection(event):
        if combo_var.get() == "Other...":
            folder_path = filedialog.askdirectory(parent=export_window) 
            if folder_path: 
                combo_var.set(folder_path)  
            else:
                combo_var.set(desktop_path)    

    combo_var = StringVar()
    options = [desktop_path, "Other..."]
    combobox = ttk.Combobox(export_window, textvariable=combo_var, values=options, state="normal")
    combobox.grid(row=1, column=1)
    combobox.bind("<<ComboboxSelected>>", selection)
    combobox.set(desktop_path)
    
    Label(export_window, text="Delimiter: ").grid(row=2, column=0)
    delimiter_var = StringVar(value=",")
    delimiter_entry = Entry(export_window, textvariable=delimiter_var)
    delimiter_entry.grid(row=2, column=1)

    Label(export_window, text="Quote Character: ").grid(row=3, column=0)
    quote_char_var = StringVar(value='"')
    quote_char_entry = Entry(export_window, textvariable=quote_char_var)
    quote_char_entry.grid(row=3, column=1)

    Label(export_window, text="Encoding: ").grid(row=4, column=0)
    encoding_var = StringVar(value="UTF-8")
    encoding_entry = Entry(export_window, textvariable=encoding_var)
    encoding_entry.grid(row=4, column=1)
    
    def export():
        selected_table = table_var.get()
        if not selected_table:
            messagebox.showerror("Error", "Please select a table.")
            return

        folder_path = combo_var.get()
        if not folder_path:
            messagebox.showerror("Error", "Please select a folder path.")
            return

        delimiter = delimiter_var.get()
        quote_char = quote_char_var.get()
        encoding = encoding_var.get()

        try:
            kursor.execute(f"SELECT * FROM {selected_table};")
            rows = kursor.fetchall()
            columns = [desc[0] for desc in kursor.description]

            csv_path = os.path.join(folder_path, f"{selected_table}.csv")

            with open(csv_path, mode="w", newline="", encoding=encoding) as csv_file:
                writer = csv.writer(csv_file, delimiter=delimiter, quotechar=quote_char, quoting=csv.QUOTE_MINIMAL)
                writer.writerow(columns) 
                writer.writerows(rows)  

            messagebox.showinfo("Success", f"Table exported successfully to {csv_path}")
            export_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export table: {e}")

    Button(export_window, text="Export", command=export).grid(row=5, column=0, columnspan=2)
    
def import_table_from_csv():
    global sqlite, kursor, sql_input_textbox, sql_output_textbox, print_button, combo, m, label_treedata
    if not sqlite:
        messagebox.showerror("Error", "No database connection found.")
        return
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
                    
                    combo['values'] = [table_name] + list(combo['values'])
                    combo.set(table_name)
            
                    get_database_structure()

            except Exception as e:
                messagebox.showerror("Error", f"Error importing CSV data: {e}")

            import_window.destroy()

        Button(import_window, text="Import", command=start_import).grid(row=4, columnspan=2)

def import_db_from_xml():    
    global sqlite, kursor, sql_input_textbox, print_button, m

    db_path = filedialog.askopenfilename(
        title="Select a .xml file",
        filetypes=[("Extensible Markup Language File", "*.xml")]
    )
    
    if db_path:  
        try:
            if(sqlite):
                sqlite.close()
            
            create_db_from_xml(db_path)
            result = kursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [str(table[0]) for table in result.fetchall()]

            combo.set("Select table")
            combo.config(values=tables)
            m.title("SQLite Database Manager - " + str(db_path))
            
            print_button.pack(side='top', pady=5, anchor='w')

            # Use grid to place sql_input_textbox and result_label next to each other
            sql_input_textbox.pack(side='top', pady=5, anchor='w', fill='x')  # 'ew' stretches sql_input_textbox horizontally
            result_label.pack(anchor='w',fill='both')  # 'ew' stretches result_label horizontally
            children = result_label.winfo_children()
            if len(children) > 2:
                children[2].destroy()
                
            tree = ttk.Treeview(result_label, xscrollcommand=h3.set, yscrollcommand=v3.set)
            tree.pack(anchor='w', side='top',fill='both')
            sql_output_textbox.pack(side='top', pady=5, anchor='w', fill='both')

            combo.pack(side='top', pady=0, padx=0, anchor='w')
            label_treedata.pack(side='top', padx=0, pady=0, fill='both', expand=True)
            label_db_struct.config(bg='white')
            get_database_structure()
            children = label_treedata.winfo_children()
            if len(children) > 2:
                children[2].destroy() 
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error connecting to database: {e}")
            import_db_from_xml()       
            
def import_db_from_sql():    
    global sqlite, kursor, sql_input_textbox, print_button, m

    db_path = filedialog.askopenfilename(
        title="Select a .sql file",
        filetypes=[("SQL Database", "*.sql")]
    )
    
    if db_path:  
        try:
            if(sqlite):
                sqlite.close()
            
            create_db_from_sql(db_path) # creating temporary .db file with data from .sql file
            result = kursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [str(table[0]) for table in result.fetchall()]

            combo.set("Select table")
            combo.config(values=tables)
            
            m.title("SQLite Database Manager - " + str(db_path)) # config all neccesseary things 
            print_button.pack(side='top', pady=5, anchor='w')
            sql_input_textbox.pack(side='top', pady=5, anchor='w', fill='x')  
            result_label.pack(anchor='w',fill='both') 
            children = result_label.winfo_children()
            if len(children) > 2:
                children[2].destroy()
                
            tree = ttk.Treeview(result_label, xscrollcommand=h3.set, yscrollcommand=v3.set)
            tree.pack(anchor='w', side='top',fill='both')
            sql_output_textbox.pack(side='top', pady=5, anchor='w', fill='both')
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
        query = sql_input_textbox.get(1.0, "end-1c").strip()  
        if not query or query == "":
            messagebox.showerror("Error", "No query typed in")
            return
        try:
            kursor.execute(query)

            # checking if its a select query to create treeview displaying the output 
            if query.lower().startswith("select"):
                result = kursor.fetchall()

                # clearing existing view if there is any
                for child in result_label.winfo_children():
                    child.destroy()

                if result:
                    sql_output_textbox.config(state='normal')
                    sql_output_textbox.delete(1.0, "end")
                    sql_output_textbox.insert("insert", f"Execution finished without errors.\n{query}\n")
                    sql_output_textbox.config(state='disabled')

                    columns = [desc[0] for desc in kursor.description] 


                    tree = ttk.Treeview(result_label, xscrollcommand=h3.set, yscrollcommand=v3.set)
                    tree["show"] = "headings"
                    tree["columns"] = columns


                    for col in columns:
                        tree.heading(col, text=col, anchor="center")
                        tree.column(col, width=100, anchor="center", stretch=False)

                    for row in result:
                        tree.insert("", "end", values=row)


                    tree.grid(row=0, column=0, sticky="nsew")

                    h3 = ttk.Scrollbar(result_label, orient="horizontal", command=tree.xview)
                    v3 = ttk.Scrollbar(result_label, orient="vertical", command=tree.yview)
                    tree.configure(xscrollcommand=h3.set, yscrollcommand=v3.set)

                    h3.grid(row=1, column=0, sticky="ew")
                    v3.grid(row=0, column=1, sticky="ns")

                    result_label.grid_rowconfigure(0, weight=1)
                    result_label.grid_columnconfigure(0, weight=1)

                else:
                    sql_output_textbox.config(state="normal")
                    sql_output_textbox.delete(1.0, "end")
                    sql_output_textbox.insert("insert", f"No results found for query:\n{query}\n")
                    sql_output_textbox.config(state="disabled")
            else: #for other queries
                sqlite.commit()
                get_database_structure()
                sql_output_textbox.config(state='normal')
                sql_output_textbox.delete(1.0, "end")
                sql_output_textbox.insert("insert",f"Execution finished without errors.\nAt line 1:\n{query}\n")
                sql_output_textbox.config(state='disabled')
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error executing query: {e}")
            sql_output_textbox.config(state='normal')
            sql_output_textbox.delete(1.0, "end")
            sql_output_textbox.config(state='disabled')

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
database_submenu.add_command(label="From XML File", command=import_db_from_xml)

importmenu.add_cascade(label="Database", menu=database_submenu)

table_submenu = Menu(importmenu, tearoff=0)
table_submenu.add_command(label="From CSV File", command=import_table_from_csv)

importmenu.add_cascade(label="Table", menu=table_submenu)
menuBar.add_cascade(label="Import", menu=importmenu)

exportmenu = Menu(menuBar, tearoff=0)
exportmenu.add_command(label="Database",command=export_db)

export_submenu = Menu(exportmenu, tearoff=0)
export_submenu.add_command(label="To CSV File", command=export_table_to_csv)

exportmenu.add_cascade(label="Table",menu=export_submenu)

menuBar.add_cascade(label="Export", menu=exportmenu)


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



sql_input_textbox = tkinter.Text(label_sql, height=5, width=50)
sql_output_textbox = tkinter.Text(label_sql, width=50)
result_label = tkinter.Frame(label_sql, width=50, height=5, bg='white')

h3 = tkinter.Scrollbar(result_label, orient = 'horizontal')
h3.pack(side = BOTTOM, fill = X)
v3 = tkinter.Scrollbar(result_label)
v3.pack(side = RIGHT, fill = Y)

print_button = tkinter.Button(label_sql, text="Execute Query", command=execute_query)

combo = ttk.Combobox(
    label_browse_data,
    state="readonly"
)
combo.bind("<<ComboboxSelected>>", switch_tables)

m.mainloop()