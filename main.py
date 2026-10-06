import json
import os
import shutil
import tempfile
import unicodedata
from copy import deepcopy
from datetime import date
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent / "data" / "employees.json"
BACKUP_FILE = DATA_FILE.with_suffix(".json.bak")

EMPLOYEE_FIELDS = {
    "first_name": "Imię",
    "last_name": "Nazwisko",
    "job_title": "Stanowisko",
    "department": "Dział",
    "street": "Ulica",
    "house_number": "Numer domu",
    "apartment_number": "Numer lokalu",
    "postal_code": "Kod pocztowy",
    "city": "Miasto",
    "country": "Kraj",
    "email": "E-mail",
    "phone": "Numer telefonu",
    "hire_date": "Data zatrudnienia (RRRR-MM-DD)",
}

REQUIRED_FIELDS = (
    "first_name", "last_name", "job_title", "department", "hire_date"
)
IMMUTABLE_FIELDS = ("id", "first_name", "medical_exam_valid_until")

FILTER_FIELDS = {
    "department": "Dział",
    "job_title": "Stanowisko",
    "city": "Miasto",
    "country": "Kraj",
}
SORT_OPTIONS = {
    "1": ("last_name", "Nazwisko"),
    "2": ("first_name", "Imię"),
    "3": ("id", "ID"),
    "4": ("department", "Dział"),
    "5": ("job_title", "Stanowisko"),
    "6": ("city", "Miasto"),
    "7": ("hire_date", "Data zatrudnienia"),
    "8": ("medical_exam_valid_until", "Termin badań"),
}
PAGE_SIZE = 10
POLISH_ALPHABET = "aąbcćdeęfghijklłmnńoópqrsśtuvwxyzźż"
LETTER_ORDER = {
    letter: index
    for index, letter in enumerate(" -\'0123456789" + POLISH_ALPHABET)
}


def parse_hire_date(value):
    parsed_date = date.fromisoformat(value)
    if parsed_date.isoformat() != value or parsed_date.year == 9999:
        raise ValueError("Użyj daty RRRR-MM-DD z rokiem nie większym niż 9998.")
    return parsed_date


def calculate_medical_expiry(hire_date):
    start = parse_hire_date(hire_date)
    day = 28 if start.month == 2 and start.day == 29 else start.day
    return start.replace(year=start.year + 1, day=day).isoformat()


def validate_database(database):
    if not isinstance(database, dict):
        raise ValueError("Baza musi zawierać obiekt JSON.")
    if type(database.get("schema_version")) is not int or database["schema_version"] != 1:
        raise ValueError("Nieobsługiwana wersja bazy.")
    if type(database.get("next_id")) is not int or database["next_id"] < 1:
        raise ValueError("Nieprawidłowy licznik ID.")
    if not isinstance(database.get("employees"), list):
        raise ValueError("Brakuje listy pracowników.")

    used_ids = set()
    for employee in database["employees"]:
        if not isinstance(employee, dict):
            raise ValueError("Nieprawidłowy wpis pracownika.")

        employee_id = employee.get("id")
        if type(employee_id) is not int or employee_id < 1 or employee_id in used_ids:
            raise ValueError("ID muszą być dodatnie i unikalne.")
        used_ids.add(employee_id)

        for field in EMPLOYEE_FIELDS:
            value = employee.get(field)
            if not isinstance(value, str):
                raise ValueError(f"Nieprawidłowe pole: {field}.")
            if field in REQUIRED_FIELDS and not value.strip():
                raise ValueError(f"Puste wymagane pole: {field}.")

        expected_expiry = calculate_medical_expiry(employee["hire_date"])
        if employee.get("medical_exam_valid_until") != expected_expiry:
            raise ValueError("Termin badań jest niezgodny z datą zatrudnienia.")

    if database["next_id"] <= max(used_ids, default=0):
        raise ValueError("Licznik ID jest niezgodny z zapisanymi wpisami.")


def load_database():
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            database = json.load(file)
    except FileNotFoundError:
        if BACKUP_FILE.exists():
            raise ValueError("Brakuje pliku bazy, ale istnieje kopia zapasowa.")
        return {"schema_version": 1, "next_id": 1, "employees": []}

    validate_database(database)
    return database


def save_database(database):
    validate_database(database)
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=DATA_FILE.parent,
            prefix="employees_",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            json.dump(database, file, ensure_ascii=False, indent=4)
            file.flush()
            os.fsync(file.fileno())

        if DATA_FILE.exists():
            shutil.copy2(DATA_FILE, BACKUP_FILE)

        os.replace(temporary_path, DATA_FILE)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def commit_database(database, candidate):
    try:
        save_database(candidate)
    except (OSError, ValueError) as error:
        print(f"Nie udało się zapisać zmian: {error}")
        return False

    database.clear()
    database.update(candidate)
    return True


