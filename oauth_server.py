import os
import requests
from flask import Flask, request

from config import ROBLOX_CLIENT_ID, ROBLOX_CLIENT_SECRET, REDIRECT_URI
from database import save_link, pop_pending_state

app = Flask(__name__)

AUTHORIZE_URL = "https://apis.roblox.com/oauth/v1/authorize"
TOKEN_URL = "https://apis.roblox.com/oauth/v1/token"
USERINFO_URL = "https://apis.roblox.com/oauth/v1/userinfo"


def build_authorize_url(state: str) -> str:
    return (
        f"{AUTHORIZE_URL}?client_id={ROBLOX_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=openid%20profile"
        f"&response_type=code"
        f"&state={state}"
    )


@app.route("/callback")
def callback():
    code = request.args.get("code")
    state = request.args.get("state")

    if not code or not state:
        return "Missing code or state.", 400

    discord_id = pop_pending_state(state)
    if not discord_id:
        return "Invalid or expired verification link. Run /verify again in Discord.", 400

    token_resp = requests.post(TOKEN_URL, data={
        "client_id": ROBLOX_CLIENT_ID,
        "client_secret": ROBLOX_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    })

    if token_resp.status_code != 200:
        return f"Token exchange failed: {token_resp.text}", 400

    access_token = token_resp.json().get("access_token")

    userinfo_resp = requests.get(USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
    if userinfo_resp.status_code != 200:
        return f"Failed to fetch user info: {userinfo_resp.text}", 400

    userinfo = userinfo_resp.json()
    roblox_id = userinfo.get("sub")
    roblox_username = userinfo.get("preferred_username") or userinfo.get("nickname")

    save_link(discord_id, roblox_id, roblox_username)

    return f"""
        <html><body style="font-family:sans-serif;text-align:center;margin-top:50px;">
        <h2>Verified as {roblox_username}!</h2>
        <p>You can close this tab and return to Discord.</p>
        </body></html>
    """


def run_oauth_server():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)