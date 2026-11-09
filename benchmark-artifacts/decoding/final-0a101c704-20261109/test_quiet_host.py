import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import quiet_host


class RestoreTests(unittest.TestCase):
    def test_restore_continues_after_one_process_error(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            item = {"started": "original", "command": "/test/fff-mcp"}
            state.write_text(json.dumps({"processes": [
                {"pid": 11, **item}, {"pid": 12, **item},
            ]}))
            with patch.object(quiet_host, "processes", return_value={11: item, 12: item}), \
                    patch.object(quiet_host.os, "kill", side_effect=[PermissionError("test"), None]):
                quiet_host.restore(state)
            result = json.loads(state.read_text())
            self.assertEqual(result["restored_pids"], [12])
            self.assertEqual(result["restore_errors"][0]["pid"], 11)

    def test_only_restores_matching_process_identities(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            state.write_text(json.dumps({"processes": [
                {"pid": 11, "started": "original", "command": "/test/fff-mcp"},
                {"pid": 12, "started": "old", "command": "/test/fff-mcp"},
                {"pid": 13, "started": "gone", "command": "/test/fff-mcp"},
                {"pid": 14, "started": "original", "command": "/test/fff-mcp"},
            ]}))
            live = {
                11: {"started": "original", "command": "/test/fff-mcp"},
                12: {"started": "replacement", "command": "/test/fff-mcp"},
                14: {"started": "original", "command": "/different/process"},
            }
            with patch.object(quiet_host, "processes", return_value=live), \
                    patch.object(quiet_host.os, "kill") as kill:
                quiet_host.restore(state)
                kill.assert_called_once_with(11, quiet_host.signal.SIGCONT)
            self.assertEqual(json.loads(state.read_text())["restored_pids"], [11])


if __name__ == "__main__":
    unittest.main()
