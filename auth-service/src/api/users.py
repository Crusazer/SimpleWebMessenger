from fastapi import APIRouter, Depends

from ..database.schemas.user_schemas import SUserMe
from ..dependencies import get_current_active_user
from ..database.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=SUserMe)
async def get_my_user_info(
    user: User = Depends(get_current_active_user),
) -> SUserMe:
    return SUserMe.from_orm(user)
