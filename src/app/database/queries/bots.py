import asyncpg


class BotActions:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def add_bot(
        self,
        bot_name: str,
        bot_username: str,
        bot_status: str = "True"
    ):
        query = """
            INSERT INTO bots (bot_name, bot_username, bot_status) VALUES($1, $2, $3)      
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, bot_name, bot_username, bot_status)

    async def get_bot(self, bot_username: str):
        query = """
            SELECT * FROM bots WHERE bot_username = $1
        """
        async with self.pool.acquire() as conn:

            return await conn.fetchrow(query, bot_username)

    async def get_all_bots(self):
        query = """
            SELECT * FROM bots
        """
        async with self.pool.acquire() as conn:

            return await conn.fetch(query)

    async def update_bot_status(self, new_bot_status: str, bot_username: str):
        query = """
            UPDATE bots SET bot_status = $1 WHERE bot_username = $2
        """
        async with self.pool.acquire() as conn:

            await conn.execute(query, new_bot_status, bot_username)

    async def delete_bot(self, bot_username: str):
        query = """
            DELETE FROM bots WHERE bot_username = $1 
        """
        async with self.pool.acquire() as conn:

            await conn.execute(query, bot_username)