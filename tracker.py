#!/usr/bin/env python3
import csv, os, sys, argparse, subprocess
from datetime import datetime, timedelta

CSV_PATH = "assignments.csv"
FIELDNAMES = [
    "id", "student_id", "student_name",
    "course", "title", "deadline", "weight", "est_hours",
    "status", "created_at"
]

# ---------- CSV helpers ----------

def ensure_csv():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDNAMES)
            w.writeheader()

def load_rows():
    ensure_csv()
    with open(CSV_PATH, newline="") as f:
        return list(csv.DictReader(f))

def save_rows(rows):
    with open(CSV_PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)

def next_id(rows):
    if not rows:
        return "1"
    return str(max(int(r["id"]) for r in rows) + 1)

# ---------- Date helpers ----------

def parse_date(s: str) -> datetime:
    """
    Accept YYYY-MM-DD or YYYY-MM-DDTHH:MM.
    Raises ValueError if invalid.
    """
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M")
    except ValueError:
        return datetime.strptime(s, "%Y-%m-%d")

def fmt_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")

# ---------- Optional: auto-sync to Google Sheets ----------

def maybe_sync():
  
    sheet_id = os.getenv("SHEET_ID")
    if not sheet_id:
        return  # autosync disabled

    sa_json = os.getenv("SERVICE_ACCOUNT_JSON", "service_account.json")
    tab     = os.getenv("SHEET_TAB", "Assignments")
    sync_py = os.getenv("SYNC_SCRIPT", "sync_to_sheet.py")

    try:
        # Use the same interpreter this script is running with
        cmd = [
            sys.executable, sync_py,
            "--sheet-id", sheet_id,
            "--service-account", sa_json,
            "--csv", CSV_PATH,
            "--tab", tab,
        ]
        subprocess.run(cmd, check=True)
        print(f"🔄 Synced to Google Sheet tab '{tab}'.")
    except FileNotFoundError:
        print("⚠️  Sync skipped: sync_to_sheet.py not found. Set SYNC_SCRIPT or place it in the same folder.")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Sync script error (exit {e.returncode}).")
    except Exception as e:
        print(f"⚠️  Sync skipped: {e}")

# ---------- Commands ----------

def add(args):
    rows = load_rows()
    rid = next_id(rows)
    now = datetime.now().isoformat(timespec="seconds")

    # Validate/normalize fields
    deadline_text = args.deadline
    try:
        _ = parse_date(deadline_text)  # raises if invalid
    except ValueError:
        print("Invalid --deadline. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM")
        sys.exit(1)

    row = {
        "id": rid,
        "student_id": str(args.student_id),
        "student_name": args.student_name,
        "course": args.course,
        "title": args.title,
        "deadline": deadline_text,  # keep original text form
        "weight": str(args.weight if args.weight is not None else ""),
        "est_hours": str(args.est_hours if args.est_hours is not None else ""),
        "status": "todo",
        "created_at": now
    }
    rows.append(row)
    save_rows(rows)

    # Auto-sync if configured
    if args.sync:
        maybe_sync()

    print(f"Added assignment #{rid} for Student {args.student_id}: {args.course} – {args.title} (due {deadline_text})")

def list_cmd(args):
    rows = load_rows()
    rows = [r for r in rows if (not args.student_id or r["student_id"] == str(args.student_id))]

    # sort by deadline ascending; skip rows with bad dates gracefully
    def key(r):
        try:
            return parse_date(r["deadline"])
        except Exception:
            return datetime.max

    rows.sort(key=key)
    if not rows:
        print("No assignments found.")
        return

    print(f"{'ID':<4} {'StuID':<6} {'Course':<10} {'Title':<30} {'Deadline':<16} {'W%':<4} {'Hrs':<4} {'Status':<6}")
    print("-"*90)
    for r in rows:
        w = r['weight'] or "-"
        h = r['est_hours'] or "-"
        print(f"{r['id']:<4} {r['student_id']:<6} {r['course']:<10} {r['title'][:28]:<30} {r['deadline']:<16} {w:<4} {h:<4} {r['status']:<6}")

def due_in(args):
    rows = load_rows()
    horizon = datetime.now() + timedelta(days=args.days)
    out = []
    for r in rows:
        try:
            d = parse_date(r["deadline"])
        except Exception:
            continue
        if d <= horizon and (not args.student_id or r["student_id"] == str(args.student_id)):
            out.append(r)

    out.sort(key=lambda r: parse_date(r["deadline"]))
    if not out:
        print(f"No assignments due in next {args.days} days.")
        return

    print(f"Assignments due in next {args.days} days:")
    today = datetime.now().date()
    for r in out:
        d = parse_date(r["deadline"])
        days_left = (d.date() - today).days
        print(f"  • #{r['id']} [{r['student_id']}] {r['course']} – {r['title']} (due {r['deadline']}, in {days_left} days) [{r['status']}]")

def done(args):
    rows = load_rows()
    updated = False
    for r in rows:
        if r["id"] == str(args.id):
            r["status"] = "done"
            updated = True
            break
    if not updated:
        print(f"No assignment with id {args.id}")
        return
    save_rows(rows)
    print(f"Marked assignment #{args.id} as done.")

# ---------- CLI ----------

def main():
    p = argparse.ArgumentParser(description="Simple Assignment Tracker (CSV-based)")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add an assignment")
    p_add.add_argument("--student-id", required=True, type=int)
    p_add.add_argument("--student-name", required=True)
    p_add.add_argument("--course", required=True)
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--deadline", required=True, help="YYYY-MM-DD or YYYY-MM-DDTHH:MM")
    p_add.add_argument("--weight", type=float, default=None)
    p_add.add_argument("--est-hours", type=float, default=None)
    p_add.add_argument("--sync", action="store_true", help="Sync to Google Sheets after add (uses SHEET_ID env)")
    p_add.set_defaults(func=add)

    p_list = sub.add_parser("list", help="List assignments (optionally by student)")
    p_list.add_argument("--student-id", type=int)
    p_list.set_defaults(func=list_cmd)

    p_due = sub.add_parser("due-in", help="List assignments due in N days")
    p_due.add_argument("--days", type=int, default=7)
    p_due.add_argument("--student-id", type=int)
    p_due.set_defaults(func=due_in)

    p_done = sub.add_parser("done", help="Mark an assignment as done by ID")
    p_done.add_argument("--id", type=int, required=True)
    p_done.set_defaults(func=done)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
