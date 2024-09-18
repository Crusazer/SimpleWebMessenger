from fastapi import APIRouter, Depends

from src.core.database.models.user import User
from src.core.schemas.user_schemas import SUserMe
from src.dependencies import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=SUserMe)
async def get_my_user_info(
    user: User = Depends(get_current_active_user),
) -> SUserMe:
    return SUserMe.from_orm(user)
