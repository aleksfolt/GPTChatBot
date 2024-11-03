import aiosqlite

DB_PATH = "user_data.db"


async def initialize_db():
    """крч here создается database"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_model (
                user_id INTEGER PRIMARY KEY,
                model TEXT
            )
        """)
        await db.commit()


async def set_user_model(user_id: int, model: str):
    """set выбранную model to database иди нахуй я английский плохо знаю"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO user_model (user_id, model) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET model = excluded.model
        """, (user_id, model))
        await db.commit()


async def get_user_model(user_id: int) -> str:
    """если честно хз че это, из названия функции понятно"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT model FROM user_model WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None
