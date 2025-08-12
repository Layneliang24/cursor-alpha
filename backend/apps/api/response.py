from __future__ import annotations

from typing import Any, Dict
from rest_framework.response import Response
from rest_framework import status


def success(data: Any = None, message: str = "OK", http_status: int = status.HTTP_200_OK) -> Response:
    payload: Dict[str, Any] = {
        "success": True,
        "message": message,
        "data": data,
    }
    return Response(payload, status=http_status)


def error(message: str = "Error", code: str | None = None, errors: Any = None,
          http_status: int = status.HTTP_400_BAD_REQUEST) -> Response:
    payload: Dict[str, Any] = {
        "success": False,
        "message": message,
    }
    if code:
        payload["code"] = code
    if errors is not None:
        payload["errors"] = errors
    return Response(payload, status=http_status)