def show_menu():
    print("\n=== Employee Manager ===")
    print("1. Dodaj pracownika")
    print("2. Pokaż pracowników")
    print("3. Edytuj pracownika")
    print("4. Wyszukaj, filtruj i sortuj")
    print("0. Zakończ")


def read_employee_field(field, label, current_value=None):
    while True:
        if current_value is None:
            value = input(f"{label}: ").strip()
        else:
            value = input(f"{label} [{current_value}]: ").strip()
            if value == "":
                return current_value

        if value == "-":
            if field in REQUIRED_FIELDS:
                print("To pole jest wymagane.")
                continue
            return ""

        if field in REQUIRED_FIELDS and not value:
            print("To pole jest wymagane.")
            continue

        if field == "hire_date":
            try:
                parse_hire_date(value)
            except ValueError:
                print("Podaj prawidłową datę RRRR-MM-DD, np. 2026-10-09.")
                continue

        return value


def add_employee(database):
    print("\nImię, nazwisko, stanowisko, dział i data zatrudnienia są wymagane.")
    print("Pola opcjonalne możesz pominąć Enterem.")

    employee = {"id": database["next_id"]}
    for field, label in EMPLOYEE_FIELDS.items():
        employee[field] = read_employee_field(field, label)

    employee["medical_exam_valid_until"] = calculate_medical_expiry(
        employee["hire_date"]
    )
    candidate = deepcopy(database)
    candidate["employees"].append(employee)
    candidate["next_id"] += 1

    if commit_database(database, candidate):
        print(f"Dodano i zapisano pracownika o ID {employee['id']}.")
        print(f"Badania ważne do: {employee['medical_exam_valid_until']}")


def show_employee(employee):
    print(f"\n--- Pracownik ID: {employee['id']} ---")
    for field, label in EMPLOYEE_FIELDS.items():
        print(f"{label}: {employee.get(field) or '—'}")
    print(f"Badania ważne do: {employee['medical_exam_valid_until']}")


def show_employees(database):
    if not database["employees"]:
        print("Lista pracowników jest pusta.")
        return

    for employee in database["employees"]:
        show_employee(employee)


def find_employee_by_id(employees, employee_id):
    for employee in employees:
        if employee["id"] == employee_id:
            return employee
    return None


def edit_employee(database):
    if not database["employees"]:
        print("Lista pracowników jest pusta.")
        return

    try:
        employee_id = int(input("Podaj ID pracownika: ").strip())
    except ValueError:
        print("ID musi być liczbą całkowitą.")
        return

    candidate = deepcopy(database)
    employee = find_employee_by_id(candidate["employees"], employee_id)
    if employee is None:
        print("Nie znaleziono pracownika o takim ID.")
        return

    print(f"\nEdycja: {employee['first_name']} {employee['last_name']}")
    print("Enter zachowuje wartość; - czyści pole opcjonalne.")
    print("Termin badań jest wyliczany z daty zatrudnienia.")
    changed = False

    for field, label in EMPLOYEE_FIELDS.items():
        if field in IMMUTABLE_FIELDS:
            continue

        current_value = employee[field]
        new_value = read_employee_field(field, label, current_value)
        if new_value != current_value:
            employee[field] = new_value
            changed = True

    if not changed:
        print("Dane pozostały bez zmian.")
        return

    employee["medical_exam_valid_until"] = calculate_medical_expiry(
        employee["hire_date"]
    )
    if commit_database(database, candidate):
        print("Zaktualizowano i zapisano dane pracownika.")
        print(f"Badania ważne do: {employee['medical_exam_valid_until']}")


def normalize_search_text(value):
    text = value.casefold().replace("ł", "l")
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    ).strip()


def polish_sort_key(value):
    text = unicodedata.normalize("NFC", value.strip().casefold())
    result = []
    for character in text:
        if character in LETTER_ORDER:
            result.append(LETTER_ORDER[character])
        else:
            for simplified in normalize_search_text(character):
                result.append(
                    LETTER_ORDER.get(simplified, len(LETTER_ORDER) + ord(simplified))
                )
    return tuple(result)


def filter_employees(employees, employee_id=None, name_query="", filters=None):
    name_parts = normalize_search_text(name_query).split()
    normalized_filters = {
        field: normalize_search_text(value)
        for field, value in (filters or {}).items()
        if value.strip()
    }
    results = []

    for employee in employees:
        if employee_id is not None and employee["id"] != employee_id:
            continue

        full_name = normalize_search_text(
            f"{employee['first_name']} {employee['last_name']}"
        )
        if not all(part in full_name for part in name_parts):
            continue

        if not all(
            value in normalize_search_text(employee[field])
            for field, value in normalized_filters.items()
        ):
            continue

        results.append(employee)

    return results


def sort_employees(employees, field, descending=False):
    ordered = sorted(
        employees,
        key=lambda employee: (
            polish_sort_key(employee["last_name"]),
            polish_sort_key(employee["first_name"]),
            employee["id"],
        ),
    )
    filled = [employee for employee in ordered if employee[field] != ""]
    empty = [employee for employee in ordered if employee[field] == ""]

    def sort_key(employee):
        if field == "id":
            return employee[field]
        if field in ("hire_date", "medical_exam_valid_until"):
            return date.fromisoformat(employee[field])
        return polish_sort_key(employee[field])

    return sorted(filled, key=sort_key, reverse=descending) + empty


def read_choice(prompt, choices, default):
    while True:
        choice = input(prompt).strip() or default
        if choice in choices:
            return choice
        print(f"Wybierz jedną z opcji: {', '.join(choices)}.")


def read_filter_id():
    while True:
        value = input("ID (Enter = dowolne): ").strip()
        if not value:
            return None
        try:
            employee_id = int(value)
            if employee_id > 0:
                return employee_id
        except ValueError:
            pass
        print("Podaj dodatnie ID albo naciśnij Enter.")


def shorten(value, width):
    text = str(value) if value != "" else "—"
    return text if len(text) <= width else text[:width - 1] + "…"


def show_summary_table(employees):
    widths = (6, 26, 24, 18, 10)
    rows = [("ID", "Imię i nazwisko", "Dział", "Miasto", "Badania do")]
    for employee in employees:
        rows.append((
            employee["id"],
            f"{employee['first_name']} {employee['last_name']}",
            employee["department"],
            employee["city"],
            employee["medical_exam_valid_until"],
        ))
    for row in rows:
        print(" | ".join(
            f"{shorten(value, width):<{width}}"
            for value, width in zip(row, widths)
        ))


def show_search_results(employees):
    page = 0
    total_pages = (len(employees) + PAGE_SIZE - 1) // PAGE_SIZE
    while True:
        start = page * PAGE_SIZE
        end = min(start + PAGE_SIZE, len(employees))
        print(
            f"\nWyniki {start + 1}–{end} z {len(employees)} "
            f"| strona {page + 1}/{total_pages}"
        )
        show_summary_table(employees[start:end])
        print("\nn = następna, p = poprzednia, ID = szczegóły, 0 = menu")
        action = input("Wybierz: ").strip().casefold()

        if action == "0":
            return
        if action == "n":
            if page + 1 < total_pages:
                page += 1
            else:
                print("To ostatnia strona.")
            continue
        if action == "p":
            if page > 0:
                page -= 1
            else:
                print("To pierwsza strona.")
            continue

        try:
            employee_id = int(action)
        except ValueError:
            print("Wpisz n, p, ID pracownika albo 0.")
            continue

        employee = find_employee_by_id(employees, employee_id)
        if employee is None:
            print("Takiego ID nie ma w wynikach wyszukiwania.")
        else:
            show_employee(employee)
            input("Naciśnij Enter, aby wrócić do wyników.")


def browse_employees(database):
    if not database["employees"]:
        print("Lista pracowników jest pusta.")
        return

    print("\n=== Wyszukiwanie i filtrowanie ===")
    print("Enter pomija filtr. Wypełnione filtry działają jednocześnie.")
    employee_id = read_filter_id()
    name_query = input("Imię i/lub nazwisko (fragmenty): ").strip()
    filters = {
        field: input(f"{label} (fragment): ").strip()
        for field, label in FILTER_FIELDS.items()
    }
    results = filter_employees(
        database["employees"], employee_id, name_query, filters
    )
    print(f"Znaleziono: {len(results)} z {len(database['employees'])}.")
    if not results:
        print("Żaden pracownik nie spełnia podanych kryteriów.")
        return

    print("\nSortuj według:")
    for option, (_, label) in SORT_OPTIONS.items():
        print(f"{option}. {label}")
    choice = read_choice(
        "Wybierz pole (Enter = nazwisko): ", SORT_OPTIONS, "1"
    )
    field, _ = SORT_OPTIONS[choice]
    print("1. Rosnąco / A–Z / od najstarszej daty")
    print("2. Malejąco / Z–A / od najnowszej daty")
    direction = read_choice(
        "Wybierz kierunek (Enter = rosnąco): ", ("1", "2"), "1"
    )
    results = sort_employees(results, field, descending=direction == "2")
    show_search_results(results)


def main():
    try:
        database = load_database()
    except (OSError, ValueError) as error:
        print(f"Nie można wczytać bazy: {error}")
        print(f"Sprawdź plik: {DATA_FILE}")
        print(f"Kopia poprzedniego zapisu: {BACKUP_FILE}")
        return

    print(f"Wczytano pracowników: {len(database['employees'])}.")

    while True:
        show_menu()
        choice = input("Wybierz opcję: ").strip()

        if choice == "1":
            add_employee(database)
        elif choice == "2":
            show_employees(database)
        elif choice == "3":
            edit_employee(database)
        elif choice == "4":
            browse_employees(database)
        elif choice == "0":
            print("Do zobaczenia!")
            break
        else:
            print("Wybierz 1, 2, 3, 4 albo 0.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nZakończono program. Wcześniejsze zapisy pozostają w bazie.")