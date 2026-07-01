import discord

# ====================== PANEL EMBED ======================
PANEL_TITLE = "BRITISH ARMY VERIFICATION SYSTEM"
PANEL_DESCRIPTION = (
    "Use the **Verify via ROBLOX Login** button to verify / reverify your ROBLOX account. "
    "Use the **Update Roles** button to update your roles."
)
PANEL_COLOR = discord.Color.green()
PANEL_AUTHOR_NAME = "Royal Guard"
PANEL_FOOTER_TEXT = None

# ====================== VERIFY (LOGIN) EMBED ======================
VERIFY_TITLE = "Roblox Verification"
VERIFY_DESCRIPTION_TEMPLATE = (
    "Click the link below to verify your Roblox account.\n\n"
    "**[Click here to verify]({url})**\n\n"
    "This link is one-time use and tied to your Discord account. It will expire once used."
)
VERIFY_COLOR = discord.Color.blue()
VERIFY_AUTHOR_NAME = "Royal Guard"
VERIFY_FOOTER_TEXT = "British Army Verification System"
VERIFY_USE_THUMBNAIL = True

# ====================== UPDATE ROLES RESULT ======================
UPDATE_SUCCESS_PREFIX = ""
UPDATE_KICK_PREFIX = ""
UPDATE_NOT_VERIFIED_TEXT = "{member} is not verified. Run `/verify` first."

# ====================== RANKBIND LIST EMBED ======================
RANKBIND_LIST_TITLE = "Rank Binds"
RANKBIND_LIST_COLOR = discord.Color.blurple()

# ====================== TICKET PANELS ======================
REPORT_TICKET_TITLE = "REPORT TICKETS"
REPORT_TICKET_DESCRIPTION = "Press the 🚨 **Create Ticket** button for tickets to report an incident or other users."
REPORT_TICKET_COLOR = discord.Color.red()

OTHER_TICKET_TITLE = "OTHER TICKETS"
OTHER_TICKET_DESCRIPTION = "Press the 🚨 **Create Ticket** button for tickets regarding other matters."
OTHER_TICKET_COLOR = discord.Color.red()

REPORT_TICKET_OPTIONS = [
    "Report High Rank",
    "Report Exploiter",
    "Report Corruption",
    "Report Other Issue"
]
OTHER_TICKET_OPTIONS = [
    "General Question",
    "Appeal",
    "Bug Report",
    "Other"
]

TICKET_CHANNEL_GREETING = "{user_mention} Thanks for opening a ticket. Staff will be with you shortly.\n\n**Category:** {category}"

# ====================== NOT VERIFIED WARNING ======================
NOT_VERIFIED_TITLE = "Warning - Not Verified"
NOT_VERIFIED_DESCRIPTION = "You must be verified to create report or other tickets."
NOT_VERIFIED_COLOR = discord.Color.orange()

NOT_VERIFIED_UPDATE_DESCRIPTION = "You must be verified before you can update your roles."