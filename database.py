from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, BigInteger
import os

# 📌 Строка подключения из переменной окружения Railway
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Async SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=False)
Base = declarative_base()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 🔹 Модель таблицы
class User(Base):
    __tablename__ = "users"
    user_id = Column(BigInteger, primary_key=True)

# ✅ Создание таблицы
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ✅ Добавление пользователя
async def add_user(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            session.add(User(user_id=user_id))
            await session.commit()

# ✅ Получение всех пользователей
async def get_all_users():
    async with async_session() as session:
        result = await session.execute(
            User.__table__.select()
        )
        users = result.scalars().all()
        return [user.user_id for user in users]