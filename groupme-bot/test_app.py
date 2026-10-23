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


def post(msg, secret="s3cret"):
    return bot.app.test_client().post(f"/callback?secret={secret}", json=msg)


def user_msg(text, user_id="u1"):
    return {"group_id": "g1", "sender_type": "user", "user_id": user_id,
            "name": "Seller", "id": "msg1", "text": text}


@pytest.mark.parametrize("text", ["Selling 2 tix", "anyone SELLING?", "selling."])
def test_should_ban(text):
    assert bot.should_ban(text)


@pytest.mark.parametrize("text", ["sell me", "bestselling book", "", None, "buying tickets"])
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


def test_dry_run_does_not_remove(calls, monkeypatch):
    monkeypatch.setattr(bot, "DRY_RUN", True)
    post(user_msg("selling"))
    assert not any("/remove" in c[1] or c[0] == "delete" for c in calls)
    assert calls[-1][2]["text"].startswith("[dry run]")
