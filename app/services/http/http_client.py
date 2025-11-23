import asyncio
from typing import Any, Type, List, Callable
from aiohttp import ClientSession, TCPConnector, ClientTimeout, ClientResponse, ClientError
import socket

import msgspec
import structlog

from app.lib.utils.exceptions import (
    BaseServiceException,
    ErrorBaseServiceBadRequest,
    ErrorBaseServiceRequestTimeout,
    ErrorBaseServiceUnavailable
)
from app.lib.utils.serialization import encode

logger = structlog.get_logger()


class HttpClient:
    _session: ClientSession | None = None
    logger = logger.bind(service="http_client")

    @classmethod
    def inizialize_session(cls) -> None:
        if not cls._session:
            timeout = ClientTimeout(total=30)
            connector = TCPConnector(family=socket.AF_INET, limit_per_host=100)
            cls._session = ClientSession(timeout=timeout, connector=connector, json_serialize=encode)

    @classmethod
    async def close_session(cls) -> None:
        if cls._session:
            await cls._session.close()
            cls._session = None
    
    @classmethod
    async def make_json_request[T](
        cls, url: str, method: str, type_: Type[T],
        is_list: bool = False, headers: dict[str, Any] = None,
        params: dict[str, Any] = None, data: dict[str, Any] = None,
        json: dict[str, Any] = None
    ) -> T:
        async def _parse_msgspec_response[T](response: ClientResponse, type__: Type[T]) -> T:
            response_data = await response.read()

            if type__ is None and 200 <= response.status < 300:
                return None

            return msgspec.json.decode(response_data, type=type__)

        return await cls._make_request(
            url, method, headers, params, data, json,
            response_handler=lambda response: _parse_msgspec_response(
                response=response,
                type__=List[type_] if is_list else type_
            )
        )

    @classmethod
    async def _make_request(cls, url: str, method: str, headers: dict = None,
                            params: dict = None, data: dict = None, json: dict = None,
                            response_handler: Callable[[ClientResponse], Any] = None) -> Any:
        for attempt in range(1, 3):
            try:
                async with cls._session.request(
                        method, url,
                        headers=headers, params=params, data=data, json=json, timeout=ClientTimeout(total=60)
                ) as response:
                    response = await cls._handle_response(response)
                    return await response_handler(response) if response_handler else None

            except asyncio.TimeoutError:
                await cls.logger.aerror("Request timed out")
                if attempt == 3:
                    raise ErrorBaseServiceRequestTimeout
                await asyncio.sleep(2 ** attempt)

            except ClientError as e:
                await cls.logger.aerror(f"Client error: {e}")
                raise ErrorBaseServiceBadRequest(f"Client error: {e}")

            except Exception as e:
                if isinstance(e, BaseServiceException):
                    await cls.logger.aerror(f"Unexpected error: {e}")
                    raise e
                await cls.logger.aerror(f"Service error: {e}")
                raise BaseServiceException


    @classmethod
    async def _handle_response(cls, response: ClientResponse) -> ClientResponse:
        """Обработка ответа от сервера"""
        if 200 <= response.status < 300:
            return response
        elif 400 <= response.status < 500:
            await cls.logger.aerror(f"Client error: {response.status}, text: {await response.text()}")
            raise ErrorBaseServiceBadRequest(f"Client error: {response.status}")
        elif 500 <= response.status < 600:
            await cls.logger.aerror(f"Server error: {response.status}")
            raise ErrorBaseServiceUnavailable(f"Server error: {response.status}")
