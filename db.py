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

        lang_id = await conn.fetchval('''
            SELECT ul.id
            FROM users u
            JOIN user_languages ul ON ul.user_id = u.id
            WHERE u.discord_id = $1
            ORDER BY ul.created_at DESC
            LIMIT 1
            ''', str(discord_id))

        return await conn.fetchval('''
            SELECT ul.learning_language
            FROM users u
            JOIN user_languages ul ON ul.user_id = u.id
            WHERE u.discord_id = $1 AND ul.id = $2
            ''', str(discord_id), str(lang_id))


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


async def delete_language(discord_id: str; learning_language: str):

    async with DB_POOL.acquire() as conn:

        user_id = await conn.fetchval('''
        SELECT id from FROM user WHERE discord_id = $1
        ''', str(discord_id))

        if not user_id:

            print(f"User with discord_id {discord_id} does not exist.") # Debugging line

            return False

        native_language, cefr_level = await conn.fetchval('''
            SELECT native_language, cefr_levels
            FROM user_languages
            WHERE user_id, learning_language = $1, $2
            ''', str user_id, str learning_language)

        await conn.execute('''
            DELETE FROM user_languages (user_id, learning_language, native_language, cefr_level)
            VALUES ($1, $2, $3, $4)
            ''', str user_id, str learning_language, str native_language, str cefr_level)

        if not await self.get_user_language_id(discord_id):

            return True

        else:

            return False
    

async def lang_exists_check(discord_id: str, language: str):

    async with DB_POOL.acquire() as conn:

        user_id = await conn.fetchval('''
            SELECT id FROM users WHERE discord_id = $1
            ''', str(discord_id))

        if not user_id:

            print(f"User with discord_id {discord_id} does not exist.") # Debugging line

            return False

        result = await conn.fetchval('''
            SELECT EXISTS (
                SELECT 1 FROM user_languages
                WHERE user_id = $1 AND language = $2)
            ''', str(user_id), str(language))
        
        if result:

            return True

        else:

            return False

# insert a language to db after onboarding quiz
async def post_onboarding_insert(discord_id: str, language: str, native_language: str, cefr_level: Optional[str] = None):

    async with DB_POOL.acquire() as conn:

        user_id = await conn.fetchval('''
            SELECT id FROM users WHERE discord_id = $1
            ''', str(discord_id))

        if not user_id:

            print(f"User with discord_id {discord_id} does not exist.") # Debugging line

            return False
        
        if not cefr_level:

            cefr_level = 'A1' # safety net

        try:

            result = await conn.execute('''
                INSERT INTO user_languages (user_id, learning_language, native_language, cefr_level)
                VALUES ($1, $2, $3, $4)
            ''', str(user_id), str(language), str(native_language), str(cefr_level))

            return True
        
        except Exception as e:

            print(f'Error inserting data to database: {e}')

            return False

# change cefr after reexamination
async def change_cefr(discord_id: str, language: str, new_cefr_level: str):

    async with DB_POOL.acquire() as conn:

        user_id = await conn.fetchval('''
            SELECT id FROM users WHERE discord_id = $1
            ''', str(discord_id))

        if not user_id:

            print(f"User with discord_id {discord_id} does not exist.") # Debugging line

            return False

        result = await conn.execute('''
            UPDATE user_languages
            SET cefr_level = $1
            WHERE user_id = $2 AND learning_language = $3
            ''', str(new_cefr_level), str(user_id), str(language))

        if result == 'UPDATE 1':

            return True

        elif result == 'UPDATE 0':

            print('No change to the database has been done. Either no user-language combination found or query faulty.')

            return False

        else:

            print('Multiple rows affected. Check for mistake.')

            return False
