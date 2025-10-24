import redis.asyncio as redis
import json
import asyncio
from typing import Callable, Any

REALTIME_CHANNEL = "realtime_updates" 

class RedisClient:
    """
    Handles asynchronous connection, publishing, and subscription to Redis Pub/Sub.
    """
    
    def __init__(self, host: str = 'localhost', port: int = 6379):
        self._host = host
        self._port = port
        self._redis: redis.Redis | None = None
        self._pubsub: redis.client.PubSub | None = None
        print(f"RedisClient initialized for {host}:{port}")

    async def connect(self):
        """
        Establishes the connection to Redis and creates the PubSub client.
        """
        try:
            self._redis = redis.Redis(host=self._host, port=self._port, decode_responses=True)
            await self._redis.ping()
            self._pubsub = self._redis.pubsub()
            print("Successfully connected to Redis.")
        except redis.ConnectionError as e:
            print(f"CRITICAL: Failed to connect to Redis at {self._host}:{self._port}. Real-time features will not work across workers. Error: {e}")
            self._redis = None
            self._pubsub = None

    async def disconnect(self):
        """
        Closes the Redis connection gracefully.
        """
        if self._pubsub:
            await self._pubsub.close()
            self._pubsub = None
        if self._redis:
            await self._redis.close()
            self._redis = None
        print("Redis client disconnected.")

    async def publish(self, data: dict):
        """
        Publishes a dictionary message to the REALTIME_CHANNEL.
        """
        if not self._redis:
            print("Warning: Cannot publish, Redis connection is not established.")
            return

        message = json.dumps(data)
        await self._redis.publish(REALTIME_CHANNEL, message)
        
    async def subscribe_and_listen(self, handler: Callable[[dict], Any]):
        """
        Subscribes to the REALTIME_CHANNEL and starts listening for messages.
        When a message is received, it calls the provided handler function.
        """
        if not self._pubsub:
            print("Warning: Cannot subscribe, PubSub client is not established.")
            return

        await self._pubsub.subscribe(REALTIME_CHANNEL)
        print(f"Subscribed to Redis channel: {REALTIME_CHANNEL}")
        
        while True:
            try:
                message = await self._pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                
                if message and isinstance(message['data'], str):
                    data = json.loads(message['data'])
                    await handler(data)
                
                await asyncio.sleep(0.01) 
                
            except redis.ConnectionError as e:
                print(f"Redis PubSub connection dropped: {e}")
                break 
            except json.JSONDecodeError:
                print(f"Error decoding JSON message: {message['data']}")
            except asyncio.CancelledError:
                print("Redis listener task cancelled.")
                break
            except Exception as e:
                print(f"An unexpected error occurred in Redis listener: {e}")
                break

redis_client = RedisClient()
