from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_refresh_token
from app.models.refresh_token import RefreshToken


class CRUDRefreshToken:
    async def create(
        self,
        db: AsyncSession,
        *,
        usuario_id: int,
        token: str,
        expiracion_en: datetime,
    ) -> RefreshToken:
        refresh = RefreshToken(
            usuario_id=usuario_id,
            token_hash=hash_refresh_token(token),
            expiracion_en=expiracion_en,
        )
        db.add(refresh)
        await db.commit()
        await db.refresh(refresh)
        return refresh

    async def get_valid(
        self, db: AsyncSession, token: str, usuario_id: int | None = None
    ) -> RefreshToken | None:
        token_hash = hash_refresh_token(token)
        now = datetime.now(UTC)
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revocado.is_(False),
            RefreshToken.expiracion_en > now,
        )
        if usuario_id is not None:
            stmt = stmt.where(RefreshToken.usuario_id == usuario_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke(self, db: AsyncSession, refresh_token: RefreshToken) -> None:
        refresh_token.revocado = True
        refresh_token.revocado_en = datetime.now(UTC)
        await db.commit()

    async def revoke_by_token(
        self, db: AsyncSession, token: str, usuario_id: int
    ) -> bool:
        refresh = await self.get_valid(db, token, usuario_id)
        if not refresh:
            return False
        await self.revoke(db, refresh)
        return True


crud_refresh_token = CRUDRefreshToken()
