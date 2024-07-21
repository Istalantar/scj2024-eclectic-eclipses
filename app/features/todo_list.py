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

    async def _get_todo_list(self, user_id: int) -> str:
        """Get all todos for a user and return them as a numbere list."""
        todos = await self.bot.db.todo_listall(user_id=user_id)
        ret = "\n".join([f"{i}. {item[0]}" for i, item in enumerate(todos, start=1)])
        if len(ret) < 1:
            return "There are no saved todos."

        return ret

    async def _add_todo(self, user_id: int, todo: str) -> None:
        await self.bot.db.todo_add(user_id=user_id, item=todo)

    async def _remove_todo(self, user_id: int, todo_number: int) -> str:
        _, _, _, todo_item = await self.bot.db.todo_get_item(user_id=user_id, item_id=todo_number)
        await self.bot.db.todo_remove(user_id=user_id, item_id=todo_number)
        return todo_item

    @slash_command(name="todo", description="Todo list", sub_cmd_name="list", sub_cmd_description="Lists all todos")
    async def todo_list(self, ctx: SlashContext) -> None:
        """List all saved todos."""
        await ctx.send(await self._get_todo_list(ctx.author.id), ephemeral=True)

    @slash_command(name="todo", description="Todo list", sub_cmd_name="add", sub_cmd_description="Adds a todo")
    @slash_option(name="todo_msg", description="The ToDo you want to add", required=True, opt_type=OptionType.STRING)
    async def todo_add(self, ctx: SlashContext, todo_msg: str) -> None:
        """Add a new todo."""
        await self._add_todo(ctx.author.id, todo_msg)
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
        ret = await self._remove_todo(ctx.author.id, todo_id)
        await ctx.send(f"You removed ``{ret}`` from your todo list.", ephemeral=True)

    @message_context_menu(name="add to todo")
    async def todo_msg_context_add(self, ctx: ContextMenuContext) -> None:
        """Add todo via message context menu."""
        message: Message = ctx.target
        todo_msg = message.content
        if "\n" in todo_msg:
            await ctx.send("Only single line messages can be added as todo.", ephemeral=True)
        else:
            await self._add_todo(ctx.author.id, todo_msg)
            await ctx.send(f"``{todo_msg}`` added to todo list.", ephemeral=True)
