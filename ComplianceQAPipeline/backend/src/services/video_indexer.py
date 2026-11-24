import logging
import time
from pathlib import Path

import requests
from azure.identity import DefaultAzureCredential

from backend.src.config import Settings
from backend.src.schemas import Evidence

logger = logging.getLogger("video-indexer")

ARM_SCOPE = "https://management.azure.com/.default"
POLL_INTERVAL_S = 20
TIMEOUT_S = 15 * 60
HTTP_TIMEOUT_S = 60


class VideoIndexerClient:
    """Thin wrapper over Azure Video Indexer: upload -> wait -> parse into Evidence."""

    def __init__(self, settings: Settings):
        self._s = settings
        self._credential = DefaultAzureCredential()
        self._base = f"https://api.videoindexer.ai/{settings.vi_location}/Accounts/{settings.vi_account_id}"

    def analyze(self, video_path: Path, name: str) -> Evidence:
        video_id = self._upload(video_path, name)
        logger.info("Uploaded. Azure video id: %s", video_id)
        return self._parse(self._wait_until_processed(video_id))

    # ---- auth ----
    def _account_token(self) -> str:
        arm_token = self._credential.get_token(ARM_SCOPE).token
        url = (
            f"https://management.azure.com/subscriptions/{self._s.subscription_id}"
            f"/resourceGroups/{self._s.resource_group}"
            f"/providers/Microsoft.VideoIndexer/accounts/{self._s.vi_name}"
            f"/generateAccessToken?api-version=2024-01-01"
        )
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {arm_token}"},
            json={"permissionType": "Contributor", "scope": "Account"},
            timeout=HTTP_TIMEOUT_S,
        )
        if not resp.ok:
            raise RuntimeError(f"Failed to get Video Indexer token: {resp.text}")
        return resp.json()["accessToken"]

    # ---- upload / poll ----
    def _upload(self, path: Path, name: str) -> str:
        params = {
            "accessToken": self._account_token(),
            "name": name,
            "privacy": "Private",
            "indexingPreset": "Default",
        }
        with path.open("rb") as f:
            resp = requests.post(f"{self._base}/Videos", params=params, files={"file": f}, timeout=600)
        if not resp.ok:
            raise RuntimeError(f"Azure upload failed: {resp.text}")
        return resp.json()["id"]

    def _wait_until_processed(self, video_id: str) -> dict:
        deadline = time.monotonic() + TIMEOUT_S
        while time.monotonic() < deadline:
            resp = requests.get(
                f"{self._base}/Videos/{video_id}/Index",
                params={"accessToken": self._account_token()},
                timeout=HTTP_TIMEOUT_S,
            )
            data = resp.json()
            state = data.get("state")
            if state == "Processed":
                return data
            if state == "Failed":
                raise RuntimeError("Video indexing failed in Azure.")
            if state == "Quarantined":
                raise RuntimeError("Video quarantined (copyright / content policy).")
            logger.info("Indexing state: %s, waiting %ss", state, POLL_INTERVAL_S)
            time.sleep(POLL_INTERVAL_S)
        raise TimeoutError(f"Video indexing did not finish within {TIMEOUT_S}s.")

    # ---- parsing ----
    @staticmethod
    def _timed_lines(items) -> list[str]:
        lines = []
        for item in items:
            text = (item.get("text") or "").strip()
            if not text:
                continue
            instances = item.get("instances") or []
            start = (instances[0].get("start", "") if instances else "").split(".")[0]
            lines.append(f"[{start}] {text}" if start else text)
        return lines

    def _parse(self, index: dict) -> Evidence:
        insights = [v.get("insights", {}) for v in index.get("videos", [])]
        transcript = self._timed_lines(i for ins in insights for i in ins.get("transcript", []))
        ocr = self._timed_lines(i for ins in insights for i in ins.get("ocr", []))
        duration = index.get("summarizedInsights", {}).get("duration", {}).get("seconds")
        return Evidence(
            transcript="\n".join(transcript),
            ocr_text=ocr,
            metadata={"duration_seconds": duration, "platform": "youtube"},
        )