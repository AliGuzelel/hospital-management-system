import httpx
from fastapi import HTTPException
class ProxyService:
    @staticmethod
    async def forward(method: str, url: str, body=None, params=None):
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.request(method, url, json=body, params=params)
            if res.status_code >= 400:
                raise HTTPException(status_code=res.status_code, detail=res.text)
            return res.json()
