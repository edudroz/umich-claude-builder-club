# GroupMe "No Selling" Bot

Bans anyone who posts the word **"selling"** in the club GroupMe. When it fires, the bot:

1. Deletes the message (best effort, since this uses an undocumented GroupMe endpoint)
2. Removes the member from the group
3. Adds their user ID to a ban list and removes them again if they rejoin
4. Posts a short notice in the chat

Group owners and admins are never removed. The match is the whole word "selling" in any case ("Selling", "SELLING"); words like "bestselling" don't count.

## Setup

1. **Access token:** log in at https://dev.groupme.com and click **Access Token**. This must be the token of a group **owner or admin**, because bots can't remove members on their own. Keep it secret.
2. **Group ID:** run `curl "https://api.groupme.com/v3/groups?token=YOUR_TOKEN"` and find your group's `id`.
3. **Deploy** (see below) to get a public URL, e.g. `https://umich-groupme-bot.onrender.com`.
4. **Create the bot:** go to https://dev.groupme.com/bots → **Create Bot**, choose the group, and set the Callback URL to
   `https://YOUR-APP-URL/callback?secret=YOUR_CALLBACK_SECRET`
   Copy the bot ID it gives you.
5. Set the environment variables below on your host.

## Environment variables

| Variable | Required | Description |
| --- | --- | --- |
| `GROUPME_TOKEN` | yes | Admin/owner access token |
| `GROUPME_BOT_ID` | yes | Bot ID from dev.groupme.com/bots |
| `GROUP_ID` | yes | Only messages from this group are acted on |
| `CALLBACK_SECRET` | yes | Any random string; must match `?secret=` in the callback URL. Without it, anyone who finds your URL could get people kicked. |
| `DRY_RUN` | no | `1` = announce what it *would* do without removing anyone |
| `BANNED_USER_IDS` | no | Comma-separated user IDs that are always banned |
| `BAN_FILE` | no | Where the ban list is saved (default `banned.json`) |

## Deploying on Render

1. Push this branch and create a new **Web Service** on https://render.com from the repo.
2. Set **Root Directory** to `groupme-bot`.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add the environment variables above.

Free hosting tiers wipe the disk on restart, so `banned.json` can be lost. To keep bans permanently, either attach a persistent disk and point `BAN_FILE` at it, or copy banned IDs from the logs (`banned NAME (USER_ID)`) into `BANNED_USER_IDS`. Also consider turning off the group's share link or requiring admin approval to join.

## Running locally

```bash
cd groupme-bot
pip install -r requirements.txt -r requirements-dev.txt
pytest
GROUPME_TOKEN=... GROUPME_BOT_ID=... GROUP_ID=... CALLBACK_SECRET=... DRY_RUN=1 python app.py
```
