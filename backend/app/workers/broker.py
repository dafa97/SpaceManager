import dramatiq
from dramatiq.brokers.redis import RedisBroker
from app.core.config import settings

# Configure Redis broker for Dramatiq
redis_broker = RedisBroker(url=settings.REDIS_URL)
dramatiq.set_broker(redis_broker)
