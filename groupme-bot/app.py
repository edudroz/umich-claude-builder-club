"""GroupMe bot that bans anyone who posts the word "selling".

GroupMe POSTs every message in the group to /callback. If a member's message
contains "selling", we delete it, remove the member, and remember their
user_id so they get removed again if they rejoin.

Bots can't remove members, so removals use a group owner/admin's access token.
"""

import json
import logging
import os
import re
import threading

import requests
from flask import Flask, abort, request

API = "https://api.groupme.com/v3"

GROUPME_TOKEN = os.environ.get("GROUPME_TOKEN", "")
GROUPME_BOT_ID = os.environ.get("GROUPME_BOT_ID", "")
GROUP_ID = os.environ.get("GROUP_ID", "")
CALLBACK_SECRET = os.environ.get("CALLBACK_SECRET", "")
BAN_FILE = os.environ.get("BAN_FILE", "banned.json")
DRY_RUN = os.environ.get("DRY_RUN", "0") == "1"

BANNED_PATTERN = re.compile(r"\bselling\b", re.IGNORECASE)

log = logging.getLogger("groupme-bot")
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
_ban_lock = threading.Lock()


def should_ban(text):
    return bool(text and BANNED_PATTERN.search(text))


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

def ban(group_id, user_id, name, message_id=None):
    member = find_member(group_id, user_id)
    if member is None:
        log.info("user %s is no longer in the group", user_id)
        add_banned(user_id)
        return False
    if is_admin(member):
        log.info("not banning admin %s", name)
        return False

    if message_id:
        delete_message(group_id, message_id)
    remove_member(group_id, member["id"])
    add_banned(user_id)
    log.info("banned %s (%s)", name, user_id)
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
            if user_id in banned and ban(group_id, user_id, user_id):
                bot_say("A banned member tried to rejoin and was removed.")
        return

    if msg.get("sender_type") != "user":
        return

    if should_ban(msg.get("text")):
        if ban(group_id, msg["user_id"], msg.get("name", ""), msg.get("id")):
            bot_say(f"Removed {msg.get('name', 'a member')}. Selling isn't allowed in this group.")


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
