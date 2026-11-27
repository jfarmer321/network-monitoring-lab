from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import TestCase
from triage import alerts, read_rows

BASE = datetime(2026, 11, 25, tzinfo=timezone.utc)


def row(seconds, event, account="casey", source="192.0.2.14", detail=""):
    return BASE + timedelta(seconds=seconds), event, account, source, detail


class TriageTest(TestCase):
    def test_seed(self):
        found = alerts(read_rows(Path(__file__).parent / "data/events.csv"))
        self.assertEqual([a["account"] for a in found], ["casey", "robin"])
        self.assertIsNone(found[0]["grant"])
        self.assertIsNotNone(found[1]["grant"])

    def test_old_failures_do_not_count(self):
        self.assertEqual(alerts([row(i, "login_fail") for i in range(3)]
                                + [row(303, "login_success")]), [])

    def test_different_source_does_not_count(self):
        self.assertEqual(alerts([row(i, "login_fail") for i in range(3)]
                                + [row(10, "login_success", source="192.0.2.15")]), [])

    def test_five_minute_boundary(self):
        found = alerts([row(i, "login_fail") for i in range(3)] + [row(300, "login_success")])
        self.assertEqual(len(found), 1)

    def test_late_grant_does_not_escalate(self):
        found = alerts([row(i, "login_fail") for i in range(3)] +
                       [row(10, "login_success"), row(611, "role_grant", detail="admin")])
        self.assertIsNone(found[0]["grant"])

    def test_changing_window_keeps_login_alert(self):
        rows = list(read_rows(Path(__file__).parent / "data/events.csv"))
        found = alerts(rows, grant_seconds=60)
        self.assertEqual([a["account"] for a in found], ["casey", "robin"])
        self.assertTrue(all(a["grant"] is None for a in found))
