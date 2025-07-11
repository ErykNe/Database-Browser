import base64
import csv
import os
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
from tkinter import ttk
import sqlite3
import xml.etree.ElementTree as et
from exports import export_db, export_table_to_csv,export_table_to_json
from db_utils import *

db_connection = None
cursor = None


def get_file_extension_from_blob(blob_data):
    # getting the image extension from blob data by interpretation of magic numbers
    if blob_data.startswith(b'\x89PNG'):
        return 'png'

    elif blob_data.startswith(b'\xFF\xD8\xFF'):
        return 'jpg'

    elif blob_data.startswith(b'GIF'):
        return 'gif'

    return 'bin'


def download_blob(blob_data, file_extension=None):
    try:
        if not file_extension:
            file_extension = get_file_extension_from_blob(blob_data)

            if not file_extension:
                file_extension = "bin"

        file_path = filedialog.asksaveasfilename(defaultextension=f".{file_extension}",
                                                 filetypes=[(f"{file_extension.upper()} files", f"*.{file_extension}")])
        if file_path:
            with open(file_path, 'wb') as file:
                file.write(blob_data)
            messagebox.showinfo("Success", f"File successfully saved to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file: {str(e)}")


def switch_tables(event):
    global combo, db_connection, cursor, label_browse_data, label_treedata, h1, v1
    selection = combo.get()
    query = f"SELECT * FROM {selection}"

    result = cursor.execute(query).fetchall()
    columns = [description[1] for description in cursor.execute(f"PRAGMA table_info({selection})").fetchall()]

    children = label_treedata.winfo_children()
    if len(children) > 2:
        children[2].destroy()
        children[3].destroy()

    tree = ttk.Treeview(label_treedata, xscrollcommand=h1.set, yscrollcommand=v1.set)

    h1.config(command=tree.xview)
    v1.config(command=tree.yview)

    tree["columns"] = columns
    tree["show"] = "headings"

    max_lengths = [len(col) for col in columns]

    column_types = [desc[2] for desc in cursor.execute(f"PRAGMA table_info({selection})").fetchall()]

    for row in result:
        for i, value in enumerate(row):
            max_lengths[i] = max(max_lengths[i], len(str(value)))

    for i, col in enumerate(columns):
        width = max(max_lengths[i] * 10, 100)
        if column_types[i] == "BLOB":
            width = 100
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor="center", stretch=False)

    def on_cell_click(event):
        # get the clicked item (row) and column
        tree = event.widget
        item_id = tree.identify_row(event.y)
        column_id = tree.identify_column(event.x)

        if item_id and column_id:
            # get the column index and row index
            col_index = int(column_id.lstrip("#")) - 1
            row_index = list(tree.get_children()).index(item_id)

            if row_index < 0 or row_index >= len(result):
                return

                # get the data from the clicked row and column
            row_values = result[row_index]
            value = row_values[col_index]
            if column_types[col_index] == "BLOB":  # if it was blob then download it
                download_blob(value)

    def on_cell_double_click(event):
        tree = event.widget
        item_id = tree.identify_row(event.y)
        column_id = tree.identify_column(event.x)

        if item_id and column_id.startswith("#"):
            col_index = int(column_id.lstrip("#")) - 1
            row_index = list(tree.get_children()).index(item_id)

            if row_index < 0 or row_index >= len(result):
                return

            row_values = result[row_index]

            primary_key_column = None
            primary_key_value = None
            for i, column in enumerate(columns):
                if column_types[i] == "INTEGER" and str(
                        cursor.execute(f"PRAGMA table_info({selection})").fetchall()[i][5] == "1"):
                    primary_key_column = column
                    primary_key_value = row_values[i]
                    break

            if not primary_key_column:
                messagebox.showerror("Error", "No primary key found for this table.")
                return

            bbox = tree.bbox(item_id, column_id)
            if not bbox:
                return

            x, y, width, height = bbox

            entry = Entry(tree)
            entry.place(x=x, y=y + height // 2, width=width, anchor='w')

            entry.insert(0, tree.item(item_id, "values")[col_index] if item_id else "")

            def save_value(event):
                new_value = entry.get()
                try:
                    query = f"UPDATE {selection} SET {columns[col_index]} = {("'" + str(new_value) + "'") if column_types[col_index] != 'INTEGER' else int(new_value)} WHERE {primary_key_column} = {("'" + str(primary_key_value) + "'") if column_types[i] != 'INTEGER' else int(primary_key_value)}"
                    cursor.execute(query)
                    db_connection.commit()
                    tree.set(item_id, columns[col_index], new_value)
                except Exception as e:
                    messagebox.showerror("Error", f"Error updating database: {e}")
                finally:
                    entry.destroy()
                    combo.set(selection)
                    combo.event_generate("<<ComboboxSelected>>")
                    return

            def close_entry(event=None):
                entry.destroy()

            entry.bind("<Return>", save_value)
            entry.bind("<FocusOut>", close_entry)
            entry.focus_set()

    def on_right_click(event):
        tree = event.widget
        item_id = tree.identify_row(event.y)
        column_id = tree.identify_column(event.x)
        if item_id and column_id.startswith("#"):
            col_index = int(column_id.lstrip("#")) - 1
            row_index = list(tree.get_children()).index(item_id)

            if row_index < 0 or row_index >= len(result):
                return

            row_values = result[row_index]
            value = row_values[col_index]

            def remove_row():
                confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this row?")
                if confirm:
                    try:
                        query = f"DELETE FROM {selection} WHERE {columns[col_index]} = {("'" + str(value) + "'") if column_types[col_index] != 'INTEGER' else int(value)}"
                        cursor.execute(query)
                        db_connection.commit()
                        tree.delete(item_id)
                        combo.set(selection)
                        combo.event_generate("<<ComboboxSelected>>")
                        return
                    except Exception as e:
                        messagebox.showerror("Error", f"Error deleting row: {e}")

            selected_item = tree.identify("item", event.x, event.y)
            tree.selection_set(selected_item)
            menu = tkinter.Menu(m, tearoff=0)
            menu.add_command(label="Remove row", command=remove_row)
            menu.post(event.x_root, event.y_root)

    for row in result:
        values = []
        for i, value in enumerate(row):
            if column_types[i] == "BLOB" and value:
                values.append("BLOB")
            else:
                values.append(value)

        tree.insert('', 'end', values=values, tags=[f'row_{row[0]}'])

    tree.pack(padx=0, pady=0, anchor='w')

    # bind the click event for handling blob files
    tree.bind("<Button-1>", on_cell_click)
    tree.bind("<Double-1>", on_cell_double_click)
    tree.bind("<Button-3>", on_right_click)

    insert_button = Button(label_treedata, text="+", command=lambda: insert_into_table(
    m, cursor, db_connection, combo, label_treedata
))
    insert_button.pack(side='top', anchor='w')


def switch_view(view):
    global m, nav_db_struct, nav_browse_data, nav_sql, label_sql, label_browse_data, label_db_struct
    match view:  # changing tabs
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
    global db_connection, cursor
    try:
        if os.path.exists("temp.db"):
            os.remove("temp.db")

        db_connection = sqlite3.connect("temp.db")
        cursor = db_connection.cursor()

        with open(sql_file, 'r') as f:
            sql = f.read()

        cursor.executescript(sql)
        db_connection.commit()

    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error creating database: {e}")


def create_db_from_xml(xml_file):
    global db_connection, cursor
    try:
        if os.path.exists("temp.db"):
            os.remove("temp.db")

        db_connection = sqlite3.connect("temp.db")
        cursor = db_connection.cursor()

        cursor.execute("PRAGMA foreign_keys = ON;")

        with open(xml_file, "r", encoding="utf-8") as f:
            content = f.read()

        # extracting data to the closing </dataset> tag
        if "</dataset>" in content:
            valid_xml = content.split("</dataset>")[0] + "</dataset>"
        else:
            raise et.ParseError("Missing closing </dataset> tag.")

        # ET parse the valid XML
        root = et.fromstring(valid_xml)

        relations = {}
        for relation in root.findall("relation"):
            table_name = relation.get("table")
            foreign_keys = []
            for fk in relation.findall("foreign_key"):
                column = fk.get("column")
                ref_table = fk.get("references_table")
                ref_column = fk.get("references_column")
                foreign_keys.append(f"FOREIGN KEY ({column}) REFERENCES {ref_table}({ref_column})")
            relations[table_name] = foreign_keys

        # create tables and insert data
        for table in root.findall("table"):
            table_name = table.get("name")

            # create table accordingly with schema
            schema = table.find("schema")
            columns = []
            for column in schema.findall("column"):
                col_name = column.get("name")
                col_type = column.get("type")
                is_pk = "PRIMARY KEY" if column.get("primary_key") == "1" else ""
                columns.append(f"{col_name} {col_type} {is_pk}".strip())

            # add foreign keys
            if table_name in relations:
                columns += relations[table_name]

            create_table_sql = f"CREATE TABLE {table_name} ({', '.join(columns)});"
            cursor.execute(create_table_sql)

            # insert table records
            data = table.find("data")
            if data is not None:
                for row in data.findall("record"):
                    col_names = []
                    col_values = []
                    for col in row:
                        col_names.append(col.tag)
                        encrypted = col.text
                        if encrypted:
                            # decode the Base64 
                            decoded = base64.b64decode(encrypted)
                            try:
                                decoded = decoded.decode('utf-8')
                            except UnicodeDecodeError:
                                pass
                            col_values.append(decoded)
                        else:
                            col_values.append(None)

                            # insert the decoded value into the database
                    insert_sql = f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES ({', '.join(['?' for _ in col_names])});"
                    cursor.execute(insert_sql, tuple(col_values))

        for view in root.findall("view"):
            view_definition = view.find("schema").text
            cursor.execute(view_definition)

        for trigger in root.findall("trigger"):
            trigger_definition = trigger.find("schema").text
            cursor.execute(trigger_definition)

        db_connection.commit()

    except sqlite3.Error as e:
        messagebox.showerror("Error", f"SQLite Error: {e}")
    except et.ParseError as e:
        messagebox.showerror("Error", f"XML Parse Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected Error: {e}")


def import_db(file_format):
    global db_connection, cursor, sql_input_textbox, sql_output_textbox, print_button, combo, m, label_treedata, result_label
    filetype = ""
    match file_format:
        case ".db":
            filetype = "SQLite Database"
        case ".sql":
            filetype = "SQL Database"
        case ".xml":
            filetype = "Extensible Markup Language File"

    db_path = filedialog.askopenfilename(
        title=f"Select a {file_format} file",
        filetypes=[(filetype, f"*{file_format}")]
    )

    if file_format == ".db":
        os.chmod(db_path, 0o666)  # asking for access to edit the .db file

    if db_path:
        try:
            if db_connection:
                db_connection.close()

            match file_format:
                case ".db":
                    db_connection = sqlite3.connect(db_path, check_same_thread=False, uri=True)
                case ".sql":
                    create_db_from_sql(db_path)
                case ".xml":
                    create_db_from_xml(db_path)

            cursor = db_connection.cursor()
            result = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [str(table[0]) for table in result.fetchall()]

            combo.set("Select table")
            combo.config(values=tables)

            m.title("SQLite Database Manager - " + str(db_path))  # config all necessary widgets
            print_button.pack(side='top', pady=5, anchor='w')
            sql_input_textbox.pack(side='top', pady=5, anchor='w', fill='x')
            result_label.pack(anchor='w', fill='both')
            children = result_label.winfo_children()
            if len(children) > 2:
                children[2].destroy()

            tree = ttk.Treeview(result_label, xscrollcommand=h3.set, yscrollcommand=v3.set)
            tree.pack(anchor='w', side='top', fill='both')
            sql_output_textbox.pack(side='top', pady=5, anchor='w', fill='both')
            combo.pack(side='top', pady=0, padx=0, anchor='w')
            label_treedata.pack(side='top', padx=0, pady=0, fill='both', expand=True)
            label_db_struct.config(bg='white')
            get_database_structure(
                m,
                db_connection,
                cursor,
                label_db_struct,
                h2,
                v2,
                create_table,
                remove_table,
                create_column,
                remove_column,
                combo,
                label_treedata,
            )
            children = label_treedata.winfo_children()
            if len(children) > 2:
                children[2].destroy()
                children[3].destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error connecting to database: {e}")


def import_table_from_csv():
    global db_connection, cursor, sql_input_textbox, sql_output_textbox, print_button, combo, m, label_treedata
    if not db_connection:
        messagebox.showerror("Error", "No database connection found.")
        return
    db_path = filedialog.askopenfilename(
        title="Select a .csv file",
        filetypes=[("Comma-Separated Values Files", "*.csv")]
    )
    if db_path:
        import_window = Toplevel(m)
        import_window.resizable(False, False)
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
                        cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns});')
                    else:
                        headers = [f"Column{i + 1}" for i in range(len(next(reader)))]
                        columns = ', '.join([f'"{header}" TEXT' for header in headers])
                        cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns});')
                        f.seek(0)

                    for row in reader:
                        placeholders = ', '.join(['?'] * len(row))
                        cursor.execute(f'INSERT INTO "{table_name}" VALUES ({placeholders});', row)

                    db_connection.commit()
                    messagebox.showinfo("Success", f"Data imported into table '{table_name}'.")

                    result = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [str(table[0]) for table in result.fetchall()]
                    combo.config(values=tables)

                    get_database_structure(
                        m,
                        db_connection,
                        cursor,
                        label_db_struct,
                        h2,
                        v2,
                        create_table,
                        remove_table,
                        create_column,
                        remove_column,
                        combo,
                        label_treedata,
                    )

            except Exception as e:
                messagebox.showerror("Error", f"Error importing CSV data: {e}")

            import_window.destroy()

        Button(import_window, text="Import", command=start_import).grid(row=4, columnspan=2)


