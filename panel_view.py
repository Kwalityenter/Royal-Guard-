import secrets
import discord

from database import save_pending_state
from oauth_server import build_authorize_url


class VerificationPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # persistent view, survives restarts if re-registered

    @discord.ui.button(label="Verify via ROBLOX Login", style=discord.ButtonStyle.success, custom_id="verify_login_btn")
    async def verify_login(self, interaction: discord.Interaction, button: discord.ui.Button):
        state = secrets.token_urlsafe(16)
        save_pending_state(state, str(interaction.user.id))
        url = build_authorize_url(state)

        embed = discord.Embed(
            title="Verify your Roblox account",
            description=f"[Click here to verify]({url})\n\nThis link is one-time use and tied to your Discord account.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Update Roles", style=discord.ButtonStyle.success, custom_id="update_roles_btn")
    async def update_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        # import locally to avoid circular import
        from bot import perform_update
        result = await perform_update(interaction.user)
        await interaction.followup.send(result, ephemeral=True)