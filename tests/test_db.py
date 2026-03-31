import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DB_SCRIPT = REPO_ROOT / "src" / "db.py"


class DbCliTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_path = Path(self.temp_dir.name)
        self.home_dir = self.temp_path / "home"
        self.home_dir.mkdir()
        self.db_path = self.temp_path / "opckit.db"

    def cli_env(self):
        env = os.environ.copy()
        env["HOME"] = str(self.home_dir)
        env["OPCKIT_DB_PATH"] = str(self.db_path)
        return env

    def run_cli(self, *args, check=True):
        completed = subprocess.run(
            [sys.executable, str(DB_SCRIPT), *args],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            env=self.cli_env(),
        )
        if check and completed.returncode != 0:
            raise AssertionError(
                f"command failed: {' '.join(args)}\n"
                f"stdout: {completed.stdout}\n"
                f"stderr: {completed.stderr}"
            )

        data = None
        if completed.stdout.strip():
            data = json.loads(completed.stdout)
        return completed, data

    def execute_sql(self, sql, params=()):
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute(sql, params)
            conn.commit()
        finally:
            conn.close()

    def test_init_lists_templates_and_creates_database(self):
        completed, data = self.run_cli("init")

        self.assertEqual(completed.returncode, 0)
        self.assertTrue(self.db_path.exists())
        self.assertEqual(
            sorted(data["available_templates"]),
            ["consultant", "creator", "designer", "developer"],
        )

    def test_init_copies_selected_template_and_rejects_unknown_template(self):
        _, data = self.run_cli("init", "--template", "designer")
        config_path = self.home_dir / ".opckit" / "config" / "industry.json"

        self.assertEqual(data["template"], "designer")
        self.assertTrue(config_path.exists())
        config = json.loads(config_path.read_text(encoding="utf-8"))
        self.assertEqual(config["industry"], "UI/品牌设计师")

        failed, failed_data = self.run_cli("init", "--template", "unknown", check=False)
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse(failed_data["ok"])
        self.assertIn("unknown", failed_data["error"])
        self.assertEqual(
            sorted(failed_data["available"]),
            ["consultant", "creator", "designer", "developer"],
        )

    def test_client_commands(self):
        _, add_one = self.run_cli(
            "client",
            "add",
            "--data",
            json.dumps(
                {
                    "name": "张总",
                    "industry": "餐饮",
                    "needs": "品牌VI设计",
                    "budget": "2万",
                    "status": "potential",
                    "tags": ["vip"],
                },
                ensure_ascii=False,
            ),
        )
        first_id = add_one["id"]

        _, add_two = self.run_cli(
            "client",
            "add",
            "--data",
            json.dumps(
                {
                    "name": "李经理",
                    "industry": "教育",
                    "needs": "官网重做",
                    "budget": "3万",
                    "status": "active",
                },
                ensure_ascii=False,
            ),
        )
        second_id = add_two["id"]

        _, add_three = self.run_cli(
            "client",
            "add",
            "--data",
            json.dumps(
                {
                    "name": "王老板",
                    "industry": "零售",
                    "needs": "包装升级",
                    "budget": "1万",
                    "status": "closed",
                },
                ensure_ascii=False,
            ),
        )
        third_id = add_three["id"]

        self.execute_sql(
            "UPDATE clients SET last_contact=? WHERE id=?",
            ("2020-01-01", second_id),
        )
        self.execute_sql(
            "UPDATE clients SET last_contact=? WHERE id=?",
            ("2020-01-02", third_id),
        )

        _, list_active = self.run_cli("client", "list", "--status", "active", "--limit", "10")
        self.assertEqual(list_active["total"], 1)
        self.assertEqual(list_active["returned"], 1)
        self.assertEqual(list_active["clients"][0]["name"], "李经理")

        _, list_search = self.run_cli("client", "list", "--search", "VI", "--limit", "10")
        self.assertEqual(list_search["total"], 1)
        self.assertEqual([client["name"] for client in list_search["clients"]], ["张总"])

        _, stale = self.run_cli("client", "stale", "--days", "3", "--limit", "10")
        self.assertEqual(stale["count"], 1)
        self.assertEqual(stale["clients"][0]["name"], "李经理")

        _, updated = self.run_cli(
            "client",
            "update",
            "--id",
            str(first_id),
            "--data",
            json.dumps(
                {
                    "status": "active",
                    "notes": "已约方案会",
                    "tags": ["vip", "urgent"],
                },
                ensure_ascii=False,
            ),
        )
        self.assertTrue(updated["ok"])
        self.assertEqual(updated["id"], first_id)

        _, list_after_update = self.run_cli("client", "list", "--search", "张总", "--limit", "10")
        self.assertEqual(list_after_update["clients"][0]["status"], "active")
        self.assertEqual(
            list_after_update["clients"][0]["tags"],
            json.dumps(["vip", "urgent"], ensure_ascii=False),
        )

        _, count = self.run_cli("client", "count")
        self.assertEqual(count["total"], 3)
        self.assertEqual(count["by_status"]["active"], 2)
        self.assertEqual(count["by_status"]["closed"], 1)

        failed, failed_data = self.run_cli(
            "client",
            "update",
            "--id",
            "9999",
            "--data",
            json.dumps({"status": "active"}, ensure_ascii=False),
            check=False,
        )
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse(failed_data["ok"])
        self.assertIn("not found", failed_data["error"])

    def test_ledger_commands(self):
        self.run_cli("ledger", "income", "--amount", "1000", "--from", "张总", "--note", "首款")
        self.run_cli("ledger", "expense", "--amount", "200", "--category", "工具", "--note", "Figma")
        self.run_cli("ledger", "expense", "--amount", "50", "--category", "交通", "--note", "打车")

        self.execute_sql("UPDATE ledger SET date=? WHERE rowid=1", ("2024-05-10",))
        self.execute_sql("UPDATE ledger SET date=? WHERE rowid=2", ("2024-05-12",))
        self.execute_sql("UPDATE ledger SET date=? WHERE rowid=3", ("2024-06-01",))

        _, report = self.run_cli("ledger", "report", "--month", "2024-05")
        self.assertEqual(report["month"], "2024-05")
        self.assertEqual(report["income"], 1000.0)
        self.assertEqual(report["expense"], 200.0)
        self.assertEqual(report["net"], 800.0)
        self.assertEqual(report["expense_by_category"], {"工具": 200.0})

        _, records = self.run_cli("ledger", "list", "--limit", "2", "--offset", "0")
        self.assertEqual(records["total"], 3)
        self.assertEqual(records["returned"], 2)
        self.assertEqual([record["category"] for record in records["records"]], ["交通", "工具"])

        failed_income, failed_income_data = self.run_cli(
            "ledger",
            "income",
            "--amount",
            "-1",
            "--from",
            "张总",
            check=False,
        )
        self.assertNotEqual(failed_income.returncode, 0)
        self.assertFalse(failed_income_data["ok"])
        self.assertIn("greater than 0", failed_income_data["error"])

        failed_expense, failed_expense_data = self.run_cli(
            "ledger",
            "expense",
            "--amount",
            "0",
            "--category",
            "工具",
            check=False,
        )
        self.assertNotEqual(failed_expense.returncode, 0)
        self.assertFalse(failed_expense_data["ok"])
        self.assertIn("greater than 0", failed_expense_data["error"])

    def test_content_commands(self):
        _, added = self.run_cli(
            "content",
            "add",
            "--title",
            "Logo 设计避坑指南",
            "--platform",
            "小红书",
            "--type",
            "图文",
            "--status",
            "published",
            "--date",
            "2024-05-20",
        )
        self.assertTrue(added["ok"])

        self.run_cli(
            "content",
            "add",
            "--title",
            "产品冷启动复盘",
            "--platform",
            "公众号",
            "--type",
            "长文",
        )

        _, published = self.run_cli("content", "list", "--status", "published", "--limit", "10")
        self.assertEqual(published["total"], 1)
        self.assertEqual(published["returned"], 1)
        self.assertEqual(published["content"][0]["title"], "Logo 设计避坑指南")

        _, xhs_only = self.run_cli("content", "list", "--platform", "小红书", "--limit", "10")
        self.assertEqual(xhs_only["total"], 1)
        self.assertEqual([item["title"] for item in xhs_only["content"]], ["Logo 设计避坑指南"])

    def test_dashboard_command(self):
        current_month = date.today().strftime("%Y-%m")
        current_publish_date = f"{current_month}-15"

        _, client_one = self.run_cli(
            "client",
            "add",
            "--data",
            json.dumps({"name": "张总", "needs": "品牌VI设计", "status": "active"}, ensure_ascii=False),
        )
        _, client_two = self.run_cli(
            "client",
            "add",
            "--data",
            json.dumps({"name": "李经理", "needs": "官网重做", "status": "potential"}, ensure_ascii=False),
        )
        self.execute_sql(
            "UPDATE clients SET last_contact=? WHERE id=?",
            ("2020-01-01", client_two["id"]),
        )

        self.run_cli("ledger", "income", "--amount", "1500", "--from", "张总", "--note", "首款")
        self.run_cli("ledger", "expense", "--amount", "300", "--category", "工具", "--note", "订阅费")

        self.run_cli(
            "content",
            "add",
            "--title",
            "爆款标题拆解",
            "--platform",
            "小红书",
            "--type",
            "图文",
            "--status",
            "published",
            "--date",
            current_publish_date,
        )
        self.run_cli(
            "content",
            "add",
            "--title",
            "交付流程模板",
            "--platform",
            "公众号",
            "--type",
            "长文",
            "--status",
            "published",
            "--date",
            "2024-01-10",
        )

        _, dashboard = self.run_cli("dashboard")

        self.assertEqual(dashboard["clients"]["total"], 2)
        self.assertEqual(dashboard["clients"]["active"], 1)
        self.assertEqual(dashboard["clients"]["stale_3d"], 1)
        self.assertEqual(dashboard["finance"]["income"], 1500.0)
        self.assertEqual(dashboard["finance"]["expense"], 300.0)
        self.assertEqual(dashboard["finance"]["net"], 1200.0)
        self.assertEqual(dashboard["content"]["total"], 2)
        self.assertEqual(dashboard["content"]["this_month"], 1)
        self.assertEqual(dashboard["stale_clients"][0]["name"], "李经理")


if __name__ == "__main__":
    unittest.main()
