import aiosqlite
from interactions import Extension, listen
from interactions.api.events import Connect, Disconnect


class Database(Extension):
    """extension class adding access to a database connection via a db attribute of the bot instance."""

    async def async_start(self) -> None:
        """Connect to db as bot loops starts."""
        self.bot.db = self
        self.bot.db_conn = await aiosqlite.connect("./ee.db")
        print("Database extension loaded")
        await self.populate_tables()

    async def populate_tables(self) -> None:
        """Run the coroutines to create the db tables."""
        await self.todo_table()
        await self.timezone_table()

    @listen(Connect)
    async def bot_connect(self, event: Connect) -> None:
        """Reconnect to db when the bot reconnects."""
        print(event)
        if not self.bot.db_conn:
            self.bot.db_conn = await aiosqlite.connect("./ee.db")

    @listen(Disconnect)
    async def bot_disconnect(self, event: Disconnect) -> None:
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
            todo (item TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            category TEXT NULL)
            """)
        await self.bot.db_conn.commit()

    async def todo_add(self, user_id: int, item: str, category: str | None = None) -> bool:
        """Add item to to-do table.

        :param user_id: Discord user id.
        :param item: To be added ToDo.
        :param category: (optional) Category of the item.
        :return: True if query succeeded, False otherwise.
        """
        async with self.bot.db_conn.cursor() as cursor:
            query = """INSERT INTO todo (user_id, category, item) VALUES (?,?,?)"""
            try:
                await cursor.execute(query, (user_id, category, item))
            except aiosqlite.IntegrityError:
                return False
        await self.bot.db_conn.commit()
        return True

    async def todo_remove(self, user_id: int, item: str) -> bool:
        """Remove item from to-do table.

        :param user_id: Discord user id.
        :param item: To be removed ToDo.
        :return: True if query succeeded, False otherwise.
        """
        async with self.bot.db_conn.cursor() as cursor:
            query = """DELETE from todo WHERE item = ? AND user_id = ?"""
            try:
                await cursor.execute(query, (item, user_id))
                await self.bot.db_conn.commit()
            except aiosqlite.OperationalError:
                return False
        return True

    async def todo_remove_category(self, user_id: int, category: str) -> bool:
        """Remove an entire category of items from the to-do table.

        :param user_id: Discord user id.
        :param category: To be removed Category.
        :return: True if query succeeded, False otherwise.
        """
        query = """DELETE from todo WHERE user_id = ? AND category = ?"""
        async with self.bot.db_conn.cursor() as cursor:
            try:
                await cursor.execute(query, (user_id, category))
                await self.bot.db_conn.commit()
            except aiosqlite.OperationalError:
                return False
        return True

    async def todo_listall(self, user_id: int, category: str | None = None) -> list[tuple[str]]:
        """Fetch all the users items from the to-do table.

        :param user_id: Discord user id.
        :param category: (optional) Category of the item.
        :return: List of the users ToDos.
        """
        async with self.bot.db_conn.cursor() as cursor:
            if category:
                query = """SELECT item FROM todo WHERE user_id = ? AND category = ?"""
                response = await cursor.execute(query, (user_id, category))
            else:
                query = """SELECT item FROM todo WHERE user_id = ? AND category is NULL"""
                response = await cursor.execute(query, (user_id,))
            return await response.fetchall()

    async def todo_get_item(self, user_id: int, item: str) -> tuple[str]:
        """Fetch individual item from to-do table."""
        async with self.bot.db_conn.cursor() as cursor:
            query = """SELECT * from todo WHERE user_id = ? AND item = ?"""
            response = await cursor.execute(query, (user_id, item))
            return await response.fetchone()

    # Timezone methods
    async def timezone_table(self) -> None:
        """Creation of timezone db table."""
        async with self.bot.db_conn.cursor() as cursor:
            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS
            timezone (user_id INTEGER PRIMARY KEY,
            tz TEXT NOT NULL)
            """)
        await self.bot.db_conn.commit()

    async def get_timezones(self) -> list[tuple[int, str]]:
        """Return all stored timezone data."""
        async with self.bot.db_conn.cursor() as cursor:
            cur = await cursor.execute("""SELECT * from timezone""")
            return await cur.fetchall()

    async def set_timezone(self, user_id: int, tz: str) -> None:
        """Add or update users timezone to db.

        :param user_id: Discord user id.
        :param tz: IANA timezone name.
        """
        async with self.bot.db_conn.cursor() as cursor:
            query = """SELECT * from timezone WHERE user_id = ?"""
            ret = await cursor.execute(query, (user_id,))
            ret = await ret.fetchall()

            if len(ret) == 0:
                query = """INSERT INTO timezone (user_id, tz) VALUES (?,?)"""
                await cursor.execute(query, (user_id, tz))
            else:
                query = """UPDATE timezone SET tz = ? WHERE user_id = ?"""
                await cursor.execute(query, (tz, user_id))
        await self.bot.db_conn.commit()
