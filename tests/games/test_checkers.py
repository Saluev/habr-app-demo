import pytest

from backend.games.checkers import Checkers
from tests.games.stub_connector import StubConnector


@pytest.mark.asyncio
async def test_checkers():
    alice, bob = "alice", "bob"
    connector = StubConnector()
    connector.actions[alice].append({"kind": "turn", "i": 0, "j": 0})
    connector.actions[bob].append({"kind": "turn", "i": 1, "j": 1})
    connector.actions[alice].append({"kind": "turn", "i": 0, "j": 1})
    connector.actions[bob].append({"kind": "turn", "i": 2, "j": 2})
    connector.actions[alice].append({"kind": "turn", "i": 0, "j": 2})
    await Checkers().play([alice, bob], connector)
    assert connector.events[alice][-1]["winner"] == alice
    assert connector.events[bob][-1]["winner"] == alice
