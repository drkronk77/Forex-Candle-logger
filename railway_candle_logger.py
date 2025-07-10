import os
import time
import json
import requests
from datetime import datetime
import pytz

# === CONFIGURATION ===
API_KEY = "d1noa39r01qovv8kh7cgd1noa39r01qovv8kh7d0"
DROPBOX_TOKEN = "ph6ywv51w9lk62t"
DROPBOX_FOLDER = "/Apps/ForexLogger"
SYMBOL = "OANDA:GBP_USD"
INTERVAL_SECONDS = 10
TIMEZONE = "Europe/London"

# === TRADING WINDOW (UK: 13:00 - 16:00) ===
def is_trading_hours():
    now = datetime.now(pytz.timezone(TIMEZONE))
    return now.weekday() < 5 and 13 <= now.hour < 16

# === LOG FILE ===
def get_filename():
    date = datetime.now(pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d")
    return f"{DROPBOX_FOLDER}/{date}_GBPUSD.json"

# === FETCH PRICE ===
def fetch_price():
    url = f"https://finnhub.io/api/v1/quote?symbol={SYMBOL}&token={API_KEY}"
    r = requests.get(url)
    data = r.json()
    return {{
        "timestamp": datetime.now(pytz.timezone(TIMEZONE)).isoformat(),
        "price": data.get("c")
    }}

# === APPEND & UPLOAD TO DROPBOX ===
def upload_to_dropbox(local_path, dropbox_path):
    with open(local_path, "rb") as f:
        data = f.read()
    r = requests.post(
        "https://content.dropboxapi.com/2/files/upload",
        headers={{
            "Authorization": f"Bearer {{DROPBOX_TOKEN}}",
            "Content-Type": "application/octet-stream",
            "Dropbox-API-Arg": json.dumps({{
                "path": dropbox_path,
                "mode": "overwrite",
                "mute": True
            }})
        }},
        data=data
    )
    if r.status_code != 200:
        print("❌ Dropbox upload failed:", r.text)

def main():
    local_file = "candles_temp.json"
    if not os.path.exists(local_file):
        with open(local_file, "w") as f:
            json.dump([], f)

    while True:
        if is_trading_hours():
            candle = fetch_price()
            print("📈", candle)
            with open(local_file, "r+") as f:
                candles = json.load(f)
                candles.append(candle)
                f.seek(0)
                json.dump(candles, f, indent=2)
                f.truncate()
            upload_to_dropbox(local_file, get_filename())
        else:
            print("⏱️ Outside trading hours...")
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
