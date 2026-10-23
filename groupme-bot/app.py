"""GroupMe bot that bans members who post about selling or giving away tickets.

GroupMe POSTs every message in the group to /callback. If a message is
flagged, we delete it, remove the member, and remember their user_id so
they get removed again if they rejoin.

A message is flagged when it contains "selling", or when it mentions tickets
together with a sale/giveaway call to action (payment app, price, "DM me",
"giving away", ...). Spam bots disguise words with fancy fonts, look-alike
letters, leetspeak and spacing, so text is normalized before matching.

Bots can't remove members, so removals use a group owner/admin's access token.
"""

import json
import logging
import os
import re
import threading
import time
import unicodedata

import requests
from flask import Flask, abort, request

API = "https://api.groupme.com/v3"

GROUPME_TOKEN = os.environ.get("GROUPME_TOKEN", "")
GROUPME_BOT_ID = os.environ.get("GROUPME_BOT_ID", "")
GROUP_ID = os.environ.get("GROUP_ID", "")
CALLBACK_SECRET = os.environ.get("CALLBACK_SECRET", "")
BAN_FILE = os.environ.get("BAN_FILE", "banned.json")
DRY_RUN = os.environ.get("DRY_RUN", "0") == "1"
EXEMPT_USER_IDS = {u.strip() for u in os.environ.get("EXEMPT_USER_IDS", "").split(",") if u.strip()}
# During a spam wave, post at most one notice per this many seconds.
ANNOUNCE_COOLDOWN = int(os.environ.get("ANNOUNCE_COOLDOWN", "300"))

log = logging.getLogger("groupme-bot")
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
_ban_lock = threading.Lock()
_announce_lock = threading.Lock()
_last_announce = 0.0
_removed_since_announce = 0


# --- detection --------------------------------------------------------------

ZERO_WIDTH = re.compile("[­​-‏⁠-⁤﻿]")
# Cyrillic/Greek letters that look like Latin ones (NFKC leaves these alone).
LOOKALIKES = str.maketrans("аеорсухіјѕԁɡκοτνΑΕΙΚΜΝΟΡΤΧ", "aeopcyxijsdgkotvaeikmnoptx")
LEET = str.maketrans("013457@$!|", "oieastasii")
LEET_RUN = re.compile(r"[013457@$!|]+(?=[a-z])")
# Letters split up with spaces/punctuation: "s e l l i n g", "t.i.x"
SPACED_OUT = re.compile(r"(?<![a-z0-9])(?:[a-z0-9][\W_]{1,3}){2,}[a-z0-9](?![a-z0-9])")

SELLING = re.compile(r"\bse(?:[li]{2,3}ing?|[li]ing)\b")  # selling, sellin, seling, se11ing
TICKET = re.compile(r"\b(?:tickets?|tix|tkts?|tickts?)\b")
TICKET_EMOJI = re.compile("[\U0001F39F\U0001F3AB]")
INTENT = re.compile(
    r"\b(?:sel+s?|for sale|wts|wtb|obo|giv(?:e|ing) ?away|giveaways?|free (?:tickets?|tix)"
    r"|iso|will pay|paying|dm(?: me)?|pm me|text me|message me|hmu"
    r"|venmo|cash ?app|zelle|paypal|apple pay)\b"
)
PRICE = re.compile(r"\$\s?\d|\b\d+\s?(?:dollars|bucks)\b", re.IGNORECASE)


def normalize(text):
    text = unicodedata.normalize("NFKC", text)
    text = ZERO_WIDTH.sub("", text).translate(LOOKALIKES).lower()
    text = SPACED_OUT.sub(lambda m: re.sub(r"[\W_]", "", m.group()), text)
    # Only swap leetspeak that runs into a letter ("se11ing", "t1x"), so prices
    # like "$40" and punctuation like "tickets!!" are left alone.
    return LEET_RUN.sub(lambda m: m.group().translate(LEET), text)


def should_ban(text):
    if not text:
        return False
    clean = normalize(text)
    if SELLING.search(clean):
        return True
    mentions_tickets = bool(TICKET.search(clean) or TICKET_EMOJI.search(text))
    return mentions_tickets and bool(INTENT.search(clean) or PRICE.search(text))


# --- ban list ---------------------------------------------------------------

