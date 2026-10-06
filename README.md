# Employee Manager

A command-line employee management application written in Python.

The application allows users to add employees, view complete records, edit employee details, search and filter records, and sort results through an interactive terminal menu.

Employee data is stored locally in JSON format and remains available after the application is closed and restarted.

The project was created as a practical Python exercise focused on data structures, input validation, dates, persistent storage, text processing, and sorting.

The application interface is in Polish. This README describes its features and usage in English.

---

## Features

The application currently supports:

- adding employees,
- displaying complete employee records,
- editing employee details,
- assigning permanent unique employee IDs,
- storing address details in separate fields,
- calculating a medical examination expiry date,
- searching by employee ID and name,
- combining multiple filters,
- sorting text, numbers, and dates in both directions,
- browsing search results in pages of 10,
- opening a complete record directly from search results,
- saving and loading records using JSON,
- keeping a backup of the previous save,
- validating user input and stored data.

---

## Employee Records

Each employee is stored as a dictionary.

| Field | Required when adding an employee | Editable |
| --- | --- | --- |
| ID | Assigned automatically | No |
| First name | Yes | No |
| Surname | Yes | Yes |
| Job title | Yes | Yes |
| Department | Yes | Yes |
| Street | No | Yes |
| House number | No | Yes |
| Apartment number | No | Yes |
| Postal code | No | Yes |
| City | No | Yes |
| Country | No | Yes |
| Email | No | Yes |
| Phone number | No | Yes |
| Hire date | Yes | Yes |
| Medical examination expiry date | Calculated automatically | Recalculated when the hire date changes |

Phone numbers, postal codes, and address numbers are stored as strings. This preserves leading zeros and characters such as `+`.

Employee IDs are generated using a separate `next_id` counter. An ID identifies a record independently of its position in a list or search result.

---

## Editing Records

Employees are selected for editing by ID.

During editing:

- current values are displayed,
- pressing Enter keeps the current value,
- entering `-` clears an optional field,
- required fields cannot be cleared,
- the first name and ID remain fixed,
- changing the hire date recalculates the medical examination expiry date.

Changes are accepted only after the updated database has been successfully saved.

---

## Medical Examination Validity

The application uses a simplified project rule: medical examinations are valid for one calendar year from the hire date.

Dates use the `YYYY-MM-DD` format.

| Hire date | Calculated expiry date |
| --- | --- |
| 2026-01-15 | 2027-01-15 |
| 2024-02-29 | 2025-02-28 |

For February 29, the application uses February 28 of the following year.

The expiry date is calculated automatically and cannot be edited directly. This rule is a demonstration assumption for the project.

---

## Searching and Filtering

Users can search by:

- exact employee ID,
- fragments of first name and surname.

Additional filters are available for:

- department,
- job title,
- city,
- country.

Pressing Enter skips an optional search criterion.

All supplied criteria must match at the same time.

Text matching ignores letter case and diacritics. For example, searching for `lodz` matches `Łódź`.

---

## Sorting

Available sort fields include:

- surname,
- first name,
- employee ID,
- department,
- job title,
- city,
- hire date,
- medical examination expiry date.

Sorting supports:

- ascending and descending text order,
- numerical ordering of IDs,
- oldest-first and newest-first date ordering,
- Polish alphabetical order,
- empty values placed last in either direction.

Surname, first name, and ID provide a consistent secondary order when primary values are equal.

The default sort order is surname in ascending order.

---

## Result Pagination

Search results are displayed in pages of 10 employees.

| Input | Action |
| --- | --- |
| `n` | Display the next page |
| `p` | Display the previous page |
| `0` | Return to the main menu |
| An employee ID | Display the complete record for an employee in the results |

Pagination keeps larger result lists readable without changing the stored records.

---

## JSON Persistence

Employee data is stored locally in:

`data/employees.json`

The application loads the database on startup and saves changes after successfully adding or editing an employee.

On the first run, a missing database starts with an empty employee list. The `data` directory and database file are created after the first successful addition.

File paths are resolved relative to `main.py`, so the data location does not depend on the terminal's current working directory.

### Saving and Backups

Before replacing the database, the application:

1. validates the proposed data,
2. writes it to a temporary file in the data directory,
3. keeps the previous database as `data/employees.json.bak`, if it exists,
4. replaces the database with the completed temporary file.

The backup contains the previous saved version. It is not imported automatically.

If the database is missing but a backup exists, startup stops with a message so the user can inspect the files.

---

## Data Structure

The database contains:

- a schema version,
- the next available employee ID,
- a list of employee records.

Example with fictional data:

```json
{
    "schema_version": 1,
    "next_id": 2,
    "employees": [
        {
            "id": 1,
            "first_name": "Anna",
            "last_name": "Nowak",
            "job_title": "Python Developer",
            "department": "IT",
            "street": "Przykładowa",
            "house_number": "1A",
            "apartment_number": "2",
            "postal_code": "90-001",
            "city": "Łódź",
            "country": "Polska",
            "email": "anna.nowak@example.com",
            "phone": "",
            "hire_date": "2026-01-15",
            "medical_exam_valid_until": "2027-01-15"
        }
    ]
}
```

