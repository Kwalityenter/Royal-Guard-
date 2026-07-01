import discord
import asyncio
import embed_config as cfg
from config import TICKET_CATEGORY_ID, STAFF_ROLE_ID
from verification_check import is_verified, not_verified_embed


class TicketTypeSelect(discord.ui.Select):
    def __init__(self, options_list, custom_id_suffix):
        options = [discord.SelectOption(label=opt) for opt in options_list]
        super().__init__(
            placeholder="Select Ticket Type",
            options=options,
            custom_id=f"ticket_select_{custom_id_suffix}"
        )

    async def callback(self, interaction: discord.Interaction):
        if not is_verified(str(interaction.user.id)):
            embed = not_verified_embed(interaction.client.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        category_name = self.values[0]
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        staff_role = guild.get_role(STAFF_ROLE_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        safe_name = interaction.user.name.lower().replace(" ", "-")[:20]
        channel = await guild.create_text_channel(
            name=f"ticket-{safe_name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            description=cfg.TICKET_CHANNEL_GREETING.format(user_mention=interaction.user.mention, category=category_name),
            color=discord.Color.red()
        )
        embed.set_author(name="Royal Guard", icon_url=interaction.client.user.display_avatar.url)
        await channel.send(embed=embed, view=CloseTicketView())

        await interaction.followup.send(f"Ticket created: {channel.mention}", ephemeral=True)


class TicketSelectView(discord.ui.View):
    def __init__(self, options_list, custom_id_suffix):
        super().__init__(timeout=None)
        self.add_item(TicketTypeSelect(options_list, custom_id_suffix))


class ReportTicketPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", emoji="🚨", style=discord.ButtonStyle.danger, custom_id="report_create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_verified(str(interaction.user.id)):
            embed = not_verified_embed(interaction.client.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await interaction.response.send_message(
            "Select Ticket Type",
            view=TicketSelectView(cfg.REPORT_TICKET_OPTIONS, "report"),
            ephemeral=True
        )


class OtherTicketPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", emoji="🚨", style=discord.ButtonStyle.danger, custom_id="other_create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_verified(str(interaction.user.id)):
            embed = not_verified_embed(interaction.client.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await interaction.response.send_message(
            "Select Ticket Type",
            view=TicketSelectView(cfg.OTHER_TICKET_OPTIONS, "other"),
            ephemeral=True
        )


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.secondary, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing ticket in 5 seconds...", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete()