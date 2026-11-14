"""Thread-safe in-process event fan-out for live task monitoring.

This is a local MVP transport. Replace the hub with NATS for multi-process deployments.
"""
from __future__ import annotations

import queue
import threading
from datetime import datetime, timezone
from typing import Any
from uuid import UUID


class EventHub:
    def __init__(self, history_size: int = 500) -> None:
        self._lock = threading.Lock()
        self._subscribers: set[queue.Queue[dict[str, Any]]] = set()
        self._history: queue.deque[dict[str, Any]] | None = None
        from collections import deque
        self._history = deque(maxlen=history_size)

    def publish(self, event_type: str, task_id: UUID | str | None, data: dict[str, Any]) -> None:
        event = {
            "type": event_type,
            "task_id": str(task_id) if task_id is not None else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        with self._lock:
            self._history.append(event)
            subscribers = tuple(self._subscribers)
        for subscriber in subscribers:
            try:
                subscriber.put_nowait(event)
            except queue.Full:
                # A slow terminal must not block task execution.
                pass

    def subscribe(self, max_queue: int = 200) -> queue.Queue[dict[str, Any]]:
        subscriber: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=max_queue)
        with self._lock:
            self._subscribers.add(subscriber)
        return subscriber

    def unsubscribe(self, subscriber: queue.Queue[dict[str, Any]]) -> None:
        with self._lock:
            self._subscribers.discard(subscriber)

    def snapshot(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._history)


event_hub = EventHub()
