import os
import base64
import sqlite3
from tkinter import Toplevel, LabelFrame, Label, StringVar, Entry, filedialog, messagebox, ttk, BooleanVar, Checkbutton, \
    Button


def export_db(db_connection, kursor, m):
    if not db_connection:
        messagebox.showerror("Error", "No connection identified")
        return

    export_window = Toplevel(m)
    export_window.title("Export database")
    export_window.geometry("650x270")
    export_window.resizable(False, False)

    # File Details Frame
    label_frame = LabelFrame(export_window, text="File Details: ")
    label_frame.pack(fill='x', padx=10, pady=10)

    file_name_label = Label(label_frame, text="File name:")
    file_name_label.pack(side='left', padx=10, pady=10, anchor='n')
    file_name_var = StringVar(value="database")
    name_entry = Entry(label_frame, textvariable=file_name_var)
    name_entry.pack(side='left', padx=10, pady=10, anchor='n')

    file_src_label = Label(label_frame, text="File path:")
    file_src_label.pack(side='left', padx=10, pady=10, anchor='n')

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")  # set the deafult path to desktop

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

    path_combobox.set(desktop_path)  # set the deafult path to desktop

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
        if not kursor:
            messagebox.showerror("Error", "Database connection is not established.")
            return

        db_file_path = os.path.join(selected_path, f"{file_name}.db")

        try:

            new_connection = sqlite3.connect(db_file_path)  # opening new connection to write the .db file
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
        if not kursor:
            messagebox.showerror("Error", "Database connection is not established.")
            return

        sql_file_path = os.path.join(selected_path, f"{file_name}.sql")

        try:
            # writing the .sql file using built-in .dump method
            with open(sql_file_path, 'w') as sql_file:
                for line in db_connection.iterdump():
                    sql_file.write(f"{line}\n")

        except Exception as e:  # handling errors
            messagebox.showerror("Error", f"Failed to export to SQL file: {str(e)}")

    def export_db_to_xml_file(file_name, selected_path):
        if not kursor:
            messagebox.showerror("Error", "Database connection is not established.")
            return
        xml_file_path = os.path.join(selected_path, f"{file_name}.xml")
        try:
            # open XML file to write data
            with open(xml_file_path, 'w', encoding='utf-8') as xml_file:
                xml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                xml_file.write('<dataset>\n')

                kursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = kursor.fetchall()

                for table in tables:
                    table_name = table[0]
                    xml_file.write(f'  <table name="{table_name}">\n')

                    kursor.execute(f"PRAGMA table_info({table_name});")
                    columns = kursor.fetchall()

                    # write table schema (datatypes)
                    xml_file.write('    <schema>\n')
                    for column in columns:
                        column_name = column[1]
                        column_type = column[2]
                        pk = column[5]
                        xml_file.write(
                            f'      <column name="{column_name}" type="{column_type}" primary_key="{pk}" />\n')
                    xml_file.write('    </schema>\n')

                    # write tables
                    kursor.execute(f"SELECT * FROM {table_name};")
                    rows = kursor.fetchall()
                    column_names = [column[1] for column in columns]
                    xml_file.write('    <data>\n')
                    for row in rows:
                        xml_file.write('      <record>\n')
                        for column_name, value in zip(column_names, row):
                            # encode data
                            if value is not None:
                                if isinstance(value, bytes):  # check if it's a BLOB
                                    # encode the BLOB
                                    encoded = base64.b64encode(value).decode('utf-8')
                                else:
                                    # encode the other data
                                    encoded = base64.b64encode(str(value).encode('utf-8')).decode('utf-8')
                                xml_file.write(f'        <{column_name}>{encoded}</{column_name}>\n')
                            else:
                                xml_file.write(f'        <{column_name}></{column_name}>\n')
                        xml_file.write('      </record>\n')
                    xml_file.write('    </data>\n')

                    xml_file.write('  </table>\n')

                # export views
                kursor.execute("SELECT name, sql FROM sqlite_master WHERE type='view';")
                views = kursor.fetchall()

                for view in views:
                    view_name, view_sql = view
                    xml_file.write(f'  <view name="{view_name}">\n')
                    xml_file.write(f'    <schema>{view_sql}</schema>\n')
                    xml_file.write('  </view>\n')

                # exporting triggers
                kursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger';")
                triggers = kursor.fetchall()
                for trigger in triggers:
                    trigger_name, trigger_sql = trigger
                    xml_file.write(f'  <trigger name="{trigger_name}">\n')
                    xml_file.write(f'    <schema>{trigger_sql}</schema>\n')
                    xml_file.write('  </trigger>\n')

                # export relationships (foreign keys)
                for table in tables:
                    table_name = table[0]
                    kursor.execute(f"PRAGMA foreign_key_list({table_name});")
                    foreign_keys = kursor.fetchall()
                    if foreign_keys:
                        xml_file.write(f'  <relation table="{table_name}">\n')
                        for fk in foreign_keys:
                            xml_file.write(
                                f'    <foreign_key column="{fk[3]}" references_table="{fk[2]}" references_column="{fk[4]}" />\n'
                            )
                        xml_file.write('  </relation>\n')

                xml_file.write('</dataset>\n')

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

        for file_type in file_types:
            match file_type:  # exporting files depending on what the user has selected
                case '.db':
                    export_db_to_db_file(file_name, selected_path)
                case '.sql':
                    export_db_to_sql_file(file_name, selected_path)
                case '.xml':
                    export_db_to_xml_file(file_name, selected_path)
        messagebox.showinfo("Success",
                            f"Database exported to:\n{os.path.join(selected_path, file_name)}\nFile types: {selected_types}")

    export_button = Button(export_window, text="Export", command=confirm_export, width=18)
    export_button.pack(pady=20, padx=10, side='left', anchor='n')
