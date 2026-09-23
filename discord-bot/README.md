# Demo Discord Bot

A small, clean Discord bot showing common features clients ask for.

**Features**
- Welcome message (embed + avatar) when someone joins
- `/poll` for reaction polls with up to 10 options
- `/remind` for reminders like `10m`, `2h`, `1d`
- `/roles` for buttons that let members give themselves roles

## Setup (about 5 minutes)

1. Create an app at https://discord.com/developers/applications, then open **Bot** → **Reset Token** and copy the token.
2. On the same page, turn on **Server Members Intent**.
3. Invite the bot: go to **OAuth2 → URL Generator**, tick scopes `bot` + `applications.commands` and permissions `Manage Roles`, `Send Messages`, `Add Reactions`, `Embed Links`, then open the URL.
4. Install and run:
   ```
   pip install -r requirements.txt
   copy .env.example .env      (then paste your token into .env)
   python bot.py
   ```
5. In your server, make roles named `Gamer`, `Artist` and `Music` (or change `SELF_ROLES` in `.env`). Drag the bot's role **above** them.
