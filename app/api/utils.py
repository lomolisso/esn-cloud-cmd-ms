import httpx
import json
import redis

# --- Gateway API ---

class GatewayAPIHandler:
    def __init__ (self, url: str):
        self.url = url

    async def get(self, endpoint: str):
        async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
            response = await client.get(
                f"{self.url}{endpoint}",
            )
            return response
    
    async def post_json(self, endpoint: str, data: dict):
        async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
            response = await client.post(
                f"{self.url}{endpoint}",
                json=data
            )
            return response
    
# --- Command Responses ---
def store_response_in_redis(redis_client: redis.Redis, command_uuid: str, response: dict):
    redis_client.set(command_uuid, json.dumps(response))

def retrieve_response_from_redis(redis_client: redis.Redis, command_uuid: str):
    response = redis_client.get(command_uuid)
    if response:
        redis_client.delete(command_uuid)
        return json.loads(response)
    return None