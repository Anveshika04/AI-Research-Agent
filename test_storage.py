import json
import tempfile
import unittest
from pathlib import Path

import storage


class StorageTest(unittest.TestCase):
    def test_save_and_load_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = storage.REPORTS_DIR
            try:
                storage.REPORTS_DIR = Path(tmpdir)
                result = {"status": "ok", "topic": "test", "summary": "hello"}
                report_id = storage.save_report("test", result)
                payload = storage.load_report(report_id)
                self.assertEqual(payload["id"], report_id)
                self.assertEqual(payload["topic"], "test")
                self.assertEqual(payload["result"]["summary"], "hello")
            finally:
                storage.REPORTS_DIR = original_dir

    def test_list_reports_newest_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = storage.REPORTS_DIR
            try:
                storage.REPORTS_DIR = Path(tmpdir)
                payload_a = {"id": "20200101000000-a", "topic": "a", "created_at": "2020-01-01T00:00:00Z"}
                payload_b = {"id": "20200102000000-b", "topic": "b", "created_at": "2020-01-02T00:00:00Z"}
                (storage.REPORTS_DIR / f"{payload_a['id']}.json").write_text(
                    json.dumps(payload_a), encoding="utf-8"
                )
                (storage.REPORTS_DIR / f"{payload_b['id']}.json").write_text(
                    json.dumps(payload_b), encoding="utf-8"
                )
                reports = storage.list_reports()
                self.assertEqual(reports[0]["id"], payload_b["id"])
                self.assertEqual(reports[1]["id"], payload_a["id"])
            finally:
                storage.REPORTS_DIR = original_dir


if __name__ == "__main__":
    unittest.main()
