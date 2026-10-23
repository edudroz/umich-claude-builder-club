# GroupMe Anti-Ticket-Spam Bot

Stops spam accounts that flood the club GroupMe with ticket sales and "giveaways". When a message is flagged, the bot:

1. Deletes the message (best effort, since this uses an undocumented GroupMe endpoint). Follow-up messages from an account that was already removed get deleted too.
2. Removes the member from the group
3. Adds their user ID to a ban list and removes them again if they rejoin
4. Posts a short notice in the chat: at most one every 5 minutes, and never including the spammer's name (spam accounts hide links and phone numbers in their names)

Group owners, admins and anyone in `EXEMPT_USER_IDS` are never removed.

## What gets flagged

- Any message with the word **"selling"**
- A message that mentions **tickets** (`ticket`, `tix`, 🎟️ ...) **and** a sale or giveaway call to action: a price (`$40`), a payment app (Venmo, Cash App, Zelle, PayPal), `DM me` / `text me` / `hmu`, `giving away`, `free tickets`, `for sale`, `WTS`/`WTB`/`ISO`

Questions like "where do I buy tickets for the hackathon?" or "do I need a ticket?" are **not** flagged.

Spam bots disguise words, so text is normalized first: fancy Unicode fonts (𝐒𝐞𝐥𝐥𝐢𝐧𝐠), look-alike Cyrillic letters, hidden zero-width characters, leetspeak (`se11ing`, `T1CKETS`) and spaced-out letters (`s e l l i n g`) are all caught.

**Not caught:** spam that's only an image with no text. Watch for it in the logs and add a check if it becomes a problem.

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
| `EXEMPT_USER_IDS` | no | Comma-separated user IDs that are never removed (e.g. e-board members who post about event tickets) |
| `ANNOUNCE_COOLDOWN` | no | Seconds between chat notices during a spam wave (default `300`) |
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
