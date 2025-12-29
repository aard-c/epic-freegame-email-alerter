import requests
import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone

EPIC_API = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_TO"]

def fetch_free_games():
    response = requests.get(EPIC_API)
    data = response.json()

    now = datetime.now(timezone.utc)
    games = []

    elements = data["data"]["Catalog"]["searchStore"]["elements"]

    for game in elements:
        promos = game.get("promotions")
        if not promos:
            continue

        offers = promos.get("promotionalOffers", [])
        if not offers:
            continue

        for offer in offers[0]["promotionalOffers"]:
            start = datetime.fromisoformat(offer["startDate"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(offer["endDate"].replace("Z", "+00:00"))

            if (
                offer["discountSetting"]["discountPercentage"] == 100
                and start <= now <= end
            ):
                slug = game.get("productSlug")
                if not slug:
                    continue

                games.append({
                    "title": game["title"],
                    "url": f"https://store.epicgames.com/p/{slug}"
                })

    return games

def load_old_games():
    if not os.path.exists("last_games.json"):
        return []
    with open("last_games.json", "r") as f:
        return json.load(f)

def save_games(games):
    with open("last_games.json", "w") as f: 
        json.dump(games, f, indent=2)

def build_html_email(new_games):
    items = ""
    for game in new_games:
        items += f"""
        <tr>
          <td style="padding:16px;border-bottom:1px solid #eee;">
            <strong>{game['title']}</strong><br>
            <a href="{game['url']}" target="_blank">Get it free →</a>
          </td>
        </tr>
        """

    return f"""
    <html>
      <body style="font-family:Arial;background:#f6f6f6;padding:20px;">
        <table width="100%" style="max-width:600px;margin:auto;background:#ffffff;border-radius:12px;">
          <tr>
            <td style="padding:24px;text-align:center;">
              <h1>🎮 New Free Epic Games</h1>
              <p>Fresh free games just dropped.</p>
            </td>
          </tr>
          {items}
        </table>
      </body>
    </html>
    """
    
def send_email(html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "New Free Games on Epic Store"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_TO
    
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        

def main():
    current_games = fetch_free_games()
    old_games = load_old_games()

    old_titles = {g["title"] for g in old_games}
    new_games = [g for g in current_games if g["title"] not in old_titles]

    if new_games:
        html = build_html_email(new_games)
        send_email(html)
        save_games(current_games)
        print("Email sent.")
    else:
        print("No new games.")

if __name__ == "__main__":
    main()