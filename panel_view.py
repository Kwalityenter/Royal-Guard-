import secrets
import time
import discord

from database import save_pending_state
from oauth_server import build_authorize_url
from verification_check import is_verified, not_verified_embed
import embed_config as cfg

# In-memory cooldown tracker: {discord_user_id: last_verify_timestamp}
_verify_cooldowns: dict[int, float] = {}
VERIFY_COOLDOWN_SECONDS = 120  # 2 minutes


def get_cooldown_remaining(user_id: int) -> int:
    """Returns seconds remaining on cooldown, or 0 if not on cooldown."""
    last = _verify_cooldowns.get(user_id, 0)
    remaining = VERIFY_COOLDOWN_SECONDS - (time.time() - last)
    return max(0, int(remaining))


class BeginVerificationView(discord.ui.View):
    """The 'Begin Verification' link button sent ephemerally to the user."""
    def __init__(self, url: str):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(
            label="Begin Verification",
            url=url,
            style=discord.ButtonStyle.link,
            emoji="↗️"
        ))


class VerificationPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify via ROBLOX Login", style=discord.ButtonStyle.success, custom_id="verify_login_btn")
    async def verify_login(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id

        # Cooldown check
        remaining = get_cooldown_remaining(user_id)
        if remaining > 0:
            mins = remaining // 60
            secs = remaining % 60
            time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"

            embed = discord.Embed(
                title="Warning - Cooldown",
                description=f"You're currently on a **{time_str}** cooldown for the `RobloxVerify` button!",
                color=discord.Color.orange()
            )
            embed.set_author(
                name=interaction.guild.name if interaction.guild else "Royal Guard",
                icon_url=interaction.client.user.display_avatar.url
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Set cooldown
        _verify_cooldowns[user_id] = time.time()

        # Generate OAuth URL
        state = secrets.token_urlsafe(16)
        save_pending_state(state, str(user_id))
        url = build_authorize_url(state)

        bot_avatar = interaction.client.user.display_avatar.url

        embed = discord.Embed(
            title=cfg.VERIFY_TITLE,
            color=cfg.VERIFY_COLOR
        )
        embed.set_author(name=cfg.VERIFY_AUTHOR_NAME, icon_url=bot_avatar)
        embed.add_field(
            name="",
            value="Click on the button below to begin verification process",
            inline=False
        )
        embed.add_field(
            name="",
            value="**Please DO NOT share this link with anyone**",
            inline=False
        )
        embed.add_field(
            name="",
            value="This link expires in **2 minutes** or once the verification process begins.",
            inline=False
        )
        if cfg.VERIFY_FOOTER_TEXT:
            embed.set_footer(text=cfg.VERIFY_FOOTER_TEXT)

        await interaction.response.send_message(
            embed=embed,
            view=BeginVerificationView(url),
            ephemeral=True
        )

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