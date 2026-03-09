<p align="center">
  <img src="https://files.catbox.moe/unmtp2.jpg" alt="MMW-Delulu Logo">
</p>

<h1 align="center">MMW-Delulu Filter Bot</h1>

<p align="center">
  A powerful and versatile Telegram bot designed for filtering, automation, and much more!
</p>

<div align="center">
  <a href="https://github.com/mmwbotzmain/MMW-Delulu/stargazers">
    <img src="https://img.shields.io/github/stars/noobgittg/MMW-Delulu?color=black&logo=github&logoColor=black&style=for-the-badge" alt="Stars" />
  </a>
  <a href="https://github.com/mmwbotzmain/MMW-Delulu/network/members">
    <img src="https://img.shields.io/github/forks/noobgittg/MMW-Delulu?color=black&logo=github&logoColor=black&style=for-the-badge" alt="Forks" />
  </a>
  <a href="https://github.com/mmwbotzmain/MMW-Delulu">
    <img src="https://img.shields.io/github/repo-size/noobgittg/MMW-Delulu?color=skyblue&logo=github&logoColor=blue&style=for-the-badge" alt="Repo Size" />
  </a>
  <a href="https://github.com/mmwbotzmain/MMW-Delulu/commits/main">
    <img src="https://img.shields.io/github/last-commit/noobgittg/MMW-Delulu?color=black&logo=github&logoColor=black&style=for-the-badge" alt="Last Commit" />
  </a>
  <a href="https://github.com/mmwbotzmain/MMW-Delulu/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-AGPL%203.0-blueviolet?style=for-the-badge" alt="License" />
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Written%20in-Python-skyblue?style=for-the-badge&logo=python" alt="Python" />
  </a>
  <a href="https://pypi.org/project/Pyrogram/">
    <img src="https://img.shields.io/pypi/v/pyrogram?color=white&label=pyrogram&logo=python&logoColor=blue&style=for-the-badge" alt="Pyrogram" />
  </a>
</div>

<hr>

## ✨ Features

- ✅ Auto Filter
- ✅ Manual Filter
- ✅ IMDB Search and Info
- ✅ Admin Commands
- ✅ Broadcast Messages
- ✅ File Indexing
- ✅ Inline Search
- ✅ Random Pics Generator
- ✅ User and Chat Stats
- ✅ Ban, Unban, Enable, Disable Commands
- ✅ File Storage
- ✅ Auto-Approval for Requests
- ✅ Feedback System
- ✅ Font Styling (`/font`)
- ✅ User Promotion/Demotion
- ✅ Pin/Unpin Messages
- ✅ Image-to-Link Conversion
- ✅ **Auto Delete** — Automatically removes user messages after processing
- ✅ **Auto Restart**
- ✅ **Keep Alive Function** — Prevents the bot from sleeping on platforms like Koyeb
- ✅ **Delete Files by Query** — `/deletefiles <keyword>` removes files by name match
- ✅ Auto delete for files
- ✅ Channel file sending mode with multiple channel support

<hr>

## 📋 Commands

| Command | Description |
|---|---|
| `/start` | Start the bot |
| `/stats` | Get status of files in DB |
| `/connections` | See all connected groups |
| `/settings` | Open settings menu |
| `/filter` | Add manual filters |
| `/filters` | View filters |
| `/connect` | Connect to PM |
| `/disconnect` | Disconnect from PM |
| `/del` | Delete a filter |
| `/delall` | Delete all filters |
| `/deleteall` | Delete all indexed files |
| `/delete` | Delete a specific file from index |
| `/info` | Get user info |
| `/id` | Get Telegram IDs |
| `/imdb` | Fetch info from IMDB |
| `/search` | Search from various sources |
| `/setskip` | Skip number of messages when indexing files |
| `/users` | Get list of users and IDs |
| `/chats` | Get list of chats and IDs |
| `/leave` | Leave from a chat |
| `/disable` | Disable a chat |
| `/enable` | Re-enable a chat |
| `/ban` | Ban a user |
| `/unban` | Unban a user |
| `/channel` | Get list of total connected channels |
| `/broadcast` | Broadcast a message to all users |
| `/grp_broadcast` | Broadcast a message to all connected groups |
| `/status` | Check Heroku dyno, bot uptime, and working day prediction |
| `/set_template` | Set a custom IMDB template for individual groups |
| `/gfilter` | Add global filters |
| `/gfilters` | View list of all global filters |
| `/delg` | Delete a specific global filter |
| `/delallg` | Delete all global filters from the bot's database |
| `/deletefiles` | Delete PreDVD and CamRip files from the bot's database |
| `/restart` | Restart the bot server |
| `/telegraph` | Get Telegraph link of any file under 5MB |
| `/stickerid` | Get ID and unique ID of sticker |
| `/font` | Get any type of font of any word |
| `/purgerequests` | Delete all join requests from database |
| `/totalrequests` | Get total number of join requests from database |

<hr>

## 🔧 Variables

### Required

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Create a bot using [@BotFather](https://t.me/BotFather) and get the Telegram API token |
| `API_ID` | Get from [telegram.org](https://my.telegram.org/apps) |
| `API_HASH` | Get from [telegram.org](https://my.telegram.org/apps) |
| `CHANNELS` | Username or ID of channel or group. Separate multiple IDs by space |
| `ADMINS` | Username or ID of Admin. Separate multiple Admins by space |
| `DATABASE_URI` | MongoDB URI (required when `SQLDB` is not set) |
| `DATABASE_URI2` | MongoDB URI (required when `SQLDB` is not set) |
| `DATABASE_URI3` | MongoDB URI (required when `SQLDB` is not set) |
| `DATABASE_URI4` | MongoDB URI (required when `SQLDB` is not set) |
| `DATABASE_URI5` | MongoDB URI (required when `SQLDB` is not set) |
| `DATABASE_NAME` | Name of the database in MongoDB |
| `LOG_CHANNEL` | A Telegram channel to log the bot's activities. Bot must be admin |

> **Note:** `DATABASE_URI2` through `DATABASE_URI5` are also accepted for multiple MongoDB shards.

### Optional

| Variable | Description |
|---|---|
| `PICS` | Telegraph links of images to show in start message (space-separated) |
| `FILE_STORE_CHANNEL` | Channel(s) for file store links (space-separated) |

> Refer to `info.py` for the full list of optional variables.

<hr>

## 🚀 Deployment

<details>
<summary><b>Deploy To Heroku</b></summary>
<br>
<a href="https://heroku.com/deploy?template=https://github.com/mmwbotzmain/MMW-Delulu">
  <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy To Heroku">
</a>
</details>

<details>
<summary><b>Deploy To Koyeb</b></summary>
<br>

<a href="https://app.koyeb.com/deploy?type=git&repository=github.com/mmwbotzmain/MMW-Delulu&branch=main&name=mmw-delulu">
  <img src="https://www.koyeb.com/static/images/deploy/button.svg" alt="Deploy to Koyeb">
</a>

<br><br>

#### Full Koyeb Tutorial 

**1. Fork this Repository**

Fork [this repo](https://github.com/mmwbotzmain/MMW-Delulu) to your GitHub account and keep your branch updated.

**2. Create Service in Koyeb**

- Go to Koyeb → Create Web Service (or Worker)
- Select your forked GitHub repository
- Branch: `main`
- Runtime: Python

**3. Set Koyeb Environment Variables**

Required Telegram vars:
- `BOT_TOKEN`, `API_ID`, `API_HASH`, `ADMINS`, `CHANNELS`, `LOG_CHANNEL`


> MongoDB vars required.

**5. Deploy**

Click **Deploy** in Koyeb. Once build completes, open Telegram and run `/start` to verify the bot is live.

**6. Troubleshooting**

- Make sure the bot is admin in all channels configured in `CHANNELS`

</details>

<details>
<summary><b>Deploy To Render</b></summary>
<br>

Use these commands:

- **Build Command:** `pip3 install -U -r requirements.txt`
- **Start Command:** `python3 bot.py`

Go to [uptimerobot.com](https://uptimerobot.com/) and add a monitor to keep your bot alive.

<img src="https://telegra.ph/file/a79a156e44f43c9833b50.jpg" alt="Render template">

<br>

<a href="https://render.com/deploy?repo=https://github.com/mmwbotzmain/MMW-Delulu/tree/Delulu">
  <img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render">
</a>

</details>

<details>
<summary><b>Deploy To VPS</b></summary>
<br>

```bash
git clone https://github.com/mmwbotzmain/MMW-Delulu

# Install dependencies
pip3 install -U -r requirements.txt

# Edit info.py with your variables, then run:
python3 bot.py
```

</details>

<hr>

## 💬 Support

<p>
  <a href="https://t.me/MRXSUPPORTS" target="_blank">
    <img src="https://img.shields.io/badge/Telegram-Support%20Group-30302f?style=flat&logo=telegram" alt="Telegram Group">
  </a>
  <a href="https://t.me/mallumovieworldmain2" target="_blank">
    <img src="https://img.shields.io/badge/Telegram-Channel-30302f?style=flat&logo=telegram" alt="Telegram Channel">
  </a>
</p>

<hr>

## 🙏 Credits

- [Dan](https://github.com/pyrogram/pyrogram) — Pyrogram & Pyrofork Libraries
- [Mahesh](https://github.com/Mahesh0253/Media-Search-bot) — Media Search Bot base
- [EvamariaTG](https://github.com/EvamariaTG/EvaMaria) — EvaMaria Bot base
- [Trojanz](https://github.com/trojanzhex/Unlimited-Filter-Bot) — Unlimited Filter Bot
- MMW BOTZ — Ping feature & Editing and maintaining this repository

> Interested in collaborating? Fork the repo and create a pull request → [Click Here To Fork](https://github.com/mmwbotzmain/MMW-Delulu/fork)

<hr>

## 📜 License & Disclaimer

<a href="https://www.gnu.org/licenses/agpl-3.0.en.html" target="_blank">
  <img src="https://www.gnu.org/graphics/agplv3-155x51.png" alt="GNU AGPLv3">
</a>

This project is licensed under the [GNU AGPL 3.0](https://github.com/mmwbotzmain/MMW-Delulu/blob/main/LICENSE).

> **Note to Devs:** Fork the repo and edit as per your needs.

⚠️ **Selling this code for monetary gain is strictly prohibited.**
