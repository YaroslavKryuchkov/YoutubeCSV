import statistics
from typing import Dict, List, Any, Tuple
from collections import namedtuple

Video = namedtuple("Video", ["title", "ctr", "retention_rate", "views", "likes", "avg_watch_time"])

class VideoReportGenerator:

    def run(self, report_name: str, videos: List[Video]) -> Tuple[List, List[str]]:
        method_name = report_name.replace('-', '_')
        method = getattr(self, method_name, None)
        if method is None:
            raise ValueError(f"Неизвестный отчёт: {report_name}")
        return method(videos)

    def clickbait(self, videos: List[Video]) -> Tuple[List[Tuple[str, float, float]], List[str]]:
        rows = []
        for video in videos:
            if video.ctr > 15 and video.retention_rate < 40:
                rows.append((video.title, video.ctr, video.retention_rate))

        rows.sort(key=lambda x:x[1], reverse = True)
        headers = ["title", "ctr", "retention_rate"]
        return rows, headers