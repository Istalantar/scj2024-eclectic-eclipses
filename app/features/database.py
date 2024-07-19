import aiosqlite
from interactions import Extension, listen
from interactions.api import events


class Database(Extension):
    """extension class adding access to a database connection via a db attribute of the bot instance."""

    async def async_start(self) -> None:
        """Connect to db as bot loops starts."""
        self.bot.db = await aiosqlite.connect("./ee.db")
        await self.populate_db()

    async def populate_db(self) -> None:
        """Creation of db table."""
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS
            todo(user_id INTEGER PRIMARY KEY, tasks BLOB)
            """)
        await self.bot.db.commit()

    @listen(events.Connect)
    async def bot_connect(self, event: events.Connect) -> None:
        """Reconnect to db when the bot reconnects."""
        print(event)
        if not self.bot.db:
            self.bot.db = await aiosqlite.connect("./ee.db")

    @listen(events.Disconnect)
    async def bot_disconnect(self, event: events.Disconnect) -> None:
        """Disconnect the db when the bot disconnects."""
        print(event)
        await self.bot.db.close()
        self.bot.db = None
