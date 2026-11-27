"""Review an exported CSV locally. No network access or live capture."""
import argparse
import csv
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def alerts(rows, grant_seconds=600):
    failures = defaultdict(list)
    pending = {}
    found = []
    for t, event, account, source, detail in sorted(rows):
        key = (account, source)
        if event == "login_fail":
            failures[key] = [f for f in failures[key] if (t-f).total_seconds() <= 300]
            failures[key].append(t)
        elif event == "login_success":
            recent = [f for f in failures.pop(key, []) if (t-f).total_seconds() <= 300]
            pending.pop(key, None)
            if len(recent) >= 3:
                alert = dict(time=t, account=account, source=source, failures=len(recent), grant=None)
                found.append(alert)
                pending[key] = alert
        elif event == "role_grant" and detail == "admin" and key in pending:
            alert = pending[key]
            if 0 < (t-alert["time"]).total_seconds() <= grant_seconds:
                alert["grant"] = t
                del pending[key]
    return found


def read_rows(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            t = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
            if t.utcoffset() is None:
                raise ValueError("timestamps must include a UTC offset")
            yield t, row["event"], row["account"], row["source"], row["detail"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=Path(__file__).parent / "data/events.csv")
    parser.add_argument("--grant-minutes", type=int, default=10)
    args = parser.parse_args()
    if args.grant_minutes < 1:
        parser.error("--grant-minutes must be at least 1")
    try:
        for item in alerts(read_rows(args.path), grant_seconds=args.grant_minutes * 60):
            label = "Escalate for verification" if item["grant"] else "Review login"
            print(f'{label} | {item["account"]} | {item["source"]} | '
                  f'{item["failures"]} failed attempts before success at {item["time"].isoformat()}')
            if item["grant"]:
                print(f'  Admin grant followed at {item["grant"].isoformat()}')
    except (OSError, ValueError, KeyError) as exc:
        sys.exit(f"Could not read event export: {exc}")
