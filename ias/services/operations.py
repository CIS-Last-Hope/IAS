from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session

from .. import tables

from ..database import get_session


class OperationService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_list(self, user_id: int) -> List[tables.Operations]:
        operations = (
            self.session
            .query(tables.Operations)
            .filter_by(user_id=user_id)
        )
        return operations
