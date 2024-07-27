import asyncio
import datetime
import zoneinfo

import interactions


class Alarm(interactions.Extension):
    """Alarm / Reminder extension."""

    def __init__(self, bot: interactions.Client) -> None:
        self.bot = bot
        print(f"{self.bot.user} loaded alarm extension")
        self.tz = UserTimezones()

    base = interactions.SlashCommand(name="remindme", description="Alarm base group")
    set = interactions.SlashCommand(name="set", description="Set base group")

    @base.subcommand(
        sub_cmd_name="at",
        sub_cmd_description="add an alarm at a specific date and time",
        options=[
            interactions.SlashCommandOption(
                name="date_time",
                description="date and time in the format 'YYYY-MM-DD HH:MM'",
                required=True,
                type=interactions.OptionType.STRING,
            ),
            interactions.SlashCommandOption(
                name="message",
                description="message to be sent when the alarm is triggered",
                required=False,
                type=interactions.OptionType.STRING,
            ),
        ],
    )
    async def add_at(
        self,
        ctx: interactions.SlashContext,
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
            await ctx.send(f"I'll remind you on {reminder_time.strftime('%A, %B %d, %Y at %H:%M')}")
            await asyncio.sleep(delay)
            await ctx.send(f"REMINDER: {message}")
        except ValueError:
            await ctx.send("Invalid date and time format. Please use 'YYYY-MM-DD HH:MM' format.")

    @base.subcommand(
        sub_cmd_name="in",
        sub_cmd_description="add a reminder for a certain amount of time from now",
        options=[
            interactions.SlashCommandOption(
                name="duration",
                description="integer representing the number of units",
                required=True,
                type=interactions.OptionType.INTEGER,
            ),
            interactions.SlashCommandOption(
                name="units",
                description="units representing a measurement of time",
                required=True,
                type=interactions.OptionType.STRING,
                choices=[
                    interactions.SlashCommandChoice(name="Seconds", value="sec"),
                    interactions.SlashCommandChoice(name="Minutes", value="min"),
                    interactions.SlashCommandChoice(name="Hours", value="hour"),
                ],
            ),
            interactions.SlashCommandOption(
                name="message",
                description="message to be sent when the alarm is triggered",
                required=False,
                type=interactions.OptionType.STRING,
            ),
        ],
    )
    async def add_in(
        self,
        ctx: interactions.SlashContext,
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
        await ctx.send(f"REMINDER: {message}")

    @set.subcommand(
        sub_cmd_name="timezone",
        sub_cmd_description="set your timezone",
    )
    @interactions.slash_option(
        name="timezone",
        description="Start typing your timezone. e.g America/Los_Angeles or Europe/London",
        required=True,
        opt_type=interactions.OptionType.STRING,
        autocomplete=True,
    )
    async def set_timezone(
        self,
        ctx: interactions.SlashContext,
        timezone: str,
    ) -> None:
        """Set timezone based on user selection."""
        # timezone selected by the user from the autocomplete list
        self.tz.add_user(ctx.author.id, timezone)
        await ctx.send(f"timezone set to {timezone}")

    @set_timezone.autocomplete("timezone")
    async def timezone_autocomplete(self, ctx: interactions.AutocompleteContext) -> None:
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

    Returns
    -------
        Float representing the number of seconds until the target time is reached.

    """
    timezone_obj = target_datetime.tzinfo
    local_dt_now = datetime.datetime.now(timezone_obj)
    seconds_until = (target_datetime - local_dt_now).total_seconds()

    # Handle negative values for times in the past (return 0)
    return float(max(0, seconds_until))


class UserTimezones:
    """Class representing database operation for storing timezone information."""

    def __init__(self) -> None:
        self.timezones = {}

    def add_user(self, user_id: int, timezone: str) -> None:
        """Add user to dict."""
        self.timezones[user_id] = timezone

    def has_user(self, user_id: int) -> bool:
        """Check if user is in dict."""
        return user_id in self.timezones

    def get_timezone(self, user_id: int) -> str:
        """Return timezone information for user_id key."""
        return self.timezones[user_id]