def execute_query():
    global h3, v3
    if db_connection:
        query = sql_input_textbox.get(1.0, "end-1c").strip()
        if not query or query == "":
            messagebox.showerror("Error", "No query typed in")
            return
        try:
            if "blob(" in query.lower():
                start = query.lower().find("blob(") + 5
                end = query.lower().find(")", start)
                if start > 0 and end > 0:
                    image_path = query[start + 1: end - 1]
                    if os.path.exists(image_path):
                        with open(image_path, "rb") as file:
                            blob_data = file.read()

                        new_query = query[:start - 5] + f"X'{blob_data.hex()}'" + query[end + 1:]

                    else:
                        messagebox.showerror("Error", f"Image file not found: {image_path}")
                        return
                else:
                    messagebox.showerror("Error", "Invalid BLOB function or image path in query.")
                    return

                cursor.execute(new_query)
            else:
                cursor.execute(query)
            # checking if it's a select query to create treeview displaying the output
            if query.lower().startswith("select"):
                result = cursor.fetchall()

                # clearing existing view if there is any
                for child in result_label.winfo_children():
                    child.destroy()

                if result:
                    sql_output_textbox.config(state='normal')
                    sql_output_textbox.delete(1.0, "end")
                    sql_output_textbox.insert("insert", f"Execution finished without errors.\n{query}\n")
                    sql_output_textbox.config(state='disabled')

                    columns = [desc[0] for desc in cursor.description]
                    column_types = [desc[2] for desc in
                                    cursor.execute(f"PRAGMA table_info({query.split('FROM ')[1].split()[0]})")]

                    tree = ttk.Treeview(result_label, xscrollcommand=h3.set, yscrollcommand=v3.set)
                    tree["show"] = "headings"
                    tree["columns"] = columns

                    for col in columns:
                        tree.heading(col, text=col, anchor="center")
                        tree.column(col, width=100, anchor="center", stretch=False)

                    for row in result:
                        values = []
                        i = 0
                        for i, value in enumerate(row):
                            if column_types[i] == "BLOB" and value:
                                values.append("BLOB")
                            else:
                                values.append(value)
                        tree.insert('', 'end', values=values, tags=[f'row_{i}_{row[0]}'])

                    def on_cell_click(event):
                        # get the clicked item (row) and column
                        tree = event.widget
                        item_id = tree.identify_row(event.y)
                        column_id = tree.identify_column(event.x)

                        if item_id and column_id:
                            # get the column index and row index
                            col_index = int(column_id[1:]) - 1
                            row_index = int(item_id[1:]) - 1
                            if row_index < 0 or row_index >= len(result):
                                return

                                # get the data from the clicked row and column
                            row_values = result[row_index]
                            value = row_values[col_index]

                            if column_types[col_index] == "BLOB":  # if it was blob then download it
                                download_blob(value)

                    tree.grid(row=0, column=0, sticky="nsew")
                    tree.bind("<Button-1>", on_cell_click)

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
            else:  # for other queries
                for child in result_label.winfo_children():
                    child.destroy()
                db_connection.commit()
                get_database_structure(
                    m,
                    db_connection,
                    cursor,
                    label_db_struct,
                    h2,
                    v2,
                    create_table,
                    remove_table,
                    create_column,
                    remove_column,
                    combo,
                    label_treedata,
                )
                sql_output_textbox.config(state='normal')
                sql_output_textbox.delete(1.0, "end")
                sql_output_textbox.insert("insert", f"Execution finished without errors.\nAt line 1:\n{query}\n")
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
filemenu.add_command(label="Open Database", command=lambda: import_db(".db"))
menuBar.add_cascade(label="File", menu=filemenu)

