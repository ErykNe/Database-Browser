# Database Browser

A GUI application to browse, analyze, and manipulate data in SQLite databases.  
Built entirely in Python with Tkinter for the interface, this tool allows users to visually interact with SQLite databases, import/export data, and perform common database operations with ease.

![db-browser](https://github.com/user-attachments/assets/d5ea1280-aa96-4d25-926b-dcffd8a0c3be)

---

## Features

- **Browse Database Structure:** View tables, views, triggers, and schemas.
- **Table Management:** Create, edit, and delete tables and columns.
- **Data Manipulation:** Insert, update, and delete records from tables via GUI.
- **Import/Export:**
  - Import databases from `.db`, `.sql`, or `.xml` files.
  - Import tables from `.csv` files.
  - Export tables to `.csv` or `.json`.
  - Export entire database to `.db`, `.sql`, or `.xml`.
- **SQL Execution:** Run custom SQL queries and view results directly in the app.
- **BLOB Support:** Download and save BLOB data from tables (e.g., images, files).
- **Multiple File Encodings:** Choose encoding when importing/exporting data.

---

## Requirements

- Python 3.13 or newer is recommended.
- Standard Python libraries: `tkinter`, `sqlite3`, `csv`, `json`, `os`, `base64`, `xml.etree.ElementTree`.
  
---

## How to Run

```sh
python main.py
```
