import asyncpg


class ReferalDataBaseActions:

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def add_referal(self, referal_id: str, referal_name: str, referal_member_count: int = 0):
        query = """
            INSERT INTO referals (referal_id, referal_name, referal_members_count) VALUES ($1, $2, $3);
        """
        async with self.pool.acquire() as conn:

            return await conn.execute(query, referal_id, referal_name, referal_member_count)

    async def get_referal(self, referal_id: str):
        query = """
            SELECT *
            FROM referals
            WHERE referal_id = $1
        """
        async with self.pool.acquire() as conn:

            return await conn.fetchrow(query, referal_id)

    async def get_all_referals(self):
        query = """
            SELECT * FROM referals
        """
        async with self.pool.acquire() as conn:

            return await conn.fetch(query)

    async def increment_referal_members_count(self, referral_id: str):
        query = """
            UPDATE referals 
            SET referal_members_count = referal_members_count + 1
            WHERE referal_id = $1
        """
        async with self.pool.acquire() as conn:

            return await conn.execute(query, referral_id)

    async def delite_referal(self, referal_id: str):
        query = """
            DELETE FROM referals WHERE referal_id = $1
        """
        async with self.pool.acquire() as conn:

            await conn.execute(query, referal_id)


