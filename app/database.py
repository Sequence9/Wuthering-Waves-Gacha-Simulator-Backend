import os
import redis
import json

class RedisManager:
    def __init__(self):
        # These env vars are provided by docker-compose
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", 6379))
        self.client = redis.Redis(
            host=self.host, 
            port=self.port, 
            decode_responses=True
        )

    # 5-star pity methods
    def get_pity(self, user_id: str, banner_id: str) -> int:
        return int(self.client.get(f"pity:{user_id}:{banner_id}") or 0)

    def set_pity(self, user_id: str, banner_id: str, count: int):
        self.client.set(f"pity:{user_id}:{banner_id}", count)

    # NEW: 4-star pity methods
    def get_pity_4(self, user_id: str, banner_id: str) -> int:
        """Retrieves current 4-star pity count (0-9)."""
        return int(self.client.get(f"pity4:{user_id}:{banner_id}") or 0)

    def set_pity_4(self, user_id: str, banner_id: str, count: int):
        """Sets the 4-star pity count."""
        self.client.set(f"pity4:{user_id}:{banner_id}", count)

    # 50/50 guarantee methods
    def get_guarantee(self, user_id: str, banner_id: str) -> bool:
        return self.client.get(f"guarantee:{user_id}:{banner_id}") == "true"

    def set_guarantee(self, user_id: str, banner_id: str, status: bool):
        val = "true" if status else "false"
        self.client.set(f"guarantee:{user_id}:{banner_id}", val)