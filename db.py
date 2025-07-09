import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DB_POOL = None


async def init_db_pool():
    
    global DB_POOL
    DB_POOL = await asyncpg.create_pool(dsn=os.getenv("SUPABASE_DB_URL"))


# Most recently added language
async def get_user_language_id(discord_id):

    async with DB_POOL.acquire() as conn:

        return await conn.fetchval('''
            SELECT ul.id
            FROM users u
            JOIN user_languages ul ON ul.user_id = u.id
            WHERE u.discord_id = $1
            ORDER BY ul.created_at DESC
            LIMIT 1
            ''', str(discord_id))


async def save_session_summary(user_language_id, summary, message_count):

    async with DB_POOL.acquire() as conn:

        await conn.execute('''
            INSERT INTO session_summaries (user_language_id, summary, message_count)
            VALUES ($1, $2, $3)
            ''', user_language_id, summary, message_count)


async def get_latest_summary(discord_id):

    async with DB_POOL.acquire() as conn:

        return await conn.fetchrow('''
            SELECT ss.summary, ss.created_at
            FROM users u
            JOIN user_languages ul ON ul.user_id = u.id
            JOIN session_summaries ss ON ss.user_language_id = ul.id
            WHERE u.discord_id = $1
            ORDER BY ss.created_at DESC
            LIMIT 1
            ''', str(discord_id))


async def add_user(discord_id):

    async with DB_POOL.acquire() as conn:

        await conn.execute('''
            INSERT INTO users (discord_id)
            VALUES ($1)
            ON CONFLICT (discord_id) DO NOTHING
            ''', str(discord_id))

        if await self.check_user(discord_id):

            return True

        else:

            return False

        return await check_user(discord_id)


async def check_user(discord_id):

    async with DB_POOL.acquire() as conn:

        result = await conn.fetchval('''
            SELECT EXISTS (
                SELECT 1 FROM users WHERE discord_id = $1
            )
            ''', str(discord_id))
        
        if result:

            return True

        else:

            return False


async def add_language(discord_id: str, language: str, native_language: str, cefr_level: Optional[str] = None):

    if cefr_level:

        async with DB_POOL.acquire() as conn:

            await conn.execute('''
                INSERT INTO user_languages (user_id, language, native_language, cefr_level)
                VALUES ($1, $2, $3, $4)
                ''', discord_id, language, native_language, cefr_level)

            if await self.get_user_language_id(discord_id):

                return True

            else:

                return False

    else:
        
        async with DB_POOL.acquire() as conn:

            await conn.execute('''
                INSERT INTO user_languages (user_id, language, native_language, cefr_level)
                VALUES ($1, $2, $3, $4)
                ''', discord_id, language, native_language, 'A1') # If no cefr is provided, assume starter

            if await self.get_user_language_id(discord_id):

                return True

            else:

                return False

        return result
