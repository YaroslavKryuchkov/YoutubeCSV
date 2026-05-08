import pytest
import csv
import tempfile
from pathlib import Path
from typing import List
from collections import namedtuple

from video_report_generator import VideoReportGenerator, Video

# ----- Фикстуры -----

@pytest.fixture
def sample_videos():
    return [
        Video("A", 20.0, 30.0, 100, 10, 120.0),   # подходит: ctr>15, ret<40
        Video("B", 10.0, 50.0, 200, 20, 90.0),    # не подходит: ctr=10
        Video("C", 18.0, 35.0, 150, 15, 110.0),   # подходит
        Video("D", 15.0, 39.0, 300, 30, 80.0),    # не подходит: ctr=15 (не >)
        Video("E", 16.0, 40.0, 250, 25, 95.0),    # не подходит: ret=40 (не <)
    ]


@pytest.fixture
def temp_csv_file():
    def _make(data_rows: List[dict]):
        fd, path = tempfile.mkstemp(suffix='.csv', text=True)
        with open(fd, 'w', newline='', encoding='utf-8') as f:
            if data_rows:
                writer = csv.DictWriter(f, fieldnames=data_rows[0].keys())
                writer.writeheader()
                writer.writerows(data_rows)
            else:
                # пустой файл только с заголовками
                writer = csv.DictWriter(f, fieldnames=["title", "ctr", "retention_rate", "views", "likes", "avg_watch_time"])
                writer.writeheader()
        return path
    return _make

# ----- Тесты для VideoReportGenerator -----

def test_run_known_report(sample_videos):
    gen = VideoReportGenerator()
    rows, headers = gen.run("clickbait", sample_videos)
    # Ожидаем: только A (ctr=20, ret=30) и C (ctr=18, ret=35), отсортированы по убыванию CTR
    assert len(rows) == 2
    assert rows[0][0] == "A"   # первый по CTR 20 > 18
    assert rows[1][0] == "C"
    assert headers == ["title", "ctr", "retention_rate"]


def test_run_unknown_report(sample_videos):
    gen = VideoReportGenerator()
    with pytest.raises(ValueError, match="Неизвестный отчёт: unknown"):
        gen.run("unknown", sample_videos)


def test_run_report_with_dashes(sample_videos):
    #Метод с дефисом должен преобразовываться в подчёркивание.
    gen = VideoReportGenerator()

    # Временно добавим метод test_method
    def test_method(self, videos):
        return [("ok",)], ["h1"]
    gen.test_method = test_method.__get__(gen)

    rows, headers = gen.run("test-method", sample_videos)
    assert rows == [("ok",)]


def test_clickbait_empty():
    gen = VideoReportGenerator()
    rows, headers = gen.clickbait([])
    assert rows == []
    assert headers == ["title", "ctr", "retention_rate"]


def test_clickbait_filtering():
    videos = [
        Video("V1", 16.0, 30.0, 1,1,1),   # подходит: 16>15 and 30<40
        Video("V2", 15.1, 39.9, 1,1,1),   # подходит: 15.1>15 и 39.9<40
        Video("V3", 15.0, 39.0, 1,1,1),   # не подходит: ctr не >15
        Video("V4", 20.0, 40.0, 1,1,1),   # не подходит: ret не <40
        Video("V5", 10.0, 30.0, 1,1,1),   # не подходит: ctr <15
    ]
    gen = VideoReportGenerator()
    rows, _ = gen.clickbait(videos)
    titles = [r[0] for r in rows]
    assert titles == ["V1", "V2"]   # порядок по убыванию CTR: 16.0 и 15.1


def test_clickbait_sorting():
    videos = [
        Video("V1", 18.0, 30.0, 1,1,1),
        Video("V2", 22.0, 35.0, 1,1,1),
        Video("V3", 17.0, 38.0, 1,1,1),
    ]
    gen = VideoReportGenerator()
    rows, _ = gen.clickbait(videos)
    assert [r[0] for r in rows] == ["V2", "V1", "V3"]  # 22 > 18 > 17


def test_clickbait_returns_correct_types():
    videos = [Video("Test", 20.0, 30.0, 100, 10, 50.0)]
    gen = VideoReportGenerator()
    rows, headers = gen.clickbait(videos)
    assert isinstance(rows, list)
    assert len(rows[0]) == 3
    assert isinstance(rows[0][0], str)
    assert isinstance(rows[0][1], float)
    assert isinstance(rows[0][2], float)