An additional fictional example is included in `examples/employees.example.json`.

The application does not import that example file automatically.

---

## Input and JSON Validation

User input is checked before modifying a record.

Validation includes:

- non-empty required fields,
- valid calendar dates in `YYYY-MM-DD` format,
- positive numeric employee IDs,
- valid menu selections.

Hire dates must have a year no greater than 9998 so the following year's expiry date can be calculated.

Loaded JSON is also validated before it is accepted.

The application checks:

- the database root structure,
- the supported schema version,
- the employee list,
- positive and unique IDs,
- required employee fields and string values,
- consistency between the hire date and calculated expiry date,
- consistency between existing IDs and `next_id`.

Invalid JSON or an incompatible database structure stops startup with an explanatory message. The application does not replace invalid stored data with an empty database.

---

## Data Privacy

The local `data/` directory is excluded from Git through `.gitignore`.

This keeps employee records and local backup files outside the repository.

The virtual environment and Python cache files are also excluded.

The committed example contains fictional records. Each user maintains their own local database when running the application.

---

## Interactive Menu

The application is controlled through a terminal menu.

The Polish menu options perform the following actions:

| Option | Action |
| --- | --- |
| 1 | Add an employee |
| 2 | Display all employee records |
| 3 | Edit an employee by ID |
| 4 | Search, filter, and sort employees |
| 0 | Exit |

Employee information can be managed through the application without editing Python code or JSON files manually.

---

## Project Structure

| File | Purpose |
| --- | --- |
| `main.py` | Application logic, terminal interface, validation, and JSON storage |
| `README.md` | Project overview and usage instructions |
| `.gitignore` | Excludes local data, the virtual environment, and generated files |
| `examples/employees.example.json` | Fictional records demonstrating the database format |

The current version keeps the application in one Python file, with responsibilities organized into functions.

---

## Core Functions

| Function | Responsibility |
| --- | --- |
| `add_employee()` | Creates a record, assigns its ID, and saves the proposed database |
| `edit_employee()` | Updates editable fields and recalculates the expiry date |
| `show_employees()` | Displays complete employee records |
| `calculate_medical_expiry()` | Calculates the next calendar-year anniversary |
| `filter_employees()` | Applies ID, name, and additional text criteria |
| `sort_employees()` | Sorts results using the selected field and direction |
| `show_search_results()` | Controls pagination and record selection |
| `load_database()` | Loads and validates stored JSON |
| `save_database()` | Writes validated data and keeps the previous save |
| `commit_database()` | Updates the active in-memory database after a successful save |
| `main()` | Loads the database and runs the main menu loop |

---

## Requirements

- Python 3.12 or newer.
- A terminal for running the application.

The application uses only the Python standard library. No third-party packages or `pip install` step are required.

---

## Installation

Clone the repository and enter its directory:

```bash
git clone https://github.com/arielprofi995/employee-manager.git
cd employee-manager
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

If the project and virtual environment already exist, open the project directory and activate the existing environment.

---

## Running the Application

With the virtual environment active, run:

```bash
python main.py
```

The application loads existing employee data and displays the main menu.

A freshly cloned repository can start without a manually prepared database.

---

## Verified Behavior

Project checks covered:

- adding and editing records,
- saving and loading data after restarting the application,
- calculating the expiry date for February 29,
- rejecting invalid database contents,
- combining search criteria,
- sorting in both directions,
- navigating result pages.

---

## Technologies

- Python
- JSON
- Visual Studio Code
- Git
- GitHub
- macOS

---

## Python Concepts Practiced

This project demonstrates practical use of:

- functions, parameters, and return values,
- dictionaries, lists, sets, and tuples,
- loops and conditional statements,
- user input validation,
- exceptions and error handling,
- calendar dates,
- file paths and UTF-8 file handling,
- JSON serialization and deserialization,
- temporary files and file replacement,
- copying data with `deepcopy()`,
- Unicode normalization,
- custom sort keys and stable sorting,
- list slicing and pagination,
- virtual environments,
- project documentation and Git.

---

## Design Decisions

### Fixed IDs and First Names

IDs identify employee records and remain unchanged. Keeping the first name fixed is an explicit rule of this project's current scope.

### Calculated Expiry Dates

The medical examination expiry date is derived from the hire date rather than entered separately. This keeps both dates consistent.

### Candidate Changes Before Saving

Adding and editing operate on a copy of the database. The active in-memory data is updated only after saving succeeds.

### Local JSON Storage

JSON keeps the storage format readable and supports persistence without an external database server.

The application is intended for local use by one running process at a time.

---

## Future Improvements

Version 1.0.0 covers the current completed scope.

Possible future extensions include:

- indicators for expired or approaching examination dates,
- employee archiving,
- splitting the application into separate modules,
- SQLite storage,
- a graphical interface.

---

## Educational and Portfolio Purpose

This project was created for educational and portfolio purposes.

Its goal is to demonstrate employee record management, validation, persistent storage, searching, filtering, sorting, and practical Python application development.
