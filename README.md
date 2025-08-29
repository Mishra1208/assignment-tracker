## 📸 Screenshots

### Google API Setup
![Google API Setup](assets/gAPI.png)

# 📝 Assignment Tracker (CSV + Google Sheets)

This is a simple command-line Assignment Tracker.  
It lets you add, list, and mark assignments as done, while also syncing them into a Google Sheet for a dashboard view.

Follow the presentation link explanining on how to setup environemnt and use the project 

https://docs.google.com/presentation/d/1-BsRWSqs6ssJg5x43oDKFV8hHUDQzVxH/edit?usp=sharing&ouid=106674971482274775497&rtpof=true&sd=true
---

## 🚀 Features
- Add assignments with **student ID, course, title, deadline, weight, hours**
- List all assignments, filter by student ID
- Check upcoming deadlines (e.g., due in next 7 days)
- Mark assignments as **done**
- Auto-sync to **Google Sheets** after each `add`

---

## 📦 Requirements
- Python 3.9+ (tested on Python 3.13)
- Packages listed in `requirements.txt`

Install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt



⚙️ Enable Auto-Sync

Before running the tracker, you must export these environment variables in your terminal:

# make sure env vars are set if you want auto-sync to Sheets on --sync
export SHEET_ID=YOUR_SHEET_ID
export SERVICE_ACCOUNT_JSON=/Users/narendramishra/Desktop/demo/service_account.json
export SHEET_TAB=Assignments


SHEET_ID → from your Google Sheet URL (between /d/ and /edit).

SERVICE_ACCOUNT_JSON → path to your downloaded service account key.

SHEET_TAB → usually Assignments (or whichever tab you want).

Then run add with the --sync flag to auto-push:

python3 tracker.py add \
  --student-id 101 --student-name "Alice Lee" \
  --course COMP353 --title "ANYTHING Assignment" \
  --deadline 2025-10-05 --weight 20 --est-hours 6 \
  --sync

🔄 Manual Sync (after updates)

If you’ve marked tasks as done or made other changes and want to push the updated CSV to Google Sheets, run:

python3 sync_to_sheet.py \
  --sheet-id "$SHEET_ID" \
  --service-account "$SERVICE_ACCOUNT_JSON" \
  --csv assignments.csv \
  --tab "$SHEET_TAB"


This ensures your latest assignment data is reflected in the Google Sheet.

🐍 Python Interpreter Note

Depending on your system, python3 may point to a different interpreter that doesn’t have gspread installed.

The version that works is usually:

/usr/local/bin/python3


To avoid confusion, you can either:

Always run tracker with /usr/local/bin/python3 tracker.py …

Or install gspread into the Python your python3 points to:

python3 -m pip install gspread oauth2client


If you prefer convenience, add an alias in your shell config (~/.zshrc):

alias pytrack="/usr/local/bin/python3 /Users/narendramishra/Desktop/demo/tracker.py"


Now you can just use:

pytrack add --student-id 101 --student-name "Alice Lee" ...

Example Workflow

Add assignments with validation:

pytrack add --student-id 101 --student-name "Alice Lee" \
  --course COMP353 --title "Hashing Assignment" \
  --deadline 2025-10-05 --weight 20 --est-hours 6 --sync


List all:

pytrack list


Show due in 7 days:

pytrack due-in --days 7


Mark as done:

pytrack done --id 1


Manually sync (if needed):

python3 sync_to_sheet.py --sheet-id "$SHEET_ID" \
  --service-account "$SERVICE_ACCOUNT_JSON" \
  --csv assignments.csv --tab "$SHEET_TAB"
