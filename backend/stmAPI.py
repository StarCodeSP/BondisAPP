import os
import logging
from time import perf_counter
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class STMAPIError(RuntimeError):
    """Error al consultar la API del transporte de Montevideo."""


class STMClient:
    def __init__(
        self,
        base_url: str | None = None,
        token_url: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        access_token: str | None = None,
        timeout: float = 20.0,
    ):
        self.base_url = (base_url or os.getenv("STM_API_BASE_URL", "https://api.montevideo.gub.uy/api/transportepublico")).rstrip("/")
        self.token_url = token_url or os.getenv("STM_TOKEN_URL", "https://mvdapi-auth.montevideo.gub.uy/token")
        self.client_id = client_id or os.getenv("STM_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("STM_CLIENT_SECRET")
        self.access_token = access_token or os.getenv("STM_ACCESS_TOKEN")
        self.timeout = timeout
        self._session = httpx.Client(timeout=self.timeout, follow_redirects=True)

    def _get_token(self) -> str:
        if self.access_token:
            return self.access_token

        if not self.client_id or not self.client_secret:
            raise STMAPIError(
                "Falta OAuth2: define STM_ACCESS_TOKEN o STM_CLIENT_ID y STM_CLIENT_SECRET en el .env"
            )

        try:
            response = self._session.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise STMAPIError(f"No se pudo obtener el token de acceso del STM: {exc}") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise STMAPIError("El token del STM no devolvió JSON válido") from exc

        token = payload.get("access_token")
        if not token:
            raise STMAPIError(f"No se encontró access_token en la respuesta del STM: {payload}")

        self.access_token = token
        return token

    def _request(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        token = self._get_token()
        url = f"{self.base_url}{path}"

        try:
            response = self._session.get(
                url,
                params=params,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise STMAPIError(f"No se pudo consultar la API del STM: {exc}") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise STMAPIError("La API del STM devolvió un JSON inválido") from exc

        if isinstance(payload, dict) and payload.get("error"):
            raise STMAPIError(str(payload["error"]))

        return payload

    def get_lines(self) -> list[Any]:
        return self._request("/buses")

    def get_busstops(self) -> list[Any]:
        return self._request("/buses/busstops")

    def get_stops(self, query: str | None = None, stop_id: str | None = None) -> list[Any]:
        params: dict[str, Any] = {}
        if query:
            params["query"] = query
        if stop_id:
            params["stop_id"] = stop_id
        return self._request("/buses/busstops", params=params)

    def get_busstops_by_line(self, line: str) -> list[Any]:
        return self._request("/buses/busstops", params={"lines": line})

    def get_bus_lines_for_stop(self, busstop_id: int) -> list[Any]:
        return self._request(f"/buses/busstops/{busstop_id}/lines")

    def close(self) -> None:
        self._session.close()

stm_client = STMClient()

class transporteRestClient():
    def __init__(self, base_url: str | None = None, timeout: float = 20.0):
        self.base_url = (base_url or os.getenv("TRANSPORTERESTCLIENT_BASE_URL", "https://api.montevideo.gub.uy/transporteRest")).rstrip("/")
        self.timeout = timeout
        self._session = httpx.Client(timeout=self.timeout, follow_redirects=True)
    
    def _request(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        started_at = perf_counter()
        logger.info("Consulta TransporteREST iniciada: GET %s params=%s", url, params or {})

        try:
            response = self._session.get(
                url,
                params=params,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            elapsed_ms = (perf_counter() - started_at) * 1000
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            logger.error(
                "Consulta TransporteREST fallida: GET %s params=%s status=%s duracion_ms=%.2f error=%s",
                url,
                params or {},
                status_code or "sin_respuesta",
                elapsed_ms,
                exc,
                exc_info=True,
            )
            raise STMAPIError(f"No se pudo consultar la API del transporteRest: {exc}") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            elapsed_ms = (perf_counter() - started_at) * 1000
            logger.error(
                "Consulta TransporteREST devolvio JSON invalido: GET %s params=%s status=%s duracion_ms=%.2f",
                url,
                params or {},
                response.status_code,
                elapsed_ms,
                exc_info=True,
            )
            raise STMAPIError("La API del transporteRest devolvió un JSON inválido") from exc

        if isinstance(payload, dict) and payload.get("error"):
            elapsed_ms = (perf_counter() - started_at) * 1000
            logger.error(
                "TransporteREST devolvio un error de aplicacion: GET %s params=%s status=%s duracion_ms=%.2f error=%s",
                url,
                params or {},
                response.status_code,
                elapsed_ms,
                payload["error"],
            )
            raise STMAPIError(str(payload["error"]))

        logger.info(
            "Consulta TransporteREST exitosa: GET %s params=%s status=%s duracion_ms=%.2f",
            url,
            params or {},
            response.status_code,
            (perf_counter() - started_at) * 1000,
        )
        return payload

    def nextAtBusstop(self, busstop_id: int) -> list[Any]:
        return self._request(f"/siguientesParada/{busstop_id}")

transporteRest_client = transporteRestClient()

__all__ = ["STMClient", "STMAPIError", "stm_client", "transporteRestClient", "transporteRest_client"]
