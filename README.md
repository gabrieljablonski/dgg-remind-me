# DGG Remind Me Bot

A bot that reminds you of stuff in the [destiny.gg](https://destiny.gg) chat.
Built using the [`dgg-chat-bot`](https://github.com/gabrieljablonski/dgg-chat-bot) package.


## Commands

| Command                       | Aliases          | What It Does                                                                                                                              |
|:-----------------------------:|:----------------:|:-----------------------------------------------------------------------------------------------------------------------------------------:|
| `!help [<cmd>]`               | `!h` `!commands` | Gives more info about the command `<cmd>`. If `<cmd>` not specified, lists all commands.                                                  |
| `!reminders`                  | `!r` `!list`     | Lists the reminders you have registered.                                                                                                  |
| `!delete <n>`                 | `!d` `!remove`   | Deletes the reminder `<n>`, as numbered in `!reminders`.                                                                                  |
| `!nexttime [<note>]`          | `!nt`            | Reminds you of `<note>` next time you join the chat. `<note>` is optional.                                                                |
| `!timezone [<tz>]`            | `!tz`            | Sets your time zone in which to show the times. `<tz>` is the offset from UTC. Examples: EST -> UTC-04, PST -> UTC-07, Germany -> UTC+02. |
| `!remindme <expr> [<note>]`   | `!rm` `!add`     | Reminds you of `<note>` at the time evaluated from `<expr>`. For details on `<expr>`, use `!help remindme`. `<note>` is optional.         |
| `!remindmeon <expr> [<note>]` | `!rmo` `!addon`  | Similar to `!remindme`, but with a different expression format. Use `!help remindmeon` for details.                                       |