def load_banned():
    banned = {u.strip() for u in os.environ.get("BANNED_USER_IDS", "").split(",") if u.strip()}
    try:
        with open(BAN_FILE) as f:
            banned.update(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return banned


def add_banned(user_id):
    with _ban_lock:
        banned = load_banned()
        banned.add(user_id)
        with open(BAN_FILE, "w") as f:
            json.dump(sorted(banned), f)


# --- GroupMe API ------------------------------------------------------------

def bot_say(text):
    if DRY_RUN:
        text = f"[dry run] {text}"
    requests.post(f"{API}/bots/post", json={"bot_id": GROUPME_BOT_ID, "text": text}, timeout=10)


def announce_removal():
    """Tell the chat someone was removed, without flooding it during a spam wave.

    Never echoes the removed member's name: spam accounts put links and phone
    numbers in their names.
    """
    global _last_announce, _removed_since_announce
    with _announce_lock:
        _removed_since_announce += 1
        now = time.monotonic()
        if _last_announce and now - _last_announce < ANNOUNCE_COOLDOWN:
            return
        count, _removed_since_announce, _last_announce = _removed_since_announce, 0, now
    who = "1 member" if count == 1 else f"{count} members"
    bot_say(f"Removed {who} for posting about buying/selling tickets, which isn't allowed here.")


def find_member(group_id, user_id):
    resp = requests.get(f"{API}/groups/{group_id}", params={"token": GROUPME_TOKEN}, timeout=10)
    resp.raise_for_status()
    members = resp.json()["response"]["members"]
    return next((m for m in members if m["user_id"] == user_id), None)


def is_admin(member):
    roles = member.get("roles", [])
    return "admin" in roles or "owner" in roles


def remove_member(group_id, membership_id):
    if DRY_RUN:
        return
    # The remove endpoint takes the membership id, not the user_id.
    resp = requests.post(
        f"{API}/groups/{group_id}/members/{membership_id}/remove",
        params={"token": GROUPME_TOKEN},
        timeout=10,
    )
    resp.raise_for_status()


def delete_message(group_id, message_id):
    """Best effort: this endpoint is undocumented and may stop working."""
    if DRY_RUN:
        return
    try:
        requests.delete(
            f"{API}/conversations/{group_id}/messages/{message_id}",
            params={"token": GROUPME_TOKEN},
            timeout=10,
        )
    except requests.RequestException:
        log.warning("could not delete message %s", message_id)


# --- handlers ---------------------------------------------------------------

def ban(group_id, user_id, message_id=None):
    if user_id in EXEMPT_USER_IDS:
        log.info("not banning exempt user %s", user_id)
        return False
    member = find_member(group_id, user_id)
    if member is not None and is_admin(member):
        log.info("not banning admin %s", user_id)
        return False

    # Delete even if they're already gone: spam bots send several messages
    # at once, and the later ones arrive after the first removed them.
    if message_id:
        delete_message(group_id, message_id)
    add_banned(user_id)
    if member is None:
        log.info("user %s is no longer in the group", user_id)
        return False

    remove_member(group_id, member["id"])
    log.info("banned %s", user_id)
    return True


def joined_user_ids(msg):
    """Pull the user ids out of a 'joined'/'added' system message."""
    event = msg.get("event") or {}
    data = event.get("data") or {}
    kind = event.get("type", "")
    if kind in ("membership.announce.joined", "membership.announce.rejoined"):
        user = data.get("user") or {}
        return [str(user["id"])] if "id" in user else []
    if kind == "membership.announce.added":
        return [str(u["id"]) for u in data.get("added_users", []) if "id" in u]
    return []


def handle_message(msg):
    group_id = msg.get("group_id")
    if GROUP_ID and group_id != GROUP_ID:
        return

    if msg.get("sender_type") == "system":
        banned = load_banned()
        for user_id in joined_user_ids(msg):
            if user_id in banned and ban(group_id, user_id):
                announce_removal()
        return

    if msg.get("sender_type") != "user":
        return

    if should_ban(msg.get("text")):
        log.info("flagged message from %s: %r", msg.get("user_id"), (msg.get("text") or "")[:200])
        if ban(group_id, msg["user_id"], msg.get("id")):
            announce_removal()


@app.post("/callback")
def callback():
    if CALLBACK_SECRET and request.args.get("secret") != CALLBACK_SECRET:
        abort(403)
    msg = request.get_json(silent=True) or {}
    try:
        handle_message(msg)
    except Exception:
        log.exception("failed to handle message")
    # Always 200 so GroupMe doesn't retry.
    return "", 200


@app.get("/")
def health():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
