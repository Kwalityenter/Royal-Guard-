import aiohttp
from config import GROUP_ID


async def get_group_role(roblox_id: str):
    url = f"https://groups.roblox.com/v2/users/{roblox_id}/groups/roles"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            for g in data.get("data", []):
                if str(g["group"]["id"]) == str(GROUP_ID):
                    return {"rank_id": g["role"]["rank"], "rank_name": g["role"]["name"]}
            return None


async def get_roblox_username(roblox_id: str):
    url = f"https://users.roblox.com/v1/users/{roblox_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return data.get("name")