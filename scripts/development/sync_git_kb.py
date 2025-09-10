# scripts/development/sync_git_kb.py
import argparse
import json
import re
import subprocess
from pathlib import Path

# --- Конфигурация ---
PAGES_DIR = "pages"
STORY_FILE_PATTERN = re.compile(r"^STORY-.*\.md$")
STORY_ID_PATTERN = re.compile(r"STORY-([A-Z0-9\-]+)")
STATUS_PATTERN = re.compile(r"status::\s*\[\[(DONE|TODO|DOING)\]\]", re.IGNORECASE)


class GitKbSync:
    """
    Скрипт для синхронизации статусов User Stories в базе знаний
    с их реальным состоянием в Git.
    """

    def __init__(self, project_root: Path, report_path: Path):
        self.project_root = project_root
        self.report_path = report_path
        self.pages_path = project_root / PAGES_DIR
        self.mismatches: list[dict[str, str]] = []

    def _find_story_files(self) -> list[Path]:
        """Находит все файлы User Story в директории pages/."""
        if not self.pages_path.is_dir():
            print(f"❌ Error: Directory '{self.pages_path}' not found.")
            return []
        return [
            f for f in self.pages_path.glob("*.md") if STORY_FILE_PATTERN.match(f.name)
        ]

    def _get_story_status(self, file_path: Path) -> str | None:
        """Извлекает статус из файла User Story."""
        content = file_path.read_text(encoding="utf-8")
        match = STATUS_PATTERN.search(content)
        return match.group(1).upper() if match else None

    def _check_git_commit_exists(self, story_id: str) -> bool:
        """Проверяет, существует ли коммит с ID задачи."""
        try:
            # Ищем коммит, в сообщении которого есть ID задачи (например, "feat: ... (STORY-API-1)")
            result = subprocess.run(
                ["git", "log", "--grep", story_id, "--oneline"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return bool(result.stdout.strip())
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def run_sync(self):
        """Основной метод для запуска процесса синхронизации."""
        story_files = self._find_story_files()
        print(f"ℹ️  Found {len(story_files)} User Story files to analyze.")

        for story_file in story_files:
            story_id_match = STORY_ID_PATTERN.search(story_file.stem)
            if not story_id_match:
                continue

            story_id = story_file.stem  # e.g. STORY-API-1
            status = self._get_story_status(story_file)

            if not status:
                print(
                    f"⚠️  Warning: Could not find status for '{story_file.name}'. Skipping."
                )
                continue

            commit_exists = self._check_git_commit_exists(story_id)

            # --- Логика проверки расхождений ---
            if status == "DONE" and not commit_exists:
                self.mismatches.append(
                    {
                        "file_path": str(story_file.relative_to(self.project_root)),
                        "story_id": story_id,
                        "issue": "Status is DONE, but no corresponding Git commit was found.",
                        "recommended_action": "Change status to [[TODO]] or investigate.",
                    }
                )

            elif status in ["TODO", "DOING"] and commit_exists:
                self.mismatches.append(
                    {
                        "file_path": str(story_file.relative_to(self.project_root)),
                        "story_id": story_id,
                        "issue": f"Status is {status}, but a closing Git commit already exists.",
                        "recommended_action": "Change status to [[DONE]].",
                    }
                )

        print(f"✅ Analysis complete. Found {len(self.mismatches)} mismatches.")

    def write_report(self):
        """Записывает найденные расхождения в JSON-отчет."""
        with open(self.report_path, "w", encoding="utf-8") as f:
            json.dump(self.mismatches, f, indent=4)
        print(f"📝 Report successfully generated at '{self.report_path}'.")


def main():
    parser = argparse.ArgumentParser(
        description="Synchronize User Story statuses between Logseq Knowledge Base and Git commits."
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        required=True,
        help="The path to save the JSON report file.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="The root directory of the project.",
    )
    args = parser.parse_args()

    syncer = GitKbSync(project_root=args.project_root, report_path=args.report_path)
    syncer.run_sync()
    syncer.write_report()


if __name__ == "__main__":
    main()
