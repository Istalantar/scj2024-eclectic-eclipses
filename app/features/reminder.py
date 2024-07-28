import asyncio
import datetime
import zoneinfo

from interactions import (
    AutocompleteContext,
    Client,
    Extension,
    OptionType,
    SlashCommand,
    SlashCommandChoice,
    SlashCommandOption,
    SlashContext,
    listen,
    slash_option,
)
from interactions.api.events import Ready


class Reminder(Extension):
    """Alarm / Reminder extension."""

    def __init__(self, bot: Client) -> None:
        self.bot = bot
        print("Reminder extension loaded")
        self.tz = None

    @listen(Ready)
    async def bot_ready(self) -> None:
        """Retrieve timezone data when the bot is ready."""
        utz = await self.bot.db.get_timezones()
        self.tz = UserTimezones(utz)

    base = SlashCommand(name="remindme", description="Alarm base group")
    set = SlashCommand(name="set", description="Set base group")

    @base.subcommand(
        sub_cmd_name="at",
        sub_cmd_description="add an alarm at a specific date and time",
        options=[
            SlashCommandOption(
                name="date_time",
                description="date and time in the format 'YYYY-MM-DD HH:MM'",
                required=True,
                type=OptionType.STRING,
            ),
            SlashCommandOption(
                name="message",
                description="message to be sent when the alarm is triggered",
                required=False,
                type=OptionType.STRING,
            ),
        ],
    )
    async def add_at(
        self,
        ctx: SlashContext,
        date_time: str,
        message: str = "Your previously set reminder has been triggered",
    ) -> None:
        """Create a reminder for a specific time of the day based on a time input."""
        if not self.tz.has_user(ctx.author.id):
            await ctx.send("unknown timezone, please set your timezone with /set timezone")
            return

        try:
            user_tz = self.tz.get_timezone(ctx.author.id)
            user_tz_obj = zoneinfo.ZoneInfo(user_tz)
            reminder_time = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M").replace(tzinfo=user_tz_obj)
            delay = seconds_until_time(reminder_time)
            await ctx.send(
                f"I'll remind you on {reminder_time.strftime('%A, %B %d, %Y at %H:%M')} "
                f"(<t:{int(reminder_time.timestamp())}:R>)",
            )
            await asyncio.sleep(delay)
            await ctx.send(f"{ctx.author.mention} REMINDER: {message}")
        except ValueError:
            await ctx.send("Invalid date and time format. Please use 'YYYY-MM-DD HH:MM' format.")

    @base.subcommand(
        sub_cmd_name="in",
        sub_cmd_description="add a reminder for a certain amount of time from now",
        options=[
            SlashCommandOption(
                name="duration",
                description="integer representing the number of units",
                required=True,
                type=OptionType.INTEGER,
            ),
            SlashCommandOption(
                name="units",
                description="units representing a measurement of time",
                required=True,
                type=OptionType.STRING,
                choices=[
                    SlashCommandChoice(name="Seconds", value="sec"),
                    SlashCommandChoice(name="Minutes", value="min"),
                    SlashCommandChoice(name="Hours", value="hour"),
                ],
            ),
            SlashCommandOption(
                name="message",
                description="message to be sent when the alarm is triggered",
                required=False,
                type=OptionType.STRING,
            ),
        ],
    )
    async def add_in(
        self,
        ctx: SlashContext,
        units: str,
        duration: int,
        message: str = "Your previously set reminder has been triggered",
    ) -> None:
        """Create a reminder for a specific time of the day based on a duration input."""
        await ctx.send(f"I'll remind you {duration} {units}(s) from now")
        match units:
            case "sec":
                await asyncio.sleep(duration)
            case "min":
                await asyncio.sleep(duration * 60)
            case "hour":
                await asyncio.sleep(duration * 3600)
            case _:
                pass
        await ctx.send(f"{ctx.author.mention} REMINDER: {message}")

    @set.subcommand(
        sub_cmd_name="timezone",
        sub_cmd_description="set your timezone",
    )
    @slash_option(
        name="timezone",
        description="Start typing your timezone. e.g America/Los_Angeles or Europe/London",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True,
    )
    async def set_timezone(
        self,
        ctx: SlashContext,
        timezone: str,
    ) -> None:
        """Set timezone based on user selection."""
        # timezone selected by the user from the autocomplete list
        self.tz.add_user(ctx.author.id, timezone)
        await self.bot.db.set_timezone(ctx.author.id, timezone)
        await ctx.send(f"timezone set to {timezone}")

    @set_timezone.autocomplete("timezone")
    async def timezone_autocomplete(self, ctx: AutocompleteContext) -> None:
        """Return autocomplete information for timezones."""
        string_option_input = ctx.input_text
        timezones = get_timezone_strings()
        # add choice if the continent or country contains user input
        choices = [tz for tz in timezones if string_option_input.lower() in tz.lower()]
        await ctx.send(
            choices=choices,
        )


def get_timezone_strings() -> list[str]:
    """Return all available timezones."""
    return sorted(zoneinfo.available_timezones())


def seconds_until_time(target_datetime: datetime.datetime) -> float:
    """Calculate seconds until a specific time is reached, considering timezones.

    :param target_datetime: Datetime to calculate seconds until.
    :return: Float representing the number of seconds until the target time is reached.
    """
    timezone_obj = target_datetime.tzinfo
    local_dt_now = datetime.datetime.now(timezone_obj)
    seconds_until = (target_datetime - local_dt_now).total_seconds()

    # Handle negative values for times in the past (return 0)
    return float(max(0.0, seconds_until))


class UserTimezones:
    """Class representing database operation for storing timezone information."""

    def __init__(self, db_timezones: list) -> None:
        self.timezones = dict(db_timezones)

    def add_user(self, user_id: int, timezone: str) -> None:
        """Add user to dict.

        :param user_id: Discord user ID.
        :param timezone: Timzone in IANA format.
        """
        self.timezones[user_id] = timezone

    def has_user(self, user_id: int) -> bool:
        """Check if user is in dict.

        :param user_id: Discord user ID.
        :return: True if user has a saved timezone, else False.
        """
        return user_id in self.timezones

    def get_timezone(self, user_id: int) -> str:
        """Return timezone information for user_id key.

        :param user_id: Discord user ID.
        :return: Users timezone in IANA format.
        """
        return self.timezones[user_id]
