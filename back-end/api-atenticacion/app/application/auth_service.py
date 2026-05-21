from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.infrastructure.user_repository import UserRepository
from app.domain.user import User
from app.schemas.user_schema import UserRegister, UserLogin
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
user_repository = UserRepository()

class AuthService:

    def hash_password(self, password: str) -> str:
        password = password[:72]
        return pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        plain = plain[:72]
        return pwd_context.verify(plain, hashed)

    def create_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    def register(self, db: Session, data: UserRegister) -> User:
        if user_repository.exists_by_email(db, data.email):
            raise ValueError("El email ya está registrado")
        
        hashed = self.hash_password(data.password)
        new_user = User(
            full_name=data.full_name,
            email=data.email,
            password_hash=hashed,
            role=data.role
        )
        return user_repository.create(db, new_user)

    def login(self, db: Session, data: UserLogin) -> str:
        user = user_repository.get_by_email(db, data.email)
        if not user:
            raise ValueError("Credenciales inválidas")
        if not self.verify_password(data.password, user.password_hash):
            raise ValueError("Credenciales inválidas")
        if not user.is_active:
            raise ValueError("Usuario inactivo")
        
        token = self.create_token({"sub": str(user.id), "email": user.email, "role": user.role})
        return token

    def get_current_user(self, db: Session, token: str) -> User:
        payload = self.decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Token inválido")
        user = user_repository.get_by_id(db, user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        return user