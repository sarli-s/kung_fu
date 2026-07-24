"""Unit tests for LobbyManager (stage 3)."""

from server.game.lobby import LobbyManager


def test_first_player_gets_white():
    lobby = LobbyManager()
    ok, _, color = lobby.join("default", "ws1", "alice")
    assert ok and color == "w"


def test_second_player_gets_black():
    lobby = LobbyManager()
    lobby.join("default", "ws1", "alice")
    ok, _, color = lobby.join("default", "ws2", "bob")
    assert ok and color == "b"


def test_third_player_rejected():
    lobby = LobbyManager()
    lobby.join("default", "ws1", "alice")
    lobby.join("default", "ws2", "bob")
    ok, reason, color = lobby.join("default", "ws3", "charlie")
    assert not ok and color is None and "full" in reason.lower()


def test_leave_frees_slot():
    lobby = LobbyManager()
    lobby.join("default", "ws1", "alice")
    lobby.join("default", "ws2", "bob")
    lobby.leave("default", "ws1")  # bob remains as only player
    ok, _, color = lobby.join("default", "ws3", "charlie")
    assert ok and color == "b"  # charlie is 2nd (bob is still in room)


def test_get_color_returns_assigned_color():
    lobby = LobbyManager()
    lobby.join("default", "ws1", "alice")
    assert lobby.get_color("default", "ws1") == "w"


def test_get_color_unknown_player_returns_none():
    lobby = LobbyManager()
    assert lobby.get_color("default", "nobody") is None


def test_player_count():
    lobby = LobbyManager()
    assert lobby.player_count("default") == 0
    lobby.join("default", "ws1", "alice")
    assert lobby.player_count("default") == 1
