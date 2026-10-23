import pytest

import app as bot


class FakeResponse:
    def __init__(self, data=None):
        self._data = data or {}

    def json(self):
        return self._data

    def raise_for_status(self):
        pass


MEMBERS = [
    {"id": "m1", "user_id": "u1", "roles": ["user"]},
    {"id": "m2", "user_id": "u2", "roles": ["admin"]},
]


@pytest.fixture
def calls(monkeypatch, tmp_path):
    log = []
    monkeypatch.setattr(bot, "BAN_FILE", str(tmp_path / "banned.json"))
    monkeypatch.setattr(bot, "GROUP_ID", "g1")
    monkeypatch.setattr(bot, "CALLBACK_SECRET", "s3cret")
    monkeypatch.setattr(bot, "DRY_RUN", False)
    monkeypatch.setattr(bot.requests, "get",
                        lambda url, **kw: FakeResponse({"response": {"members": MEMBERS}}))
    monkeypatch.setattr(bot.requests, "post",
                        lambda url, **kw: log.append(("post", url, kw.get("json"))) or FakeResponse())
    monkeypatch.setattr(bot.requests, "delete",
                        lambda url, **kw: log.append(("delete", url, None)) or FakeResponse())
    return log


@pytest.fixture(autouse=True)
def reset_announce(monkeypatch):
    monkeypatch.setattr(bot, "_last_announce", 0.0)
    monkeypatch.setattr(bot, "_removed_since_announce", 0)
    monkeypatch.setattr(bot, "EXEMPT_USER_IDS", set())
    monkeypatch.setattr(bot, "ANNOUNCE", True)


def bot_posts(calls):
    return [c[2]["text"] for c in calls if c[1].endswith("/bots/post")]


def post(msg, secret="s3cret"):
    return bot.app.test_client().post(f"/callback?secret={secret}", json=msg)


def user_msg(text, user_id="u1"):
    return {"group_id": "g1", "sender_type": "user", "user_id": user_id,
            "name": "Seller", "id": "msg1", "text": text}


@pytest.mark.parametrize("text", [
    "Selling 2 tix", "anyone SELLING?", "selling.",
    # disguised spellings spam bots use
    "\U0001d412\U0001d41e\U0001d425\U0001d425\U0001d422\U0001d427\U0001d420",  # bold "Selling"
    "\u0455\u0435ll\u0456ng",  # Cyrillic look-alikes
    "sel\u200bling", "s e l l i n g", "S.E.L.L.I.N.G", "se11ing", "$elling", "sellin cheap",
    # ticket + sale/giveaway call to action
    "Giving away 4 free tickets to the concert DM me",
    "\U0001f39f\ufe0f tix available, venmo me",
    "2 tickets $40 each", "T1CKETS for sale", "tickets!! hmu",
    "ISO 2 tickets, will pay", "WTB ticket", "t i c k e t s dm me",
])
def test_should_ban(text):
    assert bot.should_ban(text)


@pytest.mark.parametrize("text", [
    "", None, "see you at the meeting", "bestselling book", "sell me on this idea",
    "where do I buy tickets for the hackathon?", "do I need a ticket for tonight?",
    "I lost my ticket lol", "the event is free", "DM me about the project",
    "Selin is presenting today", "I scored 100 on the exam!!", "@everyone meeting at 7",
])
def test_should_not_ban(text):
    assert not bot.should_ban(text)


def test_bans_user_who_says_selling(calls):
    assert post(user_msg("selling 2 OSU tickets")).status_code == 200
    urls = [c[1] for c in calls]
    assert any(u.endswith("/conversations/g1/messages/msg1") for u in urls)
    assert any(u.endswith("/groups/g1/members/m1/remove") for u in urls)
    assert "u1" in bot.load_banned()


def test_ignores_normal_messages(calls):
    post(user_msg("see you at the meeting"))
    assert calls == []


def test_never_bans_admins(calls):
    post(user_msg("selling stickers", user_id="u2"))
    assert calls == []
    assert "u2" not in bot.load_banned()


def test_never_bans_exempt_users(calls, monkeypatch):
    monkeypatch.setattr(bot, "EXEMPT_USER_IDS", {"u1"})
    post(user_msg("selling club merch"))
    assert calls == []


def test_deletes_followup_spam_after_removal(calls, monkeypatch):
    # The member is already gone (removed by their first message).
    monkeypatch.setattr(bot.requests, "get",
                        lambda url, **kw: FakeResponse({"response": {"members": []}}))
    post(user_msg("selling tix again"))
    assert any(c[0] == "delete" for c in calls)
    assert not any("/remove" in c[1] for c in calls)


def test_spam_wave_posts_one_notice_without_names(calls):
    for _ in range(5):
        post(user_msg("selling tix"))
    notices = bot_posts(calls)
    assert len(notices) == 1
    assert "Seller" not in notices[0]


def test_rejects_bad_secret(calls):
    assert post(user_msg("selling"), secret="nope").status_code == 403
    assert calls == []


def test_ignores_other_groups(calls):
    msg = user_msg("selling")
    msg["group_id"] = "other"
    post(msg)
    assert calls == []


def test_removes_banned_user_on_rejoin(calls):
    bot.add_banned("u1")
    post({"group_id": "g1", "sender_type": "system", "text": "Seller rejoined the group",
          "event": {"type": "membership.announce.rejoined", "data": {"user": {"id": 1}}}})
    assert calls == []  # id 1 != "u1"
    post({"group_id": "g1", "sender_type": "system", "text": "Seller joined the group",
          "event": {"type": "membership.announce.joined", "data": {"user": {"id": "u1"}}}})
    assert any(c[1].endswith("/members/m1/remove") for c in calls)


def test_dry_run_only_logs(calls, monkeypatch):
    monkeypatch.setattr(bot, "DRY_RUN", True)
    post(user_msg("selling"))
    assert not any("/remove" in c[1] or c[0] == "delete" for c in calls)
    assert bot_posts(calls) == []
    assert "u1" not in bot.load_banned()


def test_no_chat_notice_unless_announce_enabled(calls, monkeypatch):
    monkeypatch.setattr(bot, "ANNOUNCE", False)
    post(user_msg("selling tix"))
    assert any("/remove" in c[1] for c in calls)
    assert bot_posts(calls) == []
