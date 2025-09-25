from dataclasses import dataclass
from typing import Any, Literal, Optional

from aiohttp import ClientSession


@dataclass
class Response:
    status: int
    body: Any


class Request:
    def __init__(self, client_session: Optional[ClientSession] = None) -> None:
        self.client_session = client_session

    async def close(self):
        if self.client_session:
            await self.client_session.close()

    async def request(
        self,
        method: Literal["GET", "POST"],
        url: str,
        return_method: Literal["json", "text", "read"],
        **kwargs: Any
    ):
        if not self.client_session:
            self.client_session = ClientSession()

        async with self.client_session.request(method, url, **kwargs) as response:
            return Response(response.status, await getattr(response, return_method)())

    async def get(
        self, url: str, return_method: Literal["json", "text", "read"], **kwargs: Any
    ):
        return await self.request("GET", url, return_method, **kwargs)

    async def post(
        self, url: str, return_method: Literal["json", "text", "read"], **kwargs: Any
    ):
        return await self.request("POST", url, return_method, **kwargs)

    async def __aenter__(self, *args: Any, **kwargs: Any) -> "Request":
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self.close()
