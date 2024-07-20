from typing import ClassVar

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

    todos: ClassVar = []

    @slash_command(name="todo", description="Todo list", sub_cmd_name="list", sub_cmd_description="Lists all todos")
    async def todo_list(self, ctx: SlashContext) -> None:
        """List all saved todos as a numbered list."""
        # TODO: add database interaction
        if len(self.todos) == 0:
            await ctx.send("There are no saved todos.", ephemeral=True)
        else:
            await ctx.send("\n".join([f"{i}. {item}" for i, item in enumerate(self.todos, start=1)]), ephemeral=True)

    @slash_command(name="todo", description="Todo list", sub_cmd_name="add", sub_cmd_description="Adds a todo")
    @slash_option(name="todo_msg", description="The ToDo you want to add", required=True, opt_type=OptionType.STRING)
    async def todo_add(self, ctx: SlashContext, todo_msg: str) -> None:
        """Add a new todo."""
        # TODO: add database interaction
        self.todos.append(todo_msg)
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
        # TODO: add database interaction
        await ctx.send(f"You removed ``{self.todos.pop(todo_id - 1)}`` from your todo list.", ephemeral=True)

    @message_context_menu(name="add to todo")
    async def todo_msg_context_add(self, ctx: ContextMenuContext) -> None:
        """Add todo via message context menu."""
        # TODO: add database interaction
        message: Message = ctx.target
        todo_msg = message.content
        if "\n" in todo_msg:
            await ctx.send("Only single line messages can be added as todo.", ephemeral=True)
        else:
            self.todos.append(todo_msg)
            await ctx.send(f"``{todo_msg}`` added to todo list.", ephemeral=True)
