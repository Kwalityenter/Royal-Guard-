import threading

import discord
from discord import app_commands
from discord.ext import commands

from config import TOKEN, GUILD_ID, ADMIN_ROLE_ID
from database import init_db, get_link
from roblox import get_group_role, get_roblox_username
from rankbind_store import set_bind, remove_bind, get_all_binds
from oauth_server import run_oauth_server
from panel_view import VerificationPanel
from ticket_view import ReportTicketPanel, OtherTicketPanel
import embed_config as cfg

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
GUILD_OBJ = discord.Object(id=GUILD_ID)


def is_admin(member: discord.Member) -> bool:
    return member.guild_permissions.administrator or any(r.id == ADMIN_ROLE_ID for r in member.roles)


@bot.event
async def on_ready():
    bot.add_view(VerificationPanel())
    bot.add_view(ReportTicketPanel())
    bot.add_view(OtherTicketPanel())
    synced = await bot.tree.sync(guild=GUILD_OBJ)
    print(f"Logged in as {bot.user} | Synced {len(synced)} commands")


async def perform_update(member: discord.Member) -> str:
    link = get_link(str(member.id))
    if not link:
        return cfg.UPDATE_NOT_VERIFIED_TEXT.format(member=member.mention)

    roblox_id = link["roblox_id"]
    role_data = await get_group_role(roblox_id)
    binds = get_all_binds()

    if not role_data:
        try:
            await member.kick(reason="No longer in Roblox group")
        except discord.Forbidden:
            return f"Could not kick {member} — missing permissions or role hierarchy issue."
        return f"{cfg.UPDATE_KICK_PREFIX}{member} was removed (no longer in the Roblox group)."

    username = await get_roblox_username(roblox_id)
    if username:
        try:
            await member.edit(nick=username[:32])
        except discord.Forbidden:
            pass

    correct_role_id = binds.get(str(role_data["rank_id"]))
    bound_role_ids = set(binds.values())

    for role_id in bound_role_ids:
        role = member.guild.get_role(int(role_id))
        if not role:
            continue
        has_role = role in member.roles
        if str(role_id) == str(correct_role_id) and not has_role:
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                pass
        elif str(role_id) != str(correct_role_id) and has_role:
            try:
                await member.remove_roles(role)
            except discord.Forbidden:
                pass

    return f"{cfg.UPDATE_SUCCESS_PREFIX}{member} updated → **{role_data['rank_name']}** (rank {role_data['rank_id']})"


@bot.tree.command(name="update", description="Resync your roles, nickname, and group status", guild=GUILD_OBJ)
@app_commands.describe(user="User to update (staff only)")
async def update(interaction: discord.Interaction, user: discord.Member = None):
    target = user or interaction.user

    if not get_link(str(target.id)):
        embed = discord.Embed(
            title=cfg.NOT_VERIFIED_TITLE,
            description=cfg.NOT_VERIFIED_UPDATE_DESCRIPTION,
            color=cfg.NOT_VERIFIED_COLOR
        )
        embed.set_author(name="Royal Guard", icon_url=interaction.client.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    await interaction.response.defer()

    if user and user != interaction.user and not is_admin(interaction.user):
        await interaction.followup.send("You don't have permission to update other users.")
        return

    result = await perform_update(target)
    await interaction.followup.send(result)


@bot.tree.command(name="panel", description="Post the verification panel", guild=GUILD_OBJ)
async def panel(interaction: discord.Interaction):
    if not is_admin(interaction.user):
        await interaction.response.send_message("You don't have permission to do this.", ephemeral=True)
        return

    embed = discord.Embed(
        title=cfg.PANEL_TITLE,
        description=cfg.PANEL_DESCRIPTION,
        color=cfg.PANEL_COLOR
    )
    embed.set_author(name=cfg.PANEL_AUTHOR_NAME)
    if cfg.PANEL_FOOTER_TEXT:
        embed.set_footer(text=cfg.PANEL_FOOTER_TEXT)
    await interaction.response.send_message(embed=embed, view=VerificationPanel())


@bot.tree.command(name="ticketpanel", description="Post the ticket creation panels", guild=GUILD_OBJ)
async def ticketpanel(interaction: discord.Interaction):
    if not is_admin(interaction.user):
        await interaction.response.send_message("You don't have permission to do this.", ephemeral=True)
        return

    report_embed = discord.Embed(
        title=cfg.REPORT_TICKET_TITLE,
        description=cfg.REPORT_TICKET_DESCRIPTION,
        color=cfg.REPORT_TICKET_COLOR
    )
    other_embed = discord.Embed(
        title=cfg.OTHER_TICKET_TITLE,
        description=cfg.OTHER_TICKET_DESCRIPTION,
        color=cfg.OTHER_TICKET_COLOR
    )

    await interaction.response.send_message(embed=report_embed, view=ReportTicketPanel())
    await interaction.followup.send(embed=other_embed, view=OtherTicketPanel())


rankbind_group = app_commands.Group(name="rankbind", description="Manage rank-to-role binds", guild_ids=[GUILD_ID])


@rankbind_group.command(name="add", description="Bind a Roblox rank to a Discord role")
@app_commands.describe(rank="Roblox rank number (1-255)", role="Discord role")
async def rankbind_add(interaction: discord.Interaction, rank: int, role: discord.Role):
    if not is_admin(interaction.user):
        await interaction.response.send_message("You don't have permission to do this.", ephemeral=True)
        return
    set_bind(rank, role.id)
    await interaction.response.send_message(f"Bound rank `{rank}` → {role.mention}")


@rankbind_group.command(name="remove", description="Remove a rank bind")
@app_commands.describe(rank="Roblox rank number")
async def rankbind_remove(interaction: discord.Interaction, rank: int):
    if not is_admin(interaction.user):
        await interaction.response.send_message("You don't have permission to do this.", ephemeral=True)
        return
    remove_bind(rank)
    await interaction.response.send_message(f"Removed bind for rank `{rank}`")


@rankbind_group.command(name="list", description="List all rank binds")
async def rankbind_list(interaction: discord.Interaction):
    binds = get_all_binds()
    if not binds:
        await interaction.response.send_message("No rank binds set.")
        return
    lines = []
    for rank_id, role_id in binds.items():
        role = interaction.guild.get_role(int(role_id))
        lines.append(f"Rank `{rank_id}` → {role.mention if role else f'`{role_id}` (deleted role)'}")
    embed = discord.Embed(title=cfg.RANKBIND_LIST_TITLE, description="\n".join(lines), color=cfg.RANKBIND_LIST_COLOR)
    await interaction.response.send_message(embed=embed)


bot.tree.add_command(rankbind_group)


def main():
    init_db()
    threading.Thread(target=run_oauth_server, daemon=True).start()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()