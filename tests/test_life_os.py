import os
import tempfile
import unittest
from pathlib import Path


class LifeOSTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["DATA_DIR"] = self.temp_dir.name
        os.environ["DATABASE_PATH"] = str(Path(self.temp_dir.name) / "test.sqlite3")

        from app import config

        config.settings = config.Settings(
            data_dir=Path(self.temp_dir.name),
            database_path=Path(self.temp_dir.name) / "test.sqlite3",
        )

        import app.db as db

        db.settings = config.settings
        db.ensure_database()
        self.db = db

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_quick_entry_creates_exercise_record_with_score(self) -> None:
        from app.nlp import parse_quick_entry

        payload = parse_quick_entry("今天跑步 45 分钟 6 公里 #健康")
        self.assertEqual(payload["module"], "exercise")
        self.assertEqual(payload["details"]["duration"], 45)
        self.assertEqual(payload["tags"], ["健康"])

        with self.db.connect() as conn:
            record = self.db.create_record(conn, payload["module"], payload)

        self.assertGreater(record["score"], 9)
        self.assertEqual(record["details"]["distance"], 6)

    def test_password_records_mask_and_reveal_secret(self) -> None:
        with self.db.connect() as conn:
            record = self.db.create_record(
                conn,
                "password",
                {
                    "title": "邮箱账号",
                    "details": {"account": "me@example.com", "secret": "s3cret"},
                },
            )
            fetched = self.db.get_record(conn, record["id"])
            secret = self.db.reveal_record_secret(conn, record["id"])

        assert fetched is not None
        self.assertEqual(fetched["details"]["secret"], "********")
        self.assertEqual(secret, "s3cret")

    def test_dashboard_contains_seeded_modules_and_insights(self) -> None:
        with self.db.connect() as conn:
            data = self.db.dashboard(conn)

        self.assertIn("life_score", data)
        self.assertTrue(data["summary"])
        self.assertTrue(data["insights"])


if __name__ == "__main__":
    unittest.main()
