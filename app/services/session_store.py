"""Thread-safe in-memory storage for active interview sessions."""

from __future__ import annotations

from datetime import datetime
from threading import RLock
from typing import Dict, Optional

from app.models.interview import InterviewSession


class SessionStore:
    """Manage interview sessions for the lifetime of the running API process."""

    def __init__(self) -> None:
        self._sessions: Dict[str, InterviewSession] = {}
        self._lock = RLock()

    def create(self, session: InterviewSession) -> InterviewSession:
        """Store a new session and reject duplicate session IDs."""
        with self._lock:
            if session.session_id in self._sessions:
                raise ValueError(f"Session already exists: {session.session_id}")

            session.updated_at = datetime.utcnow()
            self._sessions[session.session_id] = session.model_copy(deep=True)
            return self._sessions[session.session_id].model_copy(deep=True)

    def get(self, session_id: str) -> Optional[InterviewSession]:
        """Return a session copy, or None if the ID is unknown."""
        with self._lock:
            session = self._sessions.get(session_id)
            return session.model_copy(deep=True) if session else None

    def save(self, session: InterviewSession) -> InterviewSession:
        """Save changes to an existing session."""
        with self._lock:
            if session.session_id not in self._sessions:
                raise KeyError(f"Session not found: {session.session_id}")

            session.updated_at = datetime.utcnow()
            self._sessions[session.session_id] = session.model_copy(deep=True)
            return self._sessions[session.session_id].model_copy(deep=True)

    def delete(self, session_id: str) -> bool:
        """Delete a session; returns False if it was already absent."""
        with self._lock:
            return self._sessions.pop(session_id, None) is not None