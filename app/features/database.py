import aiosqlite
from interactions import Extension, listen
from interactions.api import events


class Database(Extension):
    """extension class adding access to a database connection via a db attribute of the bot instance."""

    async def async_start(self) -> None:
        """Connect to db as bot loops starts."""
        self.bot.db = self
        self.bot.db_conn = await aiosqlite.connect("./ee.db")
        await self.populate_tables()

    async def populate_tables(self) -> None:
        """Run the coroutines to create the db tables."""
        await self.todo_table()

    @listen(events.Connect)
    async def bot_connect(self, event: events.Connect) -> None:
        """Reconnect to db when the bot reconnects."""
        print(event)
        if not self.bot.db_conn:
            self.bot.db_conn = await aiosqlite.connect("./ee.db")

    @listen(events.Disconnect)
    async def bot_disconnect(self, event: events.Disconnect) -> None:
        """Disconnect the db when the bot disconnects."""
        print(event)
        await self.bot.db_conn.close()
        self.bot.db = None

    # TO-DO methods

    async def todo_table(self) -> None:
        """Creation of to-do db table."""
        async with self.bot.db_conn.cursor() as cursor:
            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS
            todo (item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NULL,
            item TEXT NOT NULL)
            """)
        await self.bot.db_conn.commit()

    async def todo_add(self, user_id: int, item: str, category: str | None = None) -> None:
        """Add item to to-do table."""
        async with self.bot.db_conn.cursor() as cursor:
            query = """INSERT INTO todo (user_id, category, item) VALUES (?,?,?)"""
            await cursor.execute(query, (user_id, category, item))
        await self.bot.db_conn.commit()

    async def todo_remove(self, user_id: int, item_id: int) -> bool:
        """Remove item from to-do table."""
        async with self.bot.db_conn.cursor() as cursor:
            query = """DELETE from todo WHERE item_id = ? AND user_id = ?"""
            try:
                await cursor.execute(query, (item_id, user_id))
                await self.bot.db_conn.commit()
            except aiosqlite.OperationalError:
                return False
        return True

    async def todo_remove_category(self, user_id: int, category: str) -> bool:
        """Remove an entire category of items from the to-do table."""
        query = """DELETE from todo WHERE user_id = ? AND category = ?"""
        async with self.bot.db_conn.cursor() as cursor:
            try:
                await cursor.execute(query, (user_id, category))
                await self.bot.db_conn.commit()
            except aiosqlite.OperationalError:
                return False
        return True

    async def todo_listall(self, user_id: int, category: str | None = None) -> list[tuple[str]]:
        """Fetch all the users items from the to-do table."""
        async with self.bot.db_conn.cursor() as cursor:
            query = """SELECT item FROM todo WHERE user_id = ? AND category = ?"""
            response = await cursor.execute(query, (user_id, category))
            return await response.fetchall()

    async def todo_get_item(self, user_id: int, item_id: int) -> tuple[str]:
        """Fetch individual item from to-do table."""
        async with self.bot.db_conn.cursor() as cursor:
            query = """SELECT * from todo WHERE user_id = ? AND item_id = ?"""
            response = await cursor.execute(query, (user_id, item_id))
            return await response.fetchone()
