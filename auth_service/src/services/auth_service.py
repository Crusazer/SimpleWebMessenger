import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.models.user import User
from src.core.repositories.user_repository import UserRepository
from src.core.schemas.token import SToken
from src.core.schemas.user_schemas import SUserCreate
from src.exceptions import (
    UserAuthenticationException,
    NotMatchPasswordException,
    InvalidTokenException,
    InvalidDeviceException,
    UserNotFoundException,
    DeviceNotExistsException,
)
from src.utils.auth import validate_password, hash_password
from src.utils.location import get_location_by_ip
from .token_service import TokenService
from ..core.repositories.device_repository import DeviceRepository
from ..core.schemas.device import DeviceDTO, SDeviceCreate, SDeviceGet

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db_session: AsyncSession):
        self._session: AsyncSession = db_session
        self._repository = UserRepository(self._session)
        self._token_service = TokenService(self._session)

    async def _register_new_device(
        self,
        user_id: uuid.UUID,
        user_agent: str,
        jti: uuid.UUID,
        ip: str,
    ) -> DeviceDTO:
        location: str = await get_location_by_ip(ip)
        if location is None:
            raise InvalidDeviceException

        device: SDeviceCreate = SDeviceCreate(
            user_id=user_id, user_agent=user_agent, ip=ip, location=location, jti=jti
        )
        device_repository: DeviceRepository = DeviceRepository(self._session)
        device: DeviceDTO = await device_repository.create(device)
        return device

    def _generate_tokens(self, user: User) -> tuple[SToken, uuid.UUID]:
        access_token: str = self._token_service.create_access_token(user)
        refresh_token, jti = self._token_service.create_refresh_token(user)
        return SToken(access_token=access_token, refresh_token=refresh_token), jti

    async def login(
        self, email: str, password: str, user_agent: str, ip: str
    ) -> SToken:
        """Check password and authenticate user via create user device"""
        user = await self._repository.get_user_by_field(email=email)
        if not user:
            raise UserNotFoundException

        if not validate_password(password, user.password):
            raise UserAuthenticationException

        tokens, jti = self._generate_tokens(user)
        device: DeviceDTO = await self._register_new_device(
            user_id=user.id, user_agent=user_agent, jti=jti, ip=ip
        )
        logger.info("User %s logged in from device: %s", user.email, device.id)
        return tokens

    async def logout(self, refresh_token: str) -> None:
        """Logout user via delete user device"""
        payload = self._token_service.get_current_token_payload(refresh_token)

        device_repository: DeviceRepository = DeviceRepository(self._session)
        try:
            await device_repository.delete_by_user_id_and_jti(
                user_id=payload["sub"], jti=payload["jti"]
            )
        except ValueError:
            raise InvalidTokenException

    async def refresh_jwt_token(
        self, refresh_token: str, user: User, user_agent: str
    ) -> SToken:
        """Generate new pair and add old refresh to blacklist"""
        payload = self._token_service.get_current_token_payload(refresh_token)
        device_repository: DeviceRepository = DeviceRepository(self._session)

        try:
            device: DeviceDTO = await device_repository.get(user.id, payload.get("jti"))

            # If user_agent not match this mean someone else tries to refresh the user JWT.
            if device.user_agent != user_agent:
                await device_repository.delete_by_user_id_and_jti(
                    user_id=user.id, jti=payload["jti"]
                )
                raise InvalidDeviceException

            tokens, jti = self._generate_tokens(user)
            await device_repository.update(
                user_id=user.id, current_jti=payload["jti"], jti=jti
            )
        except ValueError:
            raise InvalidTokenException

        return tokens

    async def register_user(
        self, email: str, password: str, re_password: str, ip: str, user_agent: str
    ):
        """Create new user if not exists and passwords match and add new user device"""
        # Check input params
        if password != re_password:
            raise NotMatchPasswordException

        if not user_agent or not ip:
            raise InvalidDeviceException

        # Create new user
        hashed_password = hash_password(password)
        s_user = SUserCreate(email=email, password=hashed_password)

        if await self._repository.get_user_by_field(email=s_user.email) is not None:
            raise UserAuthenticationException(
                detail="A user with this email already exists."
            )

        user = await self._repository.create_user(s_user)
        tokens, jti = self._generate_tokens(user)

        # Create new user device
        device: DeviceDTO = await self._register_new_device(
            user.id, user_agent, jti, ip
        )
        logger.info("Register user %s with device: %s", email, device.user_agent)
        return tokens

    async def get_my_devices(self, user: User) -> list[SDeviceGet]:
        """Return list of all user's devices '"""
        device_repository: DeviceRepository = DeviceRepository(self._session)
        devices = await device_repository.get_user_devices(user.id)
        return devices

    async def logout_device(self, device_id: uuid.UUID, user: User) -> None:
        """Check permission and delete user device"""
        device_repository: DeviceRepository = DeviceRepository(self._session)
        try:
            await device_repository.delete_by_user_id_and_device_id(user.id, device_id)
        except ValueError:
            raise DeviceNotExistsException

    async def logout_all_devices(self, user: User) -> None:
        """Logout from all user devices"""
        device_repository: DeviceRepository = DeviceRepository(self._session)
        try:
            await device_repository.delete_all_user_devices(user.id)
        except ValueError:
            raise DeviceNotExistsException
