# scripts/development/generate_logseq_config.py
from pathlib import Path


def generate_logseq_config():
    """
    Анализирует структуру проекта и генерирует/обновляет logseq/config.edn,
    автоматически скрывая все директории, не относящиеся к базе знаний.
    """
    project_root = Path(__file__).parent.parent.parent
    logseq_dir = project_root / "logseq"
    config_path = logseq_dir / "config.edn"

    # --- "Белый список": эти папки ВСЕГДА должны быть видны в Logseq ---
    knowledge_base_dirs = {
        "journals",
        "logseq",
        "pages",
        "assets",
    }

    print("Запуск генерации config.edn для Logseq...")
    logseq_dir.mkdir(exist_ok=True)

    # --- Сканируем корневую директорию проекта ---
    root_items = [item.name for item in project_root.iterdir() if item.is_dir()]

    # --- Определяем папки, которые нужно скрыть ---
    # Это все папки, которые НЕ входят в наш "белый список"
    hidden_dirs = sorted(
        [f'"{item}"' for item in root_items if item not in knowledge_base_dirs]
    )

    hidden_dirs_str = " ".join(hidden_dirs)
    print(f"Обнаружены следующие директории для скрытия: {hidden_dirs_str}")

    # --- Формируем содержимое config.edn ---
    # Мы целенаправленно перезаписываем только ключ :hidden,
    # чтобы не затереть другие возможные настройки.

    config_content = ""
    if config_path.exists():
        print("Найден существующий config.edn. Сохраняю другие настройки...")
        lines = config_path.read_text(encoding="utf-8").splitlines()
        # Отфильтровываем старые настройки :hidden
        other_lines = [line for line in lines if not line.strip().startswith(":hidden")]
        config_content = "\n".join(other_lines).strip()

    if config_content:
        config_content += "\n"

    config_content += f" ;; Этот блок сгенерирован автоматически скриптом generate_logseq_config.py\n :hidden [{hidden_dirs_str}]"

    # --- Записываем файл ---
    config_path.write_text(config_content, encoding="utf-8")
    print(f"\nФайл '{config_path}' успешно обновлен.")
    print("\nСодержимое config.edn:")
    print("--------------------")
    print(config_content)
    print("--------------------")


if __name__ == "__main__":
    generate_logseq_config()
