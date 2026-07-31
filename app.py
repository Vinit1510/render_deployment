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
# Web Session & Cookie-Authenticated Automation Engine
# ==========================================

DEFAULT_COOKIE = "cf_clearance=L.TRCap.N8zIP0CDzDwvB6VbEiEqF2vzW9s5Y2eo8eE-1785477122-1.2.1.1-MmPeDdyLrBIP_bkpNgCasJof2QBmG21weAUXzMUX02w3Kv4ley3TVsYhEkmg5Nv6liSPDageUik1WPck43kfdARfiFm5iZ3ZCOF2_WeybXVsqnq4mSc5NrcY4Ybu.0q6S4JOeAxJhJfv.wP6ZecML5Cb91evL8HSh2hYin8Rirj_8Z3LEEHcO5cMtBarbO4kEUc6i2FDWRXmxiunIraWMMq_mlR.m.U4TRpqRDB8VHLtIHHlTV45xZQa_m3hYpprytgUO9yn1iQ9CXFfgirxS3dGPIUMYIf9Z90yd_S3LISPGrXEL38nOtAkdWXq9FSKxrOW7OqVM97feF2r8vnCDNN_Wbp0rilLo_tylEhytOYap4yNcp6PqCJNGzoj9CcKLJN0ILiFg7L0xJ6nRJsvguZPJWETrSUIKoKyBS46pavbqHZZoLP25b._PiNpfaJY; AP_Login=1; AP_Login_E=1; AP_Username=zKSqBFr9o108BH6q46bY3xdtIWnPdyn5CoXcXih3PWENDb5FtYLzjqDRDXuJsHjxoAiO; tb_global_token=4e2b973f630532016d04ff457062ef6e80ea3874ebdd1b69a03f4287a247bae9; tb_signature=22b2b7ac7bb89af7837ed45208f94131017850d29361520a4ab9de33a73d1884; tb_csrf_token=268773"

class TimeBucksBot:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://timebucks.com",
            "Referer": "https://timebucks.com/publishers/index.php?pg=earn&tab=hourly_crown"
        })
        self.is_running = False
        self.logs = []
        self.user_account = "VINIT (ID: 229479070)"
        self.balance = "$1.246"
        self.streak_status = "Day 2 Checked In ✓"
        self.crown_status = "Precision Snatcher Active 👑"
        self.csrf_token = "268773"
        self.set_cookies_from_string(os.getenv("TIMEBUCKS_COOKIE", DEFAULT_COOKIE))

    def set_cookies_from_string(self, cookie_str):
        if not cookie_str:
            return
        for item in cookie_str.split(";"):
            if "=" in item:
                k, v = item.strip().split("=", 1)
                k_clean = k.strip()
                v_clean = v.strip()
                self.session.cookies.set(k_clean, v_clean, domain="timebucks.com")
                if k_clean == "tb_csrf_token":
                    self.csrf_token = v_clean
        self.log("Full session cookies & Cloudflare clearance tokens loaded ✓")

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

            csrf_match = re.search(r'name=["\']tb_csrf_token["\']\s+value=["\']([^"\'\s]+)["\']', html_text)
            if csrf_match:
                self.csrf_token = csrf_match.group(1)
        except Exception:
            pass

    def check_crown_status_api(self):
        try:
            api_url = "https://timebucks.com/redirects/hourly_crown_actions.php?action=GetCrownStatus&includePrize=1"
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "application/json, text/javascript, */*; q=0.01"
            }
            res = self.session.get(api_url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data.get("success"):
                    prize = data.get("prize", "1.89")
                    cooldown = data.get("cooldownRemaining", 0)
                    secs_left = data.get("secondsUntilTarget", 300)
                    holder = data.get("crown", {}).get("username", "Unknown")
                    
                    self.crown_status = f"Pool: ${prize} | Round Left: {secs_left}s | Holder: {holder}"
                    self.log(f"👑 Crown API Sync: Pool=${prize} | Holder={holder} | SecsToRoundEnd={secs_left}s | Cooldown={cooldown}s")

                    # Claim Crown execution
                    if cooldown == 0:
                        self.log(f"⚡ EXECUTING CROWN CLAIM REQUEST (Cooldown Ready, {secs_left}s left)... 👑")
                        claim_url = "https://timebucks.com/publishers/index.php?pg=earn&tab=hourly_crown"
                        payload = {
                            "action": "claim_crown",
                            "tb_csrf_token": self.csrf_token
                        }
                        claim_res = self.session.post(claim_url, data=payload, timeout=10)
                        if claim_res.status_code == 200:
                            self.extract_live_data(claim_res.text)
                            self.log("🏆 Crown Claim POST payload successfully submitted with session tokens!")
                        else:
                            self.log(f"Claim response status: {claim_res.status_code}")
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
                self.session.post(streak_url, data={"action": "check_in", "tb_csrf_token": self.csrf_token}, timeout=15)
                self.log("Daily Streak: Triggered Daily Check-in submission!")
        except Exception as e:
            self.log(f"Streak Warning: {e}")

        # 3. Precision Crown Check
        self.check_crown_status_api()

    def loop(self):
        self.log("🚀 High-Frequency Real-Time Logging Engine Started!")
        while self.is_running:
            self.run_cycle()
            time.sleep(15)

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
