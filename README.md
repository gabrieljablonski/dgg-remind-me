# DGG Remind Me Bot

A bot that reminds you of stuff in the [destiny.gg](https://destiny.gg) chat.
Built using the [`dgg-chat-bot`](https://github.com/gabrieljablonski/dgg-chat-bot) package.

To use it, whisper `BotReminder` in chat with a command. Example: `/whisper BotReminder !help`. You can have up to 5 timed reminders registered at a time.

## Commands

| Command                   | Aliases           | What It Does                                                                                                                              |
|:-------------------------:|:-----------------:|:-----------------------------------------------------------------------------------------------------------------------------------------:|
| `!help <cmd>`             | `!h`, `!commands` | Gives more info about the command `<cmd>`. If `<cmd>` not specified, lists all commands.                                                  |
| `!timezone <tz>`          | `!tz`             | Sets your time zone in which to show the times. `<tz>` is the offset from UTC. Examples: EST -> UTC-04, PST -> UTC-07, Germany -> UTC+02. |
| `!nexttime <note>`        | `!nt`             | Reminds you of `<note>` next time you join the chat. `<note>` is optional.                                                                |
| `!remindme <expr> <note>` | `!rm`             | Reminds you of `<note>` at the time evaluated from `<expr>`. For details on `<expr>`, use `!help remindme`. `<note>` is optional.         |
| `!reminders`              | `!r`              | Lists the reminders you have registered.                                                                                                  |
| `!delete <n>`             | `!d`              | Deletes the reminder `<n>`, as numbered in `!reminders`.                                                                                  |
