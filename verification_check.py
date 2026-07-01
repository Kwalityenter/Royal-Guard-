import secrets
import discord

from database import save_pending_state
from oauth_server import build_authorize_url
from verification_check import is_verified, not_verified_embed
import embed_config as cfg


class VerificationPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify via ROBLOX Login", style=discord.ButtonStyle.success, custom_id="verify_login_btn")
    async def verify_login(self, interaction: discord.Interaction, button: discord.ui.Button):
        state = secrets.token_urlsafe(16)
        save_pending_state(state, str(interaction.user.id))
        url = build_authorize_url(state)

        bot_avatar = interaction.client.user.display_avatar.url

        embed = discord.Embed(
            title=cfg.VERIFY_TITLE,
            description=cfg.VERIFY_DESCRIPTION_TEMPLATE.format(url=url),
            color=cfg.VERIFY_COLOR
        )
        embed.set_author(name=cfg.VERIFY_AUTHOR_NAME, icon_url=bot_avatar)
        if cfg.VERIFY_USE_THUMBNAIL:
            embed.set_thumbnail(url=bot_avatar)
        if cfg.VERIFY_FOOTER_TEXT:
            embed.set_footer(text=cfg.VERIFY_FOOTER_TEXT)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Update Roles", style=discord.ButtonStyle.success, custom_id="update_roles_btn")
    async def update_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_verified(str(interaction.user.id)):
            embed = not_verified_embed(interaction.client.user, cfg.NOT_VERIFIED_UPDATE_DESCRIPTION)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        from bot import perform_update
        result = await perform_update(interaction.user)
        await interaction.followup.send(result, ephemeral=True)