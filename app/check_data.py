import csv
from pathlib import Path

# Path to the provided dataset
DATA_PATH = Path(__file__).parent.parent / "data" / "support_tickets.csv"

with open(DATA_PATH, "r", encoding="utf-8", newline="") as file:
    reader = csv.DictReader(file)

    rows = list(reader)

print("=" * 60)
print("DATASET CHECK")
print("=" * 60)

print(f"File: {DATA_PATH}")
print(f"Total rows: {len(rows)}")

print("\nColumns:")
for column in reader.fieldnames:
    print(f" - {column}")

print("\nFirst 3 rows:")
for row in rows[:3]:
    print(row)

print("\nMissing values:")
for column in reader.fieldnames:
    missing = sum(
        1 for row in rows
        if row[column] is None or row[column].strip() == ""
    )
    print(f" - {column}: {missing}")

print("=" * 60)