"""Demo Discord bot: welcome messages, polls, reminders, and self-assign roles."""
import asyncio
import os
import re

import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
WELCOME_CHANNEL = os.getenv("WELCOME_CHANNEL", "welcome")
SELF_ROLES = [r.strip() for r in os.getenv("SELF_ROLES", "Gamer,Artist,Music").split(",") if r.strip()]

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user} — slash commands synced")


@client.event
async def on_member_join(member: discord.Member):
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL)
    if channel:
        embed = discord.Embed(
            title=f"Welcome, {member.display_name}!",
            description="Grab your roles with `/roles` and say hi 👋",
            color=0x5865F2,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)


@tree.command(description="Create a quick poll (separate options with commas)")
async def poll(interaction: discord.Interaction, question: str, options: str):
    choices = [o.strip() for o in options.split(",") if o.strip()][:10]
    if len(choices) < 2:
        await interaction.response.send_message("Give at least 2 options.", ephemeral=True)
        return
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    body = "\n".join(f"{emojis[i]} {c}" for i, c in enumerate(choices))
    await interaction.response.send_message(embed=discord.Embed(title=f"📊 {question}", description=body))
    msg = await interaction.original_response()
    for i in range(len(choices)):
        await msg.add_reaction(emojis[i])


@tree.command(description="Remind you later, e.g. /remind 10m stretch")
async def remind(interaction: discord.Interaction, when: str, message: str):
    match = re.fullmatch(r"(\d+)([smhd])", when.strip().lower())
    if not match:
        await interaction.response.send_message("Use a format like `30s`, `10m`, `2h`, `1d`.", ephemeral=True)
        return
    seconds = int(match[1]) * {"s": 1, "m": 60, "h": 3600, "d": 86400}[match[2]]
    await interaction.response.send_message(f"⏰ Got it — I'll remind you in {when}.", ephemeral=True)
    await asyncio.sleep(seconds)
    await interaction.followup.send(f"{interaction.user.mention} reminder: {message}")


class RoleButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for name in SELF_ROLES:
            button = discord.ui.Button(label=name, style=discord.ButtonStyle.secondary)
            button.callback = self.make_callback(name)
            self.add_item(button)

    @staticmethod
    def make_callback(role_name: str):
        async def callback(interaction: discord.Interaction):
            role = discord.utils.get(interaction.guild.roles, name=role_name)
            if role is None:
                await interaction.response.send_message(f"Role `{role_name}` doesn't exist yet.", ephemeral=True)
            elif role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(f"Removed **{role_name}**.", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"Added **{role_name}**!", ephemeral=True)
        return callback


@tree.command(description="Pick your roles")
async def roles(interaction: discord.Interaction):
    await interaction.response.send_message("Click to toggle a role:", view=RoleButtons())


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Set DISCORD_TOKEN in a .env file first (see README).")
    client.run(TOKEN)
