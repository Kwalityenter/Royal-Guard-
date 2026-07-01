import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
GROUP_ID = os.getenv("ROBLOX_GROUP_ID")
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID"))

ROBLOX_CLIENT_ID = os.getenv("ROBLOX_CLIENT_ID")
ROBLOX_CLIENT_SECRET = os.getenv("ROBLOX_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

TICKET_CATEGORY_ID = int(os.getenv("TICKET_CATEGORY_ID"))
STAFF_ROLE_ID = int(os.getenv("STAFF_ROLE_ID"))