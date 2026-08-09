from datetime import datetime
from typing import Dict, Optional

from app.models.interview import InterviewSession


class SessionStore:

    def __init__(self):

        self.sessions: Dict[
            str,
            InterviewSession
        ] = {}

    def create(
        self,
        session: InterviewSession
    ) -> InterviewSession:

        self.sessions[
            session.session_id
        ] = session

        return session

    def get(
        self,
        session_id: str
    ) -> Optional[InterviewSession]:

        return self.sessions.get(session_id)

    def save(
        self,
        session: InterviewSession
    ) -> InterviewSession:

        session.updated_at = datetime.utcnow()

        self.sessions[
            session.session_id
        ] = session

        return session

    def delete(
        self,
        session_id: str
    ):

        self.sessions.pop(
            session_id,
            None
        )