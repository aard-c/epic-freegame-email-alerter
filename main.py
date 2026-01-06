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
    response = requests.get(EPIC_API, timeout=15)
    data = response.json()

    games = []

    elements = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])

    for game in elements:
        promos = game.get("promotions")
        if not promos:
            continue

        if not promos.get("promotionalOffers"):
            continue

        slug = game.get("productSlug")
        if not slug:
            mappings = game.get("offerMappings", [])
            if mappings:
                slug = mappings[0].get("pageSlug")

        images = game.get("keyImages", [])
        cover = None
        for img in images:
            if img.get("type") in ["OfferImageWide", "DieselStoreFrontWide"]:
                cover = img.get("url")
                break

        end_date = "Limited time"

        offers = promos.get("promotionalOffers", [])
        if offers and offers[0].get("promotionalOffers"):
            offer = offers[0]["promotionalOffers"][0]
            if offer.get("endDate"):
                try:
                    end_dt = datetime.fromisoformat(offer["endDate"].replace("Z", "+00:00"))
                    end_date = end_dt.strftime("%d %B %Y")
                except:
                    pass

        games.append({
            "title": game.get("title"),
            "url": f"https://store.epicgames.com/p/{slug}" if slug else "https://store.epicgames.com/free-games",
            "end_date": end_date,
            "image": cover
        })

    if len(games) > 2:
        games = [games[-2]]

    return games




def load_old_games():
    if not os.path.exists("last_games.json"):
        return []
    with open("last_games.json", "r") as f:
        return json.load(f)

def save_games(games):
    with open("last_games.json", "w") as f:
        json.dump(games, f, indent=2)

def build_html_email(games):
    cards = ""

    for game in games:
        img_block = f"""
        <img src="{game['image']}" alt="{game['title']}" style="width:100%;border-radius:12px 12px 0 0;display:block;">
        """ if game["image"] else ""

        cards += f"""
        <tr>
          <td style="padding:0 0 24px 0;">
            <table width="100%" style="background:#1f1f1f;border-radius:12px;overflow:hidden;">
              <tr>
                <td>{img_block}</td>
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

    if new_games:
        html = build_html_email(new_games)
        send_email(html)
        save_games(current_games)
        print("Email sent.")
    else:
        print("No new games.")

if __name__ == "__main__":
    main()
