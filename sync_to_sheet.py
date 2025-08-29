#!/usr/bin/env python3
import argparse, csv, sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials

HEADERS = [
    "id", "student_id", "student_name",
    "course", "title", "deadline", "weight", "est_hours",
    "status", "created_at"
]

def open_sheet(sheet_id: str, sa_json: str):
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(sa_json, scope)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id)

def ensure_worksheet(sh, title: str, rows=100, cols=20):
    try:
        return sh.worksheet(title)
    except gspread.WorksheetNotFound:
        return sh.add_worksheet(title=title, rows=str(rows), cols=str(cols))

def read_csv(path: str):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    # Ensure columns order & fill missing keys
    out = []
    for r in rows:
        out.append([r.get(h, "") for h in HEADERS])
    return out

def main():
    ap = argparse.ArgumentParser(description="Sync assignments.csv -> Google Sheet tab")
    ap.add_argument("--csv", default="assignments.csv", help="Path to CSV (default: assignments.csv)")
    ap.add_argument("--sheet-id", required=True, help="Google Sheet ID")
    ap.add_argument("--service-account", default="secrets/service_account.json", help="Path to service account JSON")
    ap.add_argument("--tab", default="Assignments", help="Worksheet/tab name (default: Assignments)")
    args = ap.parse_args()

    try:
        rows = read_csv(args.csv)
    except FileNotFoundError:
        sys.exit(f"CSV not found: {args.csv}")

    sh = open_sheet(args.sheet_id, args.service_account)
    ws = ensure_worksheet(sh, args.tab)

    # Clear and write header + data
    ws.clear()
    ws.append_row(HEADERS, value_input_option="USER_ENTERED")
    if rows:
        ws.append_rows(rows, value_input_option="USER_ENTERED")

    print(f"Synced {len(rows)} rows to Sheet '{args.tab}' ({args.sheet_id}).")

if __name__ == "__main__":
    main()
