from datetime import datetime, timedelta
from typing import AsyncGenerator

import asyncpg


class UserDataBaseActions:

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def add_user(self, tg_id: int, username: str, language: str, status: str = "unblocked"):
        query = """
            INSERT INTO users(tg_id, username, status, language) VALUES($1, $2, $3, $4)      
        """
        async with self.pool.acquire() as conn:

            await conn.execute(query, tg_id, username, status, language)


    async def get_user(self, tg_id: int):
        query = """
            SELECT * FROM users WHERE tg_id = $1
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, tg_id)

    async def get_all_user(self):
        query = """
            SELECT * FROM users 
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(query)

    async def update_user_status(self, new_status: str, tg_id: int):
        query = """
            UPDATE users SET status = $1 WHERE tg_id = $2
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, new_status, tg_id)

    async def update_user_lang(self, new_lang: str, tg_id: int):
        query = """
            UPDATE users SET language = $1 WHERE tg_id = $2
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, new_lang, tg_id)

    async def get_user_ids_batch(self, offset: int, limit: int = 5000) -> list[int]:

        query = """
            SELECT tg_id FROM users
            ORDER BY tg_id -- Tartiblash muhim, chunki LIMIT/OFFSET ishonchli ishlashi uchun
            LIMIT $1 OFFSET $2
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, limit, offset)

        return [row['tg_id'] for row in rows]

    async def iterate_user_ids(
        self,
        batch_size: int = 5000
    ) -> AsyncGenerator[tuple[list[int], int], None]:

        offset = 0

        while True:
            user_ids = await self.get_user_ids_batch(offset, batch_size)

            if not user_ids:
                break

            yield user_ids, offset
            offset += len(user_ids)

    async def get_user_statistics(self):
        now = datetime.utcnow()
        one_day_ago = now - timedelta(days=1)
        one_week_ago = now - timedelta(days=7)
        one_month_ago = now - timedelta(days=30)
        one_year_ago = now - timedelta(days=365)

        async with self.pool.acquire() as conn:
            users = await conn.fetch("SELECT created_at FROM users")

        total_users = len(users)
        today_users = 0
        week_users = 0
        month_users = 0
        year_users = 0

        for (joined_at_str,) in users:
            joined_at = datetime.fromisoformat(str(joined_at_str))
            if joined_at > one_day_ago:
                today_users += 1
            if joined_at > one_week_ago:
                week_users += 1
            if joined_at > one_month_ago:
                month_users += 1
            if joined_at > one_year_ago:
                year_users += 1

        return {
            "today": today_users,
            "week": week_users,
            "month": month_users,
            "year": year_users,
            "total": total_users
        }
