# run_fuzzy_system.py
"""
Запуск нечеткой экспертной системы подбора кандидатов
"""

import os
import sys

# Добавляем пути для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
lab1_path = os.path.join(current_dir, "..", "Lab_1")
lab2_path = os.path.join(current_dir, "..", "Lab_2")

sys.path.append(lab1_path)
sys.path.append(lab2_path)

from fuzzy_main import main

if __name__ == "__main__":
    try:
        print("="*60)
        print("ЗАПУСК НЕЧЕТКОЙ ЭКСПЕРТНОЙ СИСТЕМЫ")
        print("="*60)
        main()
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        print("Убедитесь, что все необходимые модули установлены и пути настроены правильно.")
    except Exception as e:
        print(f"Критическая ошибка: {e}")