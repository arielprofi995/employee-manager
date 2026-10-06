# Employee Manager

Lokalna aplikacja terminalowa w Pythonie do zarządzania pracownikami. Projekt edukacyjny rozwijany na macOS w Visual Studio Code.

**Wydanie:** 1.0.0  
**Autorka:** Arieta Hofman  
**Zależności:** biblioteka standardowa Pythona.

## Funkcje

- Dodawanie pracowników i wyświetlanie ich pełnych danych.
- Edycja nazwiska, stanowiska, działu, adresu, e-maila, telefonu i daty zatrudnienia.
- Stałe imię oraz automatycznie nadawane, unikalne ID.
- Osobne pola adresu: ulica, numer domu i lokalu, kod pocztowy, miasto, kraj.
- Automatyczne obliczanie rocznego terminu badań z daty zatrudnienia.
- Trwały zapis JSON po dodaniu lub edycji oraz odczyt przy uruchomieniu.
- Lokalna kopia poprzedniego zapisu.
- Wyszukiwanie po dokładnym ID i fragmentach imienia oraz nazwiska.
- Łączenie filtrów działu, stanowiska, miasta i kraju.
- Sortowanie tekstów, ID i dat w obu kierunkach.
- Strony wyników po 10 osób i otwieranie szczegółów po ID.
- Sprawdzanie wymaganych pól, dat i struktury pliku danych.

## Uruchomienie

Potrzebny jest Python 3.12 lub nowszy. Projekt działał na Macu z Pythonem 3.13.15; przygotowany kod sprawdzono także z Pythonem 3.12.14.

Otwórz folder projektu w terminalu lub VS Code, a następnie na macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python main.py
```

Środowisko .venv oddziela interpreter projektu. Nie trzeba instalować pakietów przez pip.

Jeśli środowisko już istnieje, wystarczy je aktywować i uruchomić program.

## Menu

| Opcja | Działanie |
| --- | --- |
| 1 | Dodaj pracownika. |
| 2 | Wyświetl pełne dane wszystkich pracowników. |
| 3 | Edytuj pracownika po ID. |
| 4 | Wyszukaj, filtruj i sortuj. |
| 0 | Zakończ program. |

## Wprowadzanie i edycja danych

Wymagane są imię, nazwisko, stanowisko, dział i data zatrudnienia. Pozostałe pola można pozostawić puste.

- Daty wpisujemy w formacie RRRR-MM-DD.
- Enter podczas edycji zachowuje dotychczasową wartość.
- Znak - czyści pole opcjonalne.
- Imię i ID pozostają stałe.
- Zmiana daty zatrudnienia automatycznie przelicza termin badań.
- Telefon, kod pocztowy i numery adresowe są tekstem; zachowują początkowe zera oraz znak +.

## Reguła terminu badań

Założenie demonstracyjne tego projektu: termin przypada rok kalendarzowy po zatrudnieniu.

| Data zatrudnienia | Obliczony termin |
| --- | --- |
| 2026-10-09 | 2027-10-09 |
| 2024-02-29 | 2025-02-28 |

Dla 29 lutego wybieramy 28 lutego kolejnego roku. Pole terminu jest obliczane przez program.

## Wyszukiwanie i sortowanie

W opcji 4 Enter pomija filtr. Wszystkie wypełnione kryteria muszą być spełnione jednocześnie.

Filtry tekstowe dopasowują fragmenty bez rozróżniania wielkości liter i znaków diakrytycznych: lodz odnajduje Łódź. ID jest porównywane dokładnie.

Dostępne pola sortowania: nazwisko, imię, ID, dział, stanowisko, miasto, data zatrudnienia i termin badań.

- Teksty: A–Z lub Z–A, z kolejnością polskich liter.
- ID: rosnąco lub malejąco jako liczby.
- Daty: od najstarszej lub najnowszej.
- Puste wartości: na końcu w obu kierunkach.
- Remisy: pomocnicza kolejność nazwiska, imienia i ID.
- Domyślnie: nazwisko A–Z.

W wynikach n oznacza następną stronę, p poprzednią, 0 powrót do menu. Wpisanie numeru ID otwiera pełne dane osoby z wyników.

## Dane i zapis

Program sam tworzy katalog data oraz plik data/employees.json po pierwszym udanym dodaniu osoby. Ścieżka jest ustalana względem main.py.

Baza przechowuje wersję schematu, licznik następnego ID i listę pracowników. Zapis odbywa się przez plik roboczy i podmianę gotowego pliku. Kolejny zapis tworzy data/employees.json.bak z poprzednią wersją.

Nieprawidłowa zawartość bazy zatrzymuje uruchomienie i daje komunikat. Zmiany są zatwierdzane w pamięci po udanym zapisie na dysku.

Projekt jest przeznaczony do lokalnej pracy w jednym procesie.

## Pliki projektu

| Plik | Rola |
| --- | --- |
| main.py | Pełny kod aplikacji. |
| .gitignore | Pomija środowisko, lokalną bazę i pliki generowane. |
| examples/employees.example.json | Fikcyjne dane pokazujące format bazy. |

Katalog data jest lokalny i znajduje się w .gitignore. Plik przykładowy pozostaje osobno w examples; aplikacja nie importuje go automatycznie.

## Sprawdzone działanie

Sprawdzono zapis i odczyt po ponownym uruchomieniu, edycję, regułę 29 lutego, obsługę błędów pliku, łączone filtry, sortowanie w obu kierunkach i przechodzenie między stronami.

## Nauka i dalszy rozwój

Projekt ćwiczy funkcje, słowniki, listy, pętle, wyjątki, pracę z datami i plikami, normalizację tekstu oraz sortowanie.

Obecny zakres wydania 1.0.0 jest zamknięty. W przyszłości można rozważyć status terminów badań, archiwizację, podział na moduły, SQLite lub interfejs graficzny.

Projekt powstał podczas nauki Pythona we współpracy z asystentem AI.
