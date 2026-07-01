import discord
from database import get_link


def is_verified(discord_id: str) -> bool:
    return get_link(discord_id) is not None


def not_verified_embed(bot_user: discord.ClientUser, description: str = None) -> discord.Embed:
    title = "Warning - Not Verified"
    desc = description or "You must be verified to create report or other tickets."
    color = discord.Color.orange()

    embed = discord.Embed(title=title, description=desc, color=color)
    embed.set_author(name="Royal Guard", icon_url=bot_user.display_avatar.url)
    return embed