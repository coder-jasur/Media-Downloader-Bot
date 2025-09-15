import logging

from asyncpg import Connection

loger = logging.getLogger(__name__)


async def create_database_tables(conn: Connection):
    try:
        await create_users_table(conn)
        await create_channels_table(conn)
        await create_bots_table(conn)
        await create_table_referrals(conn)
    except Exception as e:
        loger.exception(e)


async def create_users_table(conn: Connection):
    query = """ 
        CREATE TABLE IF NOT EXISTS users(
            tg_id BIGINT PRIMARY KEY NOT NULL,
            username TEXT NOT NULL,
            status TEXT NOT NULL,
            language TEXT NOT NULL,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
    """
    await conn.execute(query)


async def create_channels_table(conn: Connection):
    query = """ 
        CREATE TABLE IF NOT EXISTS channels(
            channel_id BIGINT PRIMARY KEY NOT NULL,
            channel_name TEXT NOT NULL,
            channel_username TEXT NOT NULL,
            channel_status TEXT NOT NULL,
            message TEXT,
            channel_url TEXT,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
    """
    await conn.execute(query)

async def create_bots_table(conn: Connection) -> None:
    query = """
        CREATE TABLE IF NOT EXISTS bots(
            bot_name TEXT NOT NULL,
            bot_username TEXT NOT NULL,
            bot_status TEXT NOT NULL,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
    """

    await conn.execute(query)


async def create_table_referrals(conn: Connection) -> None:
    query = """
        CREATE TABLE IF NOT EXISTS referrals (
            referral_id TEXT PRIMARY KEY NOT NULL,
            referral_name TEXT NOT NULL,
            referral_members_count INTEGER NOT NULL,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
    """

    await conn.execute(query)
