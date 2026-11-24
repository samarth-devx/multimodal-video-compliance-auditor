import logging
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import yt_dlp

logger = logging.getLogger("downloader")


@contextmanager
def downloaded_video(url: str) -> Iterator[Path]:
    """Download a YouTube video into a temp dir that is always cleaned up."""
    with tempfile.TemporaryDirectory(prefix="mvca_") as tmp:
        path = Path(tmp) / "video.mp4"
        opts = {
            "format": "best",
            "outtmpl": str(path),
            "quiet": True,
            "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
            "http_headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        }
        logger.info("Downloading %s", url)
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
        except yt_dlp.utils.DownloadError as exc:
            raise RuntimeError(f"YouTube download failed: {exc}") from exc
        yield path