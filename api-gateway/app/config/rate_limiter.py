import time
from collections import defaultdict, deque
class InMemoryRateLimiter:
    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window
        self.requests = defaultdict(deque)
    def allow(self, key: str) -> bool:
        now = time.time()
        q = self.requests[key]
        while q and q[0] < now - self.window:
            q.popleft()
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True
