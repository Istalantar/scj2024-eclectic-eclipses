from interactions import (
    ActionRow,
    Button,
    ButtonStyle,
    ContextMenuContext,
    Extension,
    Message,
    Modal,
    ModalContext,
    OptionType,
    ShortText,
    SlashContext,
    listen,
    message_context_menu,
    slash_command,
    slash_option,
)
from interactions.api.events import Component


class TodoList(Extension):
    """Todo list extension."""

    async def _get_todo_list(self, user_id: int) -> list[str]:
        """Get all todos for a user and return them as a numbere list."""
        todos = await self.bot.db.todo_listall(user_id=user_id)
        ret = [f"{i}. {item[0]}" for i, item in enumerate(todos, start=1)]
        if len(ret) < 1:
            return ["There are no saved todos."]
        return ret

    async def _add_todo(self, user_id: int, todo: str) -> None:
        await self.bot.db.todo_add(user_id=user_id, item=todo)

    async def _remove_todo(self, user_id: int, todo: str) -> str:
        start = todo.find(".") + 1
        todo = todo[start:].strip()
        _, _, _, todo_item = await self.bot.db.todo_get_item(user_id=user_id, item=todo)
        await self.bot.db.todo_remove(user_id=user_id, item=todo)
        return todo_item

    @staticmethod
    def _gui_move_top(todo_list: list[str]) -> list[str]:
        """Move the highlight to the top of the todo list."""
        for i, todo in enumerate(todo_list):
            if "`" in todo:
                todo_list[i] = todo.replace("`", "")
                todo_list[0] = f"`{todo_list[0]}`"
                break
        return todo_list

    @staticmethod
    def _gui_move_up(todo_list: list[str]) -> list[str]:
        """Move the highlight to the previous todo."""
        for i, todo in enumerate(todo_list):
            if "`" in todo:
                todo_list[i] = todo.replace("`", "")
                if i <= 0:
                    todo_list[-1] = f"`{todo_list[-1]}`"
                else:
                    todo_list[i - 1] = f"`{todo_list[i - 1]}`"
                break
        return todo_list

    @staticmethod
    def _gui_move_down(todo_list: list[str]) -> list[str]:
        """Move the highlight to the next todo."""
        for i, todo in enumerate(todo_list):
            if "`" in todo:
                todo_list[i] = todo.replace("`", "")
                if i >= len(todo_list) - 1:
                    todo_list[0] = f"`{todo_list[0]}`"
                else:
                    todo_list[i + 1] = f"`{todo_list[i + 1]}`"
                break
        return todo_list

    @staticmethod
    def _gui_move_bottom(todo_list: list[str]) -> list[str]:
        """Move the highlight to the bottom of the todo list."""
        for i, todo in enumerate(todo_list):
            if "`" in todo:
                todo_list[i] = todo.replace("`", "")
                todo_list[-1] = f"`{todo_list[-1]}`"
                break
        return todo_list

    async def _gui_add(self, user_id: int, todo: str) -> list[str]:
        """Add a new todo and highlight the added todo."""
        await self.bot.db.todo_add(user_id=user_id, item=todo)
        todo_list = await self._get_todo_list(user_id=user_id)
        todo_list[-1] = f"`{todo_list[-1]}`"
        return todo_list

    async def _gui_remove(self, user_id: int, todo_list: list[str]) -> list[str]:
        """Remove the highlighted todo and highlight the next todo."""
        todo_number = -1
        todo = ""
        for i, temp_todo in enumerate(todo_list):
            if "`" in temp_todo:
                todo_number = i
                todo = temp_todo.replace("`", "")
                start = todo.find(".") + 1
                todo = todo[start:].strip()
                break

        await self.bot.db.todo_remove(user_id=user_id, item=todo)
        todo_list = await self._get_todo_list(user_id=user_id)
        # highlight the next todo in the list, which took the position of the removed todo,
        # if the last todo was removed, highlight the last todo in the list
        if todo_number < len(todo_list):
            todo_list[todo_number] = f"`{todo_list[todo_number]}`"
        else:
            todo_list[-1] = f"`{todo_list[-1]}`"
        return todo_list

    @slash_command(name="todo", description="Todo list", sub_cmd_name="list", sub_cmd_description="Lists all todos")
    async def todo_list(self, ctx: SlashContext) -> None:
        """List all saved todos."""
        todo_list = await self._get_todo_list(ctx.author.id)
        await ctx.send("\n".join(todo_list), ephemeral=True)

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
        todo_list = await self._get_todo_list(user_id=ctx.author.id)
        todo = todo_list[todo_id - 1]
        ret = await self._remove_todo(ctx.author.id, todo)
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

    @slash_command(
        name="todo",
        description="Todo list",
        sub_cmd_name="gui",
        sub_cmd_description="Interact via buttons with the todo list",
    )
    async def todo_gui(self, ctx: SlashContext) -> None:
        """Interact via buttons with the todo list."""
        components: list[ActionRow] = [
            ActionRow(
                Button(
                    style=ButtonStyle.GREY,
                    label="|<",
                    custom_id="top",
                ),
                Button(
                    style=ButtonStyle.GREY,
                    label="<",
                    custom_id="up",
                ),
                Button(
                    style=ButtonStyle.GREY,
                    label=">",
                    custom_id="down",
                ),
                Button(
                    style=ButtonStyle.GREY,
                    label=">|",
                    custom_id="bottom",
                ),
            ),
            ActionRow(
                Button(
                    style=ButtonStyle.RED,
                    label="Remove",
                    custom_id="remove",
                ),
                Button(
                    style=ButtonStyle.GREEN,
                    label="Add",
                    custom_id="add",
                ),
            ),
        ]
        todo_list = await self._get_todo_list(ctx.author.id)
        todo_list[0] = f"`{todo_list[0]}`"  # highlight the first todo
        await ctx.send("\n".join(todo_list), components=components, ephemeral=True)

    @listen(Component)
    async def on_component(self, event: Component) -> None:
        """Handle button interaction."""
        ctx = event.ctx
        todo_list = []
        is_modal = False
        match ctx.custom_id:
            case "top":
                todo_list = self._gui_move_top(ctx.message.content.split("\n"))
            case "up":
                todo_list = self._gui_move_up(ctx.message.content.split("\n"))
            case "down":
                todo_list = self._gui_move_down(ctx.message.content.split("\n"))
            case "bottom":
                todo_list = self._gui_move_bottom(ctx.message.content.split("\n"))
            case "add":
                is_modal = True
                message = ctx.message
                todo_input = Modal(ShortText(label="New Todo", custom_id="modal_todo"), title="Adding Todo")
                await ctx.send_modal(modal=todo_input)
                modal_ctx: ModalContext = await ctx.bot.wait_for_modal(modal=todo_input)
                todo = modal_ctx.responses["modal_todo"]
                todo_list = await self._gui_add(ctx.author.id, todo)
                await modal_ctx.edit(message=message, content="\n".join(todo_list))
            case "remove":
                todo_list = await self._gui_remove(ctx.author.id, ctx.message.content.split("\n"))

        if not is_modal:
            # ctx is already acknowledged through modal usage for 'add'
            await ctx.edit_origin(content="\n".join(todo_list))
