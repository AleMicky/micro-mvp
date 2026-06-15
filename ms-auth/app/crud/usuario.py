from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate


class CRUDUsuario:
    async def get(self, db: AsyncSession, id: int) -> Usuario | None:
        stmt = (
            select(Usuario)
            .options(selectinload(Usuario.roles).selectinload(Rol.permisos))
            .where(Usuario.id == id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        solo_activos: bool = False,
    ) -> list[Usuario]:
        stmt = select(Usuario).options(
            selectinload(Usuario.roles).selectinload(Rol.permisos)
        )
        if solo_activos:
            stmt = stmt.where(Usuario.activo.is_(True))
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_username_or_email(
        self, db: AsyncSession, identificador: str
    ) -> Usuario | None:
        stmt = (
            select(Usuario)
            .options(selectinload(Usuario.roles).selectinload(Rol.permisos))
            .where(
                or_(
                    Usuario.nombre_usuario == identificador,
                    Usuario.correo == identificador,
                )
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, nombre_usuario: str) -> Usuario | None:
        stmt = select(Usuario).where(Usuario.nombre_usuario == nombre_usuario)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, correo: str) -> Usuario | None:
        stmt = select(Usuario).where(Usuario.correo == correo)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, obj_in: UsuarioCreate) -> Usuario:
        usuario = Usuario(
            nombre_completo=obj_in.nombre_completo,
            nombre_usuario=obj_in.nombre_usuario,
            correo=obj_in.correo,
            password_hash=hash_password(obj_in.password),
            activo=obj_in.activo,
        )
        db.add(usuario)
        await db.commit()
        return await self.get(db, usuario.id)  # type: ignore[arg-type]

    async def update(
        self, db: AsyncSession, db_obj: Usuario, obj_in: UsuarioUpdate
    ) -> Usuario:
        data = obj_in.model_dump(exclude_unset=True)
        password = data.pop("password", None)
        for field, value in data.items():
            setattr(db_obj, field, value)
        if password:
            db_obj.password_hash = hash_password(password)
        await db.commit()
        return await self.get(db, db_obj.id)  # type: ignore[arg-type]

    async def soft_delete(self, db: AsyncSession, db_obj: Usuario) -> None:
        db_obj.activo = False
        await db.commit()

    async def update_last_login(self, db: AsyncSession, usuario: Usuario) -> None:
        usuario.ultimo_login_en = datetime.now(UTC)
        await db.commit()

    async def assign_roles(
        self, db: AsyncSession, usuario: Usuario, rol_ids: list[int]
    ) -> Usuario:
        roles = []
        for rol_id in rol_ids:
            rol = await db.get(Rol, rol_id)
            if rol and rol.activo:
                roles.append(rol)

        usuario.roles = roles
        await db.commit()
        return await self.get(db, usuario.id)  # type: ignore[arg-type]

    async def add_roles(
        self, db: AsyncSession, usuario: Usuario, rol_ids: list[int]
    ) -> Usuario:
        roles_actuales = {rol.id for rol in usuario.roles}
        for rol_id in rol_ids:
            if rol_id in roles_actuales:
                continue
            rol = await db.get(Rol, rol_id)
            if rol and rol.activo:
                usuario.roles.append(rol)
        await db.commit()
        await db.refresh(usuario, attribute_names=["roles"])
        return await self.get(db, usuario.id)  # type: ignore[arg-type]

    @staticmethod
    def get_role_codes(usuario: Usuario) -> list[str]:
        return [rol.codigo for rol in usuario.roles if rol.activo]

    @staticmethod
    def get_permission_codes(usuario: Usuario) -> list[str]:
        permisos: set[str] = set()
        for rol in usuario.roles:
            if not rol.activo:
                continue
            for permiso in rol.permisos:
                if permiso.activo:
                    permisos.add(permiso.codigo)
        return sorted(permisos)


crud_usuario = CRUDUsuario()
