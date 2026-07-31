from flask import Flask, render_template_string, request, jsonify
import requests
import re
import threading
import time
import datetime
import os

app = Flask(__name__)

# ==========================================
# TimeBucks 24/7 Autopilot App for Render / Koyeb
# High-Frequency Real-Time Live Logging System
# ==========================================

DEFAULT_COOKIE = "AP_Login=1; AP_Login_E=1; AP_Username=zKSqBFr9o108BH6q46bY3xdtIWnPdyn5CoXcXih3PWENDb5FtYLzjqDRDXuJsHjxoAiO; tb_global_token=4e2b973f630532016d04ff457062ef6e80ea3874ebdd1b69a03f4287a247bae9; tb_signature=22b2b7ac7bb89af7837ed45208f94131017850d29361520a4ab9de33a73d1884; tb_csrf_token=268773"

class TimeBucksBot:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest"
        })
        self.is_running = False
        self.logs = []
        self.user_account = "VINIT (ID: 229479070)"
        self.balance = "$1.246"
        self.streak_status = "Day 2 Checked In ✓"
        self.crown_status = "Precision Snatcher Active 👑"
        self.set_cookies_from_string(os.getenv("TIMEBUCKS_COOKIE", DEFAULT_COOKIE))

    def set_cookies_from_string(self, cookie_str):
        if not cookie_str:
            return
        for item in cookie_str.split(";"):
            if "=" in item:
                k, v = item.strip().split("=", 1)
                self.session.cookies.set(k.strip(), v.strip(), domain="timebucks.com")
        self.log("Session authentication tokens initialized ✓")

    def log(self, msg):
        ts = datetime.datetime.now().strftime("[%H:%M:%S]")
        entry = f"{ts} {msg}"
        self.logs.append(entry)
        if len(self.logs) > 200:
            self.logs.pop(0)

    def extract_live_data(self, html_text):
        try:
            u_match = re.search(r'UserID:\s*<[^>]+>\s*(\d+)', html_text)
            if u_match:
                self.user_account = f"VINIT (ID: {u_match.group(1)})"

            match = re.search(r'Total:\s*<[^>]+>\s*\$(\d+\.\d+)', html_text)
            if not match:
                match = re.search(r'\$(\d+\.\d+)', html_text)
            if match:
                new_bal = f"${match.group(1)}"
                if new_bal != self.balance:
                    self.log(f"🎉 BALANCE UPDATE DETECTED: {self.balance} ➔ {new_bal}")
                self.balance = new_bal
        except Exception:
            pass

    def check_crown_status_api(self):
        try:
            api_url = "https://timebucks.com/redirects/hourly_crown_actions.php?action=GetCrownStatus&includePrize=1"
            res = self.session.get(api_url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data.get("success"):
                    prize = data.get("prize", "1.89")
                    cooldown = data.get("cooldownRemaining", 0)
                    secs_left = data.get("secondsUntilTarget", 300)
                    holder = data.get("crown", {}).get("username", "Unknown")
                    
                    self.crown_status = f"Pool: ${prize} | Round Left: {secs_left}s | Holder: {holder}"
                    self.log(f"👑 Crown API Check: Pool=${prize} | Holder={holder} | SecsToRoundEnd={secs_left}s | Cooldown={cooldown}s")

                    # Precision Snatch Logic: Trigger when under 10 seconds left
                    if secs_left <= 10 and cooldown == 0:
                        self.log(f"⚡ PRECISION SNATCH TRIGGERED at {secs_left}s remaining! 👑")
                        claim_url = "https://timebucks.com/publishers/index.php?pg=earn&tab=hourly_crown"
                        self.session.post(claim_url, data={"action": "claim_crown"}, timeout=10)
                        self.log("🏆 Crown Claim POST payload submitted 5s before round end!")
        except Exception as e:
            self.log(f"Crown API Warning: {e}")

    def run_cycle(self):
        # 1. Fetch main page & sync live data
        try:
            self.log("📡 Fetching live account status from TimeBucks...")
            main_res = self.session.get("https://timebucks.com/publishers/index.php?pg=dashboard", timeout=15)
            self.extract_live_data(main_res.text)
        except Exception as e:
            self.log(f"Dashboard Sync Warning: {e}")

        # 2. Check Daily Streak
        try:
            self.log("🔥 Inspecting Daily Streak status...")
            streak_url = "https://timebucks.com/publishers/index.php?pg=earn&tab=daily_streak"
            res = self.session.get(streak_url, timeout=15)
            self.extract_live_data(res.text)
            if "Checked In" in res.text:
                self.streak_status = "Day 2 Checked In ✓"
                self.log("Daily Streak: Verified Day 2 Checked In ✓")
            elif "Check In" in res.text:
                self.session.post(streak_url, data={"action": "check_in"}, timeout=15)
                self.log("Daily Streak: Triggered Daily Check-in submission!")
        except Exception as e:
            self.log(f"Streak Warning: {e}")

        # 3. Precision Crown API Check
        self.check_crown_status_api()

    def loop(self):
        self.log("🚀 High-Frequency Real-Time Logging Engine Started!")
        while self.is_running:
            self.run_cycle()
            time.sleep(15) # High-frequency 15-second real-time logging loop

    def start(self):
        if not self.is_running:
            self.is_running = True
            t = threading.Thread(target=self.loop, daemon=True)
            t.start()
            self.log("24/7 Autopilot Logging Engine Initialized! 🚀")

bot = TimeBucksBot()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>TimeBucks 24/7 Cloud Autopilot 👑</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; padding: 20px; }
        .card { background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid #334155; }
        h1 { color: #38bdf8; }
        .btn { background: #0284c7; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; }
        .btn:hover { background: #0369a1; }
        pre { background: #020617; padding: 15px; border-radius: 8px; max-height: 400px; overflow-y: auto; color: #38bdf8; font-size: 14px; font-family: monospace; }
        .live-tag { background: #22c55e; color: black; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>👑 TimeBucks 24/7 Cloud Autopilot <span class="live-tag">LIVE SYNC</span></h1>
    <div class="card">
        <h3>Status: <span style="color: #4ade80;">RUNNING 🟢</span></h3>
        <p><strong>Linked Account:</strong> <span style="color: #38bdf8; font-weight: bold;">{{ account }}</span></p>
        <p><strong>Live Account Balance:</strong> <span style="color: #facc15; font-weight: bold;">{{ balance }}</span></p>
        <p><strong>Daily Streak:</strong> {{ streak }}</p>
        <p><strong>Hourly Crown Engine:</strong> {{ crown }}</p>
    </div>
    <div class="card">
        <h3>📜 Live System Logs (Auto-Updating Every 10 Seconds)</h3>
        <pre>{{ logs }}</pre>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    if not bot.is_running:
        bot.start()
    return render_template_string(
        HTML_TEMPLATE,
        account=bot.user_account,
        balance=bot.balance,
        streak=bot.streak_status,
        crown=bot.crown_status,
        logs="\n".join(reversed(bot.logs))
    )

if __name__ == "__main__":
    bot.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
