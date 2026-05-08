import argparse
import csv
from tabulate import tabulate

from typing import Dict, List, Any

from video_report_generator import VideoReportGenerator, Video

def load(files : List[str]) -> List[Video]:
    data: List[Video] = []
    for filename in files:
        try:
            with open(filename, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    video = Video(
                        title=row["title"],
                        ctr=float(row["ctr"]),
                        retention_rate=float(row["retention_rate"]),
                        views=int(row["views"]),
                        likes=int(row["likes"]),
                        avg_watch_time=float(row["avg_watch_time"])
                    )
                    data.append(video)
        except FileNotFoundError:
            print(f"Файл не найден {filename}") 
        except Exception as e:
            print(f"Ошибка при чтении файле {filename}: {e}") 
    return data

def main():
    parser = argparse.ArgumentParser(description="Приложение для обработки csv-файлов с метриками видео на YouTube.")
    parser.add_argument("--files", nargs="+", required=True, help="Список файлов для обработки.")
    parser.add_argument("--report", required=True, help="Название отчёта.")
    args = parser.parse_args()

    data = load(args.files)
    generator = VideoReportGenerator()

    table_data, headers = generator.run(args.report, data)

    print(tabulate(table_data, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    main()