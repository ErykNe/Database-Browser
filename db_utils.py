import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3


def create_column(m, table_name, cursor, db_connection, combo, label_treedata, get_database_structure):
    create_column_window = Toplevel(m)
    create_column_window.title("Create Column")
    create_column_window.resizable(False, False)

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

            cursor.execute(query)
            db_connection.commit()
            get_database_structure()
            messagebox.showinfo("Success", f"Column '{column_name}' added to table '{table_name}'.")
            create_column_window.destroy()
            combo.set("Select table")
            children = label_treedata.winfo_children()
            if len(children) > 2:
                children[2].destroy()
                children[3].destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add column: {e}")

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

    Button(create_column_window, text="Create Column", command=lambda: create_column_in_db(table_name, variables)).pack(
        side='left', padx=5, pady=10, anchor='n')


def create_table(m, cursor, db_connection, combo, get_database_structure):
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
    widget_refs = []
    variables_refs = []

    def add_row():
        row_id = tree.insert('', 'end', values=["" for _ in columns])
        row_widgets = []
        variables = []
        for col_index, col_name in enumerate(columns):
            x, y, width, height = tree.bbox(row_id, f"#{col_index + 1}")
            if col_name == 'Type':
                var = StringVar()
                widget = ttk.Combobox(create_window, textvariable=var,
                                      values=["INTEGER", "TEXT", "BLOB", "REAL", "NUMERIC"])
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
        widget_refs.append(row_widgets)
        variables_refs.append(variables)

    def remove_row():
        selected_item = tree.selection()
        if selected_item:
            tree.delete(selected_item)
            for idx, widgets in enumerate(widget_refs):
                if tree.get_children()[idx] == selected_item[0]:
                    for widget in widgets:
                        widget.destroy()
                    widget_refs.pop(idx)
                    variables_refs.pop(idx)
                    break
        elif tree.get_children():
            last_item = tree.get_children()[-1]
            tree.delete(last_item)
            widgets = widget_refs.pop()
            variables_refs.pop()
            for widget in widgets:
                widget.destroy()

    def execute_create_table_query():
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
        try:
            cursor.execute(query)
            db_connection.commit()
            messagebox.showinfo("Success", f"Successfully created table '{delimiter_entry.get()}'.")
            combo['values'] = list(combo['values'] + [delimiter_entry.get()])
            create_window.destroy()
            get_database_structure()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error creating table: {e}")

    tree.pack(anchor='w', fill='x')
    Button(create_window, text="Add Row", command=add_row).pack(side='left', padx=5, pady=5, anchor='n')
    Button(create_window, text="Remove Row", command=remove_row).pack(side='left', padx=5, pady=5, anchor='n')
    Button(create_window, text="Create Table", command=execute_create_table_query).pack(side='left', padx=5, pady=5,
                                                                                        anchor='n')


def remove_table(cursor, db_connection, table_name, combo, label_treedata, get_database_structure):
    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the table '{table_name}'?")
    if confirm:
        try:
            query = f"DROP TABLE {table_name}"
            cursor.execute(query)
            db_connection.commit()
            get_database_structure()
            result = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [str(table[0]) for table in result.fetchall()]
            combo.set("Select table")
            combo.config(values=tables)
            children = label_treedata.winfo_children()
            if len(children) > 2:
                children[2].destroy()
                children[3].destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting table: {e}")


def remove_column(cursor, db_connection, table_name, column_name, combo, label_treedata, get_database_structure):
    confirm = messagebox.askyesno("Confirm Deletion",
                                  f"Are you sure you want to delete the column '{column_name}' from table '{table_name}'?")
    if confirm:
        try:
            query = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
            cursor.execute(query)
            db_connection.commit()
            get_database_structure()
            result = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [str(table[0]) for table in result.fetchall()]
            combo.set("Select table")
            combo.config(values=tables)
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting column: {e}")


def insert_into_table(m, cursor, db_connection, combo, label_treedata):
    selected_table = combo.get()
    if not selected_table or selected_table == "Select table":
        messagebox.showerror("Error", "Please select a table.")
        return

    insert_window = Toplevel(m)
    insert_window.title(f"Insert into {selected_table}")
    insert_window.resizable(False, False)

    cursor.execute(f"PRAGMA table_info({selected_table})")
    columns = cursor.fetchall()

    entries = {}
    columns_per_row = 3
    for i, column in enumerate(columns):
        col_name = column[1]
        row_pos = i // columns_per_row
        col_pos = (i % columns_per_row) * 2
        Label(insert_window, text=col_name).grid(column=col_pos, row=row_pos, padx=5, pady=5)
        entry = Entry(insert_window)
        entry.grid(column=col_pos + 1, row=row_pos, padx=5, pady=5)
        entries[col_name] = entry

    def insert_record():
        values = {col: entry.get() for col, entry in entries.items()}
        columns_str = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        query = f"INSERT INTO {selected_table} ({columns_str}) VALUES ({placeholders})"
        try:
            cursor.execute(query, list(values.values()))
            db_connection.commit()
            messagebox.showinfo("Success", "Record inserted successfully.")
            insert_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to insert record: {e}")

    Button(insert_window, text="Insert", command=insert_record, width=7).grid(column=0, row=columns_per_row)


def get_database_structure(
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
        insert_into_table_func=None
):
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

    longest_schema_length = 0

    tree.tag_configure("underline", font=("", 9, "underline"))

    table_node = tree.insert("", "end", text="Tables", open=True, tags=("table_node",))

    query_table_names = "SELECT name, type, sql FROM sqlite_master WHERE type='table'"
    tables = cursor.execute(query_table_names).fetchall()
    db_connection.commit()

    for table in tables:
        name = str(table[0])
        schema = str(table[2]).replace("\n", " ")
        if longest_schema_length < len(schema):
            longest_schema_length = len(schema)
        table_item = tree.insert(table_node, "end", text=name, open=False, values=("", schema), tags=("table",))
        table_info = f"PRAGMA table_info({name});"
        table_struct = cursor.execute(table_info).fetchall()
        db_connection.commit()
        for struct in table_struct:
            result = f'"{struct[1]}" {struct[2]} {"NOT NULL " if struct[3] == 1 else ""} {"PRIMARY KEY" if struct[5] == 1 else ""}'
            column_item = tree.insert(table_item, "end", text=str(struct[1]), values=(str(struct[2]), result),
                                      tags=("column",))
            if struct[5] == 1:
                tree.item(column_item, tags=("column", "underline"))

    view_node = tree.insert("", "end", text="Views", open=True, tags=("view_node",))
    query_view_names = "SELECT name, type, sql FROM sqlite_master WHERE type='view'"
    views = cursor.execute(query_view_names).fetchall()
    db_connection.commit()

    for view in views:
        name = str(view[0])
        schema = str(view[2]).replace("\n", " ")
        if longest_schema_length < len(schema):
            longest_schema_length = len(schema)
        tree.insert(view_node, "end", text=name, open=False, values=("", schema), tags=("view",))

    trigger_node = tree.insert("", "end", text="Triggers", open=True, tags=("trigger_node",))
    query_triggers_names = "SELECT name, type, sql FROM sqlite_master WHERE type='trigger'"
    triggers = cursor.execute(query_triggers_names).fetchall()
    db_connection.commit()

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

    def right_click(event):
        selected_item = tree.identify("item", event.x, event.y)
        selected_tags = tree.item(selected_item, "tags")
        if "table_node" in selected_tags:
            tree.selection_set(selected_item)
            menu = tkinter.Menu(m, tearoff=0)
            menu.add_command(
                label="Add Table",
                command=lambda: create_table(
                    m,
                    cursor,
                    db_connection,
                    combo,
                    lambda: get_database_structure(
                        m, db_connection, cursor, label_db_struct, h2, v2,
                        create_table, remove_table, create_column, remove_column, combo, label_treedata,
                        insert_into_table_func
                    )
                )
            )
            menu.post(event.x_root, event.y_root)
        elif "table" in selected_tags:
            tree.selection_set(selected_item)
            table_name = tree.item(selected_item, "text")
            menu = tkinter.Menu(m, tearoff=0)
            menu.add_command(
                label="Remove Table",
                command=lambda: remove_table(
                    cursor, db_connection, table_name, combo, label_treedata,
                    lambda: get_database_structure(
                        m, db_connection, cursor, label_db_struct, h2, v2,
                        create_table, remove_table, create_column, remove_column, combo, label_treedata,
                        insert_into_table_func
                    )
                )
            )
            menu.add_command(
                label="Add Column",
                command=lambda: create_column(
                    m,
                    table_name,
                    cursor,
                    db_connection,
                    combo,
                    label_treedata,
                    lambda: get_database_structure(
                        m, db_connection, cursor, label_db_struct, h2, v2,
                        create_table, remove_table, create_column, remove_column, combo, label_treedata,
                        insert_into_table_func
                    )
                )
            )
            menu.post(event.x_root, event.y_root)
        elif "column" in selected_tags:
            tree.selection_set(selected_item)
            table_name = tree.item(tree.parent(selected_item), "text")
            column_name = tree.item(selected_item, "text")
            menu = tkinter.Menu(m, tearoff=0)
            menu.add_command(
                label="Remove Column",
                command=lambda: remove_column(
                    cursor,
                    db_connection,
                    table_name,
                    column_name,
                    combo,
                    label_treedata,
                    lambda: get_database_structure(
                        m, db_connection, cursor, label_db_struct, h2, v2,
                        create_table, remove_table, create_column, remove_column, combo, label_treedata,
                        insert_into_table_func
                    )
                )
            )
            menu.post(event.x_root, event.y_root)

    tree.bind("<Button-3>", right_click)