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
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Error - Royal Guard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #1a1a2e;
            font-family: 'Segoe UI', sans-serif;
        }
        .card {
            background: #16213e;
            border: 1px solid #e76f51;
            border-radius: 20px;
            padding: 50px 60px;
            text-align: center;
            max-width: 480px;
            width: 90%;
        }
        .emoji-big { font-size: 72px; display: block; margin-bottom: 20px; }
        h1 { color: #e76f51; font-size: 26px; margin-bottom: 16px; }
        p { color: #aaa; font-size: 15px; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="card">
        <span class="emoji-big">❌</span>
        <h1>Invalid or Expired Link</h1>
        <p>This verification link is invalid or has already been used.<br><br>
        Please run <strong>/verify</strong> again in Discord to get a new link.</p>
    </div>
</body>
</html>
""", 400

    # Exchange code for access token
    token_resp = requests.post(TOKEN_URL, data={
        "client_id": ROBLOX_CLIENT_ID,
        "client_secret": ROBLOX_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    })

    if token_resp.status_code != 200:
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Error - Royal Guard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #1a1a2e;
            font-family: 'Segoe UI', sans-serif;
        }}
        .card {{
            background: #16213e;
            border: 1px solid #e76f51;
            border-radius: 20px;
            padding: 50px 60px;
            text-align: center;
            max-width: 480px;
            width: 90%;
        }}
        .emoji-big {{ font-size: 72px; display: block; margin-bottom: 20px; }}
        h1 {{ color: #e76f51; font-size: 26px; margin-bottom: 16px; }}
        p {{ color: #aaa; font-size: 15px; line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="card">
        <span class="emoji-big">⚠️</span>
        <h1>Token Exchange Failed</h1>
        <p>Something went wrong during verification.<br><br>
        Please try again by running <strong>/verify</strong> in Discord.</p>
    </div>
</body>
</html>
""", 400

    access_token = token_resp.json().get("access_token")

    # Get Roblox identity
    userinfo_resp = requests.get(USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
    if userinfo_resp.status_code != 200:
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Error - Royal Guard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #1a1a2e;
            font-family: 'Segoe UI', sans-serif;
        }
        .card {
            background: #16213e;
            border: 1px solid #e76f51;
            border-radius: 20px;
            padding: 50px 60px;
            text-align: center;
            max-width: 480px;
            width: 90%;
        }
        .emoji-big { font-size: 72px; display: block; margin-bottom: 20px; }
        h1 { color: #e76f51; font-size: 26px; margin-bottom: 16px; }
        p { color: #aaa; font-size: 15px; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="card">
        <span class="emoji-big">⚠️</span>
        <h1>Failed to Fetch User Info</h1>
        <p>Could not retrieve your Roblox account details.<br><br>
        Please try again by running <strong>/verify</strong> in Discord.</p>
    </div>
</body>
</html>
""", 400

    userinfo = userinfo_resp.json()
    roblox_id = userinfo.get("sub")
    roblox_username = userinfo.get("preferred_username") or userinfo.get("nickname")

    save_link(discord_id, roblox_id, roblox_username)

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verified - Royal Guard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #1a1a2e;
            font-family: 'Segoe UI', sans-serif;
            overflow: hidden;
        }}

        .card {{
            background: #16213e;
            border: 1px solid #2a9d8f;
            border-radius: 20px;
            padding: 50px 60px;
            text-align: center;
            max-width: 480px;
            width: 90%;
            box-shadow: 0 0 40px rgba(42, 157, 143, 0.2);
            animation: fadeUp 0.6s ease forwards;
        }}

        @keyframes fadeUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .emoji-big {{
            font-size: 72px;
            display: block;
            margin-bottom: 20px;
            animation: bounce 1s ease infinite alternate;
        }}

        @keyframes bounce {{
            from {{ transform: translateY(0); }}
            to {{ transform: translateY(-10px); }}
        }}

        h1 {{
            color: #2a9d8f;
            font-size: 28px;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }}

        .username {{
            color: #e9c46a;
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 16px;
        }}

        p {{
            color: #aaa;
            font-size: 15px;
            line-height: 1.6;
        }}

        .divider {{
            border: none;
            border-top: 1px solid #2a9d8f33;
            margin: 24px 0;
        }}

        .badge {{
            display: inline-block;
            background: #2a9d8f22;
            border: 1px solid #2a9d8f;
            color: #2a9d8f;
            border-radius: 20px;
            padding: 6px 18px;
            font-size: 13px;
            letter-spacing: 1px;
            margin-top: 8px;
        }}

        canvas {{
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            pointer-events: none;
            z-index: 999;
        }}
    </style>
</head>
<body>
    <canvas id="confetti"></canvas>

    <div class="card">
        <span class="emoji-big">🎉</span>
        <h1>Verification Complete!</h1>
        <div class="username">@{roblox_username}</div>
        <p>Your Roblox account has been successfully linked to your Discord account.</p>
        <hr class="divider">
        <p>You can now close this tab and return to Discord. 🪖</p>
        <div class="badge">✅ ROYAL GUARD VERIFIED</div>
    </div>

    <script>
        const canvas = document.getElementById('confetti');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const colors = ['#2a9d8f', '#e9c46a', '#e76f51', '#f4a261', '#ffffff', '#a8dadc'];
        const pieces = Array.from({{ length: 160 }}, () => ({{
            x: Math.random() * canvas.width,
            y: Math.random() * -canvas.height,
            r: Math.random() * 8 + 4,
            d: Math.random() * 3 + 1,
            color: colors[Math.floor(Math.random() * colors.length)],
            tilt: Math.random() * 10 - 5,
            tiltSpeed: Math.random() * 0.1 + 0.05,
            angle: 0
        }}));

        let frame = 0;
        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            frame++;
            pieces.forEach(p => {{
                p.angle += p.tiltSpeed;
                p.tilt = Math.sin(p.angle) * 12;
                p.y += p.d;
                if (p.y > canvas.height) {{
                    p.y = -10;
                    p.x = Math.random() * canvas.width;
                }}
                ctx.beginPath();
                ctx.lineWidth = p.r;
                ctx.strokeStyle = p.color;
                ctx.moveTo(p.x + p.tilt + p.r / 2, p.y);
                ctx.lineTo(p.x + p.tilt, p.y + p.tilt + p.r / 2);
                ctx.stroke();
            }});
            if (frame < 300) requestAnimationFrame(draw);
            else ctx.clearRect(0, 0, canvas.width, canvas.height);
        }}
        draw();
    </script>
</body>
</html>
"""


def run_oauth_server():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)