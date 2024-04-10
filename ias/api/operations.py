from typing import List

from fastapi import APIRouter
from fastapi import Depends

from ..models import User
from ..models.operations import Operation
from ..services.auth import get_current_user
from ..services.operations import OperationService

router = APIRouter(
    prefix='/operations',
)


@router.get('/', response_model=List[Operation])
def get_operations(service: OperationService = Depends(),
                   user: User = Depends(get_current_user)):
    return service.get_list()