importmenu = Menu(menuBar, tearoff=0)

database_submenu = Menu(importmenu, tearoff=0)
database_submenu.add_command(label="From SQL File", command=lambda: import_db(".sql"))
database_submenu.add_command(label="From XML File", command=lambda: import_db(".xml"))

importmenu.add_cascade(label="Database", menu=database_submenu)

table_submenu = Menu(importmenu, tearoff=0)
table_submenu.add_command(label="From CSV File", command=import_table_from_csv)

importmenu.add_cascade(label="Table", menu=table_submenu)
menuBar.add_cascade(label="Import", menu=importmenu)

exportmenu = Menu(menuBar, tearoff=0)

exportmenu.add_command(label="Database", command=lambda: export_db(db_connection, cursor, m))

export_submenu = Menu(exportmenu, tearoff=0)
export_submenu.add_command(label="To CSV File", command=lambda: export_table_to_csv(db_connection, cursor, m))
export_submenu.add_command(label="To JSON File", command=lambda: export_table_to_json(db_connection, cursor, m))

exportmenu.add_cascade(label="Table", menu=export_submenu)

menuBar.add_cascade(label="Export", menu=exportmenu)

m.config(menu=menuBar)

navbar = tkinter.Frame(m, bg='lightgray', padx=5, pady=0)
navbar.pack(fill='x', side='top')

nav_db_struct = tkinter.Button(navbar, text="Database structure", borderwidth=0, relief="flat", bg=m.cget("bg"),
                               command=lambda: switch_view("1"))
nav_db_struct.pack(side="left")


def on_right_click(event):
    menu = tkinter.Menu(m, tearoff=0)
    menu.add_command(label="Refresh", command=get_database_structure(
                    m,
                    db_connection,
                    cursor,
                    label_db_struct,
                    h2,
                    v2,
                    create_table,
                    remove_table,
                    create_column,
                    remove_column,
                    combo,
                    label_treedata,
                ))
    menu.post(event.x_root, event.y_root)


nav_db_struct.bind("<Button-3>", on_right_click)

nav_browse_data = tkinter.Button(navbar, text="Browse data", borderwidth=0, relief="flat", bg='lightgray',
                                 command=lambda: switch_view("2"))
nav_browse_data.pack(side="left")

nav_sql = tkinter.Button(navbar, text="Execute SQL", borderwidth=0, relief="flat", bg='lightgray',
                         command=lambda: switch_view("3"))
nav_sql.pack(side="left")

label_sql = tkinter.Frame(m, padx=0, pady=0)

label_db_struct = tkinter.Frame(m, padx=0, pady=0)
label_db_struct.pack(side='left', fill='both', expand=True)

label_browse_data = tkinter.Frame(m, padx=0, pady=0)
label_treedata = tkinter.Frame(label_browse_data, bg="white", padx=0, pady=0)

h1 = tkinter.Scrollbar(label_treedata, orient='horizontal')
h1.pack(side=BOTTOM, fill=X)
v1 = tkinter.Scrollbar(label_treedata)
v1.pack(side=RIGHT, fill=Y)

h2 = tkinter.Scrollbar(label_db_struct, orient='horizontal')
h2.pack(side=BOTTOM, fill=X)
v2 = tkinter.Scrollbar(label_db_struct)
v2.pack(side=RIGHT, fill=Y)

sql_input_textbox = tkinter.Text(label_sql, height=5, width=50)
sql_output_textbox = tkinter.Text(label_sql, width=50)
result_label = tkinter.Frame(label_sql, width=50, height=5, bg='white')

h3 = tkinter.Scrollbar(result_label, orient='horizontal')
h3.pack(side=BOTTOM, fill=X)
v3 = tkinter.Scrollbar(result_label)
v3.pack(side=RIGHT, fill=Y)

print_button = tkinter.Button(label_sql, text="Execute Query", command=execute_query)

combo = ttk.Combobox(
    label_browse_data,
    state="readonly"
)
combo.bind("<<ComboboxSelected>>", switch_tables)

m.mainloop()
