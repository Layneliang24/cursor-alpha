from __future__ import annotations

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status
from .response import error


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is not None:
        # 包装DRF标准异常
        message = response.data.get('detail') if isinstance(response.data, dict) else None
        return error(message=message or '请求错误', errors=response.data, http_status=response.status_code)

    # 未被DRF捕获的异常：返回500
    return error(message='服务器内部错误', http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)


