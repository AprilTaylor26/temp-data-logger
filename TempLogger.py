import datetime
import csv
from pathlib import Path

print("SCRIPT PATH:", Path(__file__).resolve())
print("CSV PATH:", (Path(__file__).resolve().parent / "ZooData.csv"))
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "ZooData.csv"
DATE_FORMAT = "%d/%m/%Y"

print("Using CSV file at:", CSV_PATH)


def now_ts() -> str:
    return str(datetime.datetime.now()).split(".")[0]


def convert_f_to_c(temp_f: float) -> float:
    return (temp_f - 32) * 5 / 9


def validate_date(date_str: str) -> datetime.date | None:
    """Return a date object if valid, else None."""
    try:
        return datetime.datetime.strptime(date_str, DATE_FORMAT).date()
    except ValueError:
        return None


def ensure_csv_has_header(path: Path) -> None:
    """Create file + header if it doesn't exist or is empty."""
    if (not path.exists()) or path.stat().st_size == 0:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "temp_f", "temp_c"])


def insert_row(path: Path, entry_date: str, temp_f: float, temp_c: float) -> None:
    ensure_csv_has_header(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([entry_date, f"{temp_f:.2f}", f"{temp_c:.2f}"])


def read_rows(path: Path) -> list[dict]:
    if (not path.exists()) or path.stat().st_size == 0:
        return []
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def view_data(path: Path) -> None:
    ensure_csv_has_header(path)
    rows = read_rows(path)

    if not rows:
        print(f"\nNo records found in {path}.")
        return

    print(f"\nContents of {path} ({len(rows)} records):")
    for r in rows:
        print(f"{r['date']} | {r['temp_f']}F | {r['temp_c']}C")


def input_entries() -> None:
    try:
        total_entries = int(input("How many entries are you inputting? "))
        if total_entries <= 0:
            print("Please enter a number greater than 0.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    for _ in range(total_entries):
        entry_date = input("\nEnter a date (DD/MM/YYYY): ").strip()
        parsed = validate_date(entry_date)
        if not parsed:
            print("Invalid date format. Please use DD/MM/YYYY (example: 03/03/2026).")
            continue

        try:
            temp_f = float(input("Enter the highest temp (F) for that date: "))
        except ValueError:
            print("Please enter a valid temperature.")
            continue

        temp_c = convert_f_to_c(temp_f)

        try:
            insert_row(CSV_PATH, entry_date, temp_f, temp_c)
            print(f"\nSaved at {now_ts()}: {entry_date} | {temp_f:.2f}F | {temp_c:.2f}C")
        except Exception as e:
            print(f"Failed to save entry: {e}")


def generate_report(path: Path) -> None:
    rows = read_rows(path)
    if not rows:
        print("\nNo data available to generate a report.")
        return

    temps_f = [float(r["temp_f"]) for r in rows]
    temps_c = [float(r["temp_c"]) for r in rows]

    count = len(rows)
    avg_f = sum(temps_f) / count
    avg_c = sum(temps_c) / count
    min_f, max_f = min(temps_f), max(temps_f)
    min_c, max_c = min(temps_c), max(temps_c)

    def parse_row_date(r: dict) -> datetime.date:
        return datetime.datetime.strptime(r["date"], DATE_FORMAT).date()

    most_recent = max(rows, key=parse_row_date)

    report_lines = [
        "=== Zoo Temperature Report ===",
        f"Generated: {now_ts()}",
        f"Records: {count}",
        "",
        f"Average Temp: {avg_f:.2f}F | {avg_c:.2f}C",
        f"Minimum Temp: {min_f:.2f}F | {min_c:.2f}C",
        f"Maximum Temp: {max_f:.2f}F | {max_c:.2f}C",
        "",
        "Most Recent Entry:",
        f"  Date: {most_recent['date']}",
        f"  Temp: {float(most_recent['temp_f']):.2f}F | {float(most_recent['temp_c']):.2f}C",
    ]

    print("\n" + "\n".join(report_lines))

    save = input("\nSave report to file? (y/n): ").strip().lower()
    if save == "y":
        report_path = BASE_DIR / "ZooData_Report.txt"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
        print(f"Report saved to {report_path}")


def menu() -> None:
    ensure_csv_has_header(CSV_PATH)

    running = True
    while running:
        print("\nApril's Spreadsheet Automation Menu")
        print("1. Input Data")
        print("2. View Current Data")
        print("3. Generate Report")
        print("4. Exit")

        choice = input("Select Option: ").strip()

        match choice:
            case "1":
                print(f"\nOption 1 selected at {now_ts()}")
                input_entries()
            case "2":
                print(f"\nOption 2 selected at {now_ts()}")
                view_data(CSV_PATH)
            case "3":
                print(f"\nOption 3 selected at {now_ts()}")
                generate_report(CSV_PATH)
            case "4":
                print("\nExiting Program. Bye!")
                running = False
            case _:
                print("\nError: Invalid choice. Please try again.")


menu()


