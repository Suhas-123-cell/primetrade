import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://testnet.binancefuture.com"


class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _get(self, path: str, params: dict = None, signed: bool = False) -> dict:
        params = params or {}
        if signed:
            params = self._sign(params)
        url = BASE_URL + path
        safe_params = {k: v for k, v in params.items() if k != "signature"}
        logger.debug("GET %s | params=%s", path, safe_params)
        try:
            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            logger.debug("Response: %s", data)
            return data
        except requests.exceptions.HTTPError as exc:
            body = exc.response.text if exc.response is not None else "no body"
            logger.error("HTTP %s on GET %s | %s", exc.response.status_code, path, body)
            raise
        except requests.exceptions.RequestException as exc:
            logger.error("Network error on GET %s | %s", path, exc)
            raise

    def _post(self, path: str, params: dict = None) -> dict:
        params = params or {}
        params = self._sign(params)
        url = BASE_URL + path
        safe_params = {k: v for k, v in params.items() if k != "signature"}
        logger.debug("POST %s | params=%s", path, safe_params)
        try:
            resp = self.session.post(url, data=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            logger.debug("Response: %s", data)
            return data
        except requests.exceptions.HTTPError as exc:
            body = exc.response.text if exc.response is not None else "no body"
            logger.error("HTTP %s on POST %s | %s", exc.response.status_code, path, body)
            raise
        except requests.exceptions.RequestException as exc:
            logger.error("Network error on POST %s | %s", path, exc)
            raise

    def ping(self) -> bool:
        try:
            self._get("/fapi/v1/ping")
            return True
        except Exception:
            return False

    def get_server_time(self) -> int:
        data = self._get("/fapi/v1/time")
        return data["serverTime"]

    def place_order(self, **params) -> dict:
        return self._post("/fapi/v1/order", params)

    def get_account(self) -> dict:
        return self._get("/fapi/v2/account", signed=True)
