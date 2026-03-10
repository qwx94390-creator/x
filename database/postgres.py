from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base, Trade


class Database:
    def __init__(self, url: str) -> None:
        self.engine = create_async_engine(url, echo=False)
        self._session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def connect(self) -> None:
        return None

    async def create_tables(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def insert_trade(self, trade_data: dict) -> None:
        async with self._session() as session:
            session.add(Trade(**trade_data))
            await session.commit()
