"""The legacy check-in must not report success without a verified receipt."""

import contextlib
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import checkin  # noqa: E402


class CheckinTests(unittest.TestCase):
    def test_success_only_after_post_and_verify(self):
        output = io.StringIO()
        verified = {"room": "lobby", "seq": 123, "verified": True}
        with (mock.patch("checkin.load_pem_private_key", return_value=object()),
              mock.patch("pathlib.Path.read_bytes", return_value=b"test-key"),
              mock.patch("checkin.post_and_verify", return_value=verified) as post,
              contextlib.redirect_stdout(output)):
            self.assertEqual(checkin.main(), 0)
        self.assertEqual(json.loads(output.getvalue()), verified)
        self.assertEqual(post.call_args.args[0], "lobby")

    def test_failed_verification_exits_nonzero(self):
        error = io.StringIO()
        with (mock.patch("checkin.load_pem_private_key", return_value=object()),
              mock.patch("pathlib.Path.read_bytes", return_value=b"test-key"),
              mock.patch("checkin.post_and_verify", side_effect=RuntimeError("readback unavailable")) as post,
              contextlib.redirect_stderr(error)):
            self.assertEqual(checkin.main(), 1)
        self.assertIn("not verified", error.getvalue())
        self.assertEqual(post.call_count, 1)


if __name__ == "__main__":
    unittest.main()
