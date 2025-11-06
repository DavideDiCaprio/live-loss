"""
Asynchronous Redis Pub/Sub Client.

This module provides the RedisClient class for managing an asynchronous
connection to Redis, specifically designed for real-time message
"""
import redis.asyncio as redis
import json
import asyncio
from typing import Callable, Any, Awaitable, Final

# --- Module-Level Constants ---

REALTIME_CHANNEL: Final[str] = "realtime_updates"
"""The specific Redis Pub/Sub channel used for broadcasting real-time updates."""

# --- Redis Client Class ---

class RedisClient:
    """
    Handles asynchronous connection, publishing, and subscription to Redis Pub/Sub.

    Provides a high-level wrapper for managing the connection,
    publishing JSON-serialized messages, and running a persistent
    listener loop that dispatches messages to a callback handler.
    """

    def __init__(self, host: str = 'localhost', port: int = 6379):
        """
        Initializes the RedisClient configuration parameters.

        Note: This method only configures the client and does not establish
        an actual connection. Call `connect()` to start the connection.

        Args:
            host: The **hostname** or IP address of the Redis server.
            port: The **port number** of the Redis server.
        """
        self._host = host
        self._port = port
        self._redis: redis.Redis | None = None
        self._pubsub: redis.client.PubSub | None = None
        print(f"RedisClient initialized for {host}:{port}")

    async def connect(self):
        """
        Establishes the asynchronous connection to Redis.

        Pings the server to verify the connection and initializes
        the dedicated PubSub client.
        """
        try:
            # decode_responses=True ensures Redis returns strings, not bytes
            self._redis = redis.Redis(
                host=self._host,
                port=self._port,
                decode_responses=True
            )
            await self._redis.ping()
            self._pubsub = self._redis.pubsub()
            print("Successfully connected to Redis.")
        except redis.ConnectionError as e:
            print(
                f"CRITICAL: Failed to connect to Redis at {self._host}:{self._port}. "
                f"Real-time features will not work. Error: {e}"
            )
            self._redis = None
            self._pubsub = None

    async def disconnect(self):
        """
        Closes the PubSub and underlying Redis connections gracefully.
        """
        if self._pubsub:
            await self._pubsub.close()
            self._pubsub = None
        if self._redis:
            await self._redis.close()
            self._redis = None
        print("Redis client disconnected.")

    async def publish(self, data: dict[str, Any]):
        """
        Publishes a dictionary message to the REALTIME_CHANNEL.

        The data dictionary is serialized to a JSON string before publishing.

        Args:
            data: The **message payload** (a dictionary) to serialize and send.
        """
        if not self._redis:
            print("Warning: Cannot publish, Redis connection is not established.")
            return

        try:
            message = json.dumps(data)
            await self._redis.publish(REALTIME_CHANNEL, message)
        except redis.ConnectionError as e:
            print(f"Error publishing message (connection lost): {e}")
        except TypeError as e:
            print(f"Error serializing message data to JSON: {e}")

    async def subscribe_and_listen(
        self,
        handler: Callable[[dict[str, Any]], Awaitable[Any]]
    ):
        """
        Subscribes to the channel and runs a persistent message listener loop.

        This method blocks execution (runs indefinitely), waiting for messages.
        It deserializes the JSON payload and calls the provided asynchronous
        handler with the resulting dictionary.

        Args:
            handler: An **async callable** that takes one argument (the
                     deserialized message dictionary) and is awaited.
        """
        if not self._pubsub:
            print("Warning: Cannot subscribe, PubSub client is not established.")
            return

        await self._pubsub.subscribe(REALTIME_CHANNEL)
        print(f"Subscribed to Redis channel: {REALTIME_CHANNEL}")

        while True:
            try:
                # Wait for a message with a timeout
                message = await self._pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0
                )

                # Check if a valid message was received
                if message and isinstance(message.get('data'), str):
                    try:
                        data = json.loads(message['data'])
                        # Asynchronously process the message
                        await handler(data)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON message: {message['data']}")

                # Short sleep to yield control, preventing a busy-loop
                await asyncio.sleep(0.01)

            except redis.ConnectionError as e:
                print(f"Redis PubSub connection dropped: {e}. Stopping listener.")
                break
            except asyncio.CancelledError:
                print("Redis listener task cancelled.")
                break
            except Exception as e:
                print(f"An unexpected error occurred in Redis listener: {e}")
                break  # Stop listener on unexpected errors

# --- Singleton Instance ---

redis_client: Final[RedisClient] = RedisClient()
"""
A **singleton instance** of the RedisClient to be shared across the application.
"""