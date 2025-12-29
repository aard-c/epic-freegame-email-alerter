# Epic Games Free Game Email Alert Bot

This project is a Python-based automation tool that **monitors Epic Games Store free game promotions** and **sends a styled email alert** whenever free games are available.

It runs **fully automatically using GitHub Actions**, meaning:
- No local setup required
- Runs on a schedule
- Sends emails only when free games are detected

---

## Features

- Detects **currently free** Epic Games Store games
- Avoids false positives from discounted (but not free) games
- Sends **modern, Epic-style HTML emails**
- Email includes:
  - Game cover images
  - “Free until DATE” text
  - Direct **Get Free Game** button
- Designed to handle Epic’s inconsistent API behavior
- Fully automated via **GitHub Actions**
- Uses environment variables for security
- Safe to use as a **public repository** (no secrets committed)

---

## How to Run

### 1. Fork this repository
Click the **Fork** button on GitHub.  
This creates a personal copy under your own GitHub account.

---

### 2. Add your email secrets
In **your fork**:

- Go to **Settings → Secrets and variables → Actions**
- Add the following secrets:
  - `EMAIL_ADDRESS` — your email address (sender)
  - `EMAIL_PASSWORD` — your email app password
  - `EMAIL_TO` — where alerts should be sent

These secrets are private and only apply to your fork.

---

### 3. Automation starts automatically
- The GitHub Actions workflow is already included
- GitHub’s servers run the script on a schedule
- Your computer does **not** need to be on

---

### 4. Receive email alerts
- Emails are sent **from your email**
- Emails are delivered **to you**
- The original repository owner is not involved

Each fork runs completely independently.

---

