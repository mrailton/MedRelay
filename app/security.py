from typing import cast

from passlib.context import CryptContext  # type: ignore[import-untyped]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(password: str) -> str:
    return cast(str, pwd_context.hash(password))


def verify_password(plain: str, hashed: str) -> bool:
    return cast(bool, pwd_context.verify(plain, hashed))
