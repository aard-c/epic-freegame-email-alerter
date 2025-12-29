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

            if offer["discountSetting"]["discountPercentage"] == 100 and start <= now <= end:
                slug = game.get("productSlug")
                if not slug:
                    continue

                images = game.get("keyImages", [])
                cover = None
                for img in images:
                    if img.get("type") in ["OfferImageWide", "DieselStoreFrontWide"]:
                        cover = img.get("url")
                        break

                games.append({
                    "title": game["title"],
                    "url": f"https://store.epicgames.com/p/{slug}",
                    "end_date": end.strftime("%d %B %Y"),
                    "image": cover
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
    cards = ""
    for game in new_games:
        img_block = f"""
        <img src="{game['image']}" alt="{game['title']}" style="width:100%;border-radius:12px 12px 0 0;display:block;">
        """ if game["image"] else ""

        cards += f"""
        <tr>
          <td style="padding:0 0 24px 0;">
            <table width="100%" style="background:#1f1f1f;border-radius:12px;overflow:hidden;">
              <tr>
                <td>
                  {img_block}
                </td>
              </tr>
              <tr>
                <td style="padding:20px;">
                  <h2 style="margin:0 0 8px 0;font-size:20px;color:#ffffff;">
                    {game['title']}
                  </h2>
                  <p style="margin:0 0 16px 0;color:#b5b5b5;font-size:14px;">
                    Free until {game['end_date']}
                  </p>
                  <a href="{game['url']}" target="_blank"
                     style="display:inline-block;background:#0078f2;color:#ffffff;
                     text-decoration:none;padding:12px 18px;border-radius:6px;
                     font-weight:600;font-size:14px;">
                    Get Free Game
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        """

    return f"""
    <html>
      <body style="margin:0;padding:0;background:#121212;font-family:Arial,Helvetica,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="padding:24px 0;">
          <tr>
            <td align="center">
              <table width="100%" style="max-width:600px;">
                <tr>
                  <td style="text-align:center;padding:24px;">
                    <h1 style="color:#ffffff;margin:0;font-size:26px;">
                      🎮 New Free Epic Games
                    </h1>
                    <p style="color:#9e9e9e;margin:8px 0 0 0;">
                      Available now on Epic Games Store
                    </p>
                  </td>
                </tr>
                {cards}
                <tr>
                  <td style="text-align:center;padding:12px;">
                    <a href="https://store.epicgames.com/free-games" target="_blank"
                       style="color:#9e9e9e;font-size:12px;text-decoration:none;">
                      View all free games on Epic Games Store
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

def send_email(html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🎮 New Free Games on Epic Games Store"
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

    if True:
        html = build_html_email(current_games)
        send_email(html)
        save_games(current_games)
        print("Email sent.")
    else:
        print("No new games.")

if __name__ == "__main__":
    main()
