from interactions import (
    ContextMenuContext,
    Extension,
    Message,
    OptionType,
    SlashContext,
    message_context_menu,
    slash_command,
    slash_option,
)


class TodoList(Extension):
    """Todo list extension."""

    @slash_command(name="todo", description="Todo list", sub_cmd_name="list", sub_cmd_description="Lists all todos")
    async def todo_list(self, ctx: SlashContext) -> None:
        """List all saved todos as a numbered list."""
        todos = await ctx.bot.db.todo_listall(user_id=ctx.author.id)
        if len(todos) == 0:
            await ctx.send("There are no saved todos.", ephemeral=True)
        else:
            await ctx.send("\n".join([f"{i}. {item[0]}" for i, item in enumerate(todos, start=1)]), ephemeral=True)

    @slash_command(name="todo", description="Todo list", sub_cmd_name="add", sub_cmd_description="Adds a todo")
    @slash_option(name="todo_msg", description="The ToDo you want to add", required=True, opt_type=OptionType.STRING)
    async def todo_add(self, ctx: SlashContext, todo_msg: str) -> None:
        """Add a new todo."""
        await ctx.bot.db.todo_add(user_id=ctx.user.id, item=todo_msg)
        await ctx.send(f"``{todo_msg}`` added to todo list.", ephemeral=True)

    @slash_command(name="todo", description="Todo list", sub_cmd_name="remove", sub_cmd_description="Removes a todo")
    @slash_option(
        name="todo_id",
        description="The number of the ToDo you want to remove",
        required=True,
        opt_type=OptionType.INTEGER,
    )
    async def todo_remove(self, ctx: SlashContext, todo_id: int) -> None:
        """Remove a todo."""
        _, _, _, todo_item = await ctx.bot.db.todo_get_item(user_id=ctx.author.id, item_id=todo_id)
        await ctx.bot.db.todo_remove(user_id=ctx.author.id, item_id=todo_id)
        await ctx.send(f"You removed ``{todo_item}`` from your todo list.", ephemeral=True)

    @message_context_menu(name="add to todo")
    async def todo_msg_context_add(self, ctx: ContextMenuContext) -> None:
        """Add todo via message context menu."""
        message: Message = ctx.target
        todo_msg = message.content
        if "\n" in todo_msg:
            await ctx.send("Only single line messages can be added as todo.", ephemeral=True)
        else:
            await ctx.bot.db.todo_add(user_id=ctx.author.id, item=todo_msg)
            await ctx.send(f"``{todo_msg}`` added to todo list.", ephemeral=True)
