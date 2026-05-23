import os
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv("../.env.bot.secret")
load_dotenv(".env.bot.secret")


class BackendClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("BACKEND_URL", "http://localhost:42002").rstrip("/")
        self.api_key = os.getenv("LMS_API_KEY", "")

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        try:
            response = requests.get(
                f"{self.base_url}{path}",
                headers=self._headers(),
                params=params,
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as error:
            raise RuntimeError(f"connection refused ({self.base_url})") from error
        except requests.exceptions.HTTPError as error:
            status = error.response.status_code if error.response else "unknown"
            text = error.response.text if error.response else str(error)
            raise RuntimeError(f"HTTP {status}: {text[:200]}") from error
        except requests.exceptions.RequestException as error:
            raise RuntimeError(str(error)) from error
    
    def post(self, path: str, json_body: dict[str, Any] | None = None) -> Any:
        try:
            response = requests.post(
                f"{self.base_url}{path}",
                headers=self._headers(),
                json=json_body or {},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            raise RuntimeError(str(error)) from error