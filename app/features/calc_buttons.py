import re

from interactions import Button, Extension, SlashContext, component_callback, slash_command
from interactions.models.discord.components import ActionRow, BaseComponent
from interactions.models.internal.context import ComponentContext

buttons = [
    ActionRow(
        Button(style=1, label="0", custom_id="result"),
        Button(label="<", style=3, custom_id="<", disabled=True),
        Button(label=">", style=3, custom_id=">"),
    ),
]
buttons += [
    ActionRow(
        *(Button(label=f"{i}", custom_id=f"{i}", style=2) for i in range(7, 10)),
        Button(label="+", style=1, custom_id="calc_+"),
        Button(label="-", style=1, custom_id="calc_-"),
    ),
]
buttons += [
    ActionRow(
        *(Button(label=f"{i}", custom_id=f"{i}", style=2) for i in range(4, 7)),
        Button(label="*", style=1, custom_id="calc_*"),
        Button(label="/", style=1, custom_id="calc_/"),
    ),
]
buttons += [ActionRow(*(Button(label=f"{i}", custom_id=f"{i}", style=2) for i in range(1, 4)))]
buttons += [
    ActionRow(
        Button(label=".", style=2, custom_id="calc_."),
        Button(label="0", custom_id="0", style=2),
        Button(label="=", style=3, custom_id="calc_="),
    ),
]

mathfunctions = [
    ("cos(", "tan(", "sin(", ")"),
    ("acos(", "atan(", "asin(", "rad("),
    ("abs(", "sqrt(", "log(", "deg("),
    ("^", "e", "π", "!"),
]


class ButtonCalc(Extension):
    """Discord Calculator Widget Extension via Button Interactions."""

    @slash_command(
        name="calc",
        description="Calculator functions",
        sub_cmd_name="gui",
        sub_cmd_description="Calculate a number via buttons",
    )
    async def calc_gui(self, ctx: SlashContext) -> None:
        """Display Calculator."""
        await ctx.send(components=buttons, ephemeral=True)

    @component_callback(re.compile(r"^[0-9]$"))
    async def numbers_callback(self, ctx: ComponentContext) -> None:
        """Triggers on calc number buttons."""
        await ctx.defer(edit_origin=True, suppress_error=True)
        components = ctx.message.components
        a_r: ActionRow = components[0]
        label_button: BaseComponent = a_r.components[0]
        label_button.label = int(label_button.label) + int(ctx.custom_id)
        await ctx.edit_origin(components=components, content=f'`{ctx.message.content.strip("`") + ctx.custom_id}`')

    @component_callback(re.compile(r"^[<>]$"))
    async def pagination_callback(self, ctx: ComponentContext) -> None:
        """Triggers for calc pagination buttons."""
        await ctx.defer(edit_origin=True)
        if ctx.custom_id == ">":
            lb = ctx.message.components[0].components[0].to_dict()
            lb["custom_id"] = "result"
            comp = [
                ActionRow(
                    Button.from_dict(lb),
                    Button(label="<", style=3, custom_id="<"),
                    Button(label=">", style=3, custom_id=">", disabled=True),
                ),
            ]
            comp += [
                ActionRow(*(Button(label=f"{func}", custom_id=f"calc_{func}", style=2) for func in row))
                for row in mathfunctions
            ]
            await ctx.edit_origin(components=comp)
        else:
            current_label: BaseComponent = ctx.message.components[0].components[0]
            base_label: BaseComponent = buttons[0].components[0]
            base_label.label = current_label.to_dict()["label"]
            await ctx.edit_origin(components=buttons)

    @component_callback(re.compile("calc_.*"))
    async def callback_for_calc_buttons(self, ctx: ComponentContext) -> None:
        """Triggers for calc text buttons."""
        await ctx.defer(edit_origin=True)
        match ctx.custom_id:
            case "calc_=":
                # TODO: parse string
                await ctx.send(f"Result {ctx.message.content}", ephemeral=True)
                return
        await ctx.edit_origin(content=f'`{ctx.message.content.strip("`") + ctx.custom_id.split('_')[1]}`')

    @component_callback("result")
    async def result_callback(self, ctx: ComponentContext) -> None:
        """Triggers for calc result button."""
        result: Button | BaseComponent = ctx.message.components[0].components[0]
        await ctx.send(result.label, ephemeral=True)

    @slash_command(name="counter")
    async def counter(self, ctx: SlashContext) -> None:
        """Send basic counter widget."""
        components = ActionRow(
            Button(style=2, label="0"),
            Button(style=3, label="+", custom_id="+"),
            Button(style=4, label="-", custom_id="-"),
        )
        await ctx.send(components=components, ephemeral=True)

    @component_callback(re.compile(r"^[+-]$"))
    async def counter_callback(self, ctx: ComponentContext) -> None:
        """Triggers for counter buttons."""
        components = ctx.message.components
        _label = components[0].components[0]
        if ctx.custom_id == "+":
            _label.label = int(_label.label) + 1
        else:
            _label.label = int(_label.label) - 1
        await ctx.edit_origin(components=components)
