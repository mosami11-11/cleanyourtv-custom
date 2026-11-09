"""Where the #577 field report went: the Fire OS limits bullet and the TVision Hub note.

The report covers six devices in one session, and most of it was already documented (the onn 4K Pro
setupwraith handover, Fire OS 6's protected packages). Two things were not: that some firmware
refuses every route to disabling a package, and the one device with a working list and no note.
These tests pin both, plus the pointers that make them findable, and that the note is not a tested
list it has no evidence to be.

Run from the repository root: python3 -m unittest discover -s tests -v
"""
import re
from pathlib import Path
import unittest

from readme_profile import skip_standard_readme_test

ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "docs" / "devices" / "tvision-hub.md"
TROUBLE = ROOT / "docs" / "TROUBLESHOOTING.md"
README = ROOT / "README.md"
EXAMPLES_README = ROOT / "examples" / "README.md"
PROMPT = ROOT / "PROMPT.md"
FIRE_STICK = ROOT / "examples" / "amazon-fire-tv-stick-4k-2018" / "debloat.txt"
ISSUE = "https://github.com/Gathin23/cleanyourtv/issues/577"

PACKAGES = [
    "com.nes.tvbugtracker",
    "com.nes.tv.bugreportsender",
    "com.google.android.tvrecommendations",
    "com.sei.hitv.explore",
    "com.google.android.videos",
    "com.android.camera2",
    "com.google.android.play.games",
]

LINK = re.compile(r"\]\(([^)\s]+)\)")


def flat(text):
    """Prose wrapped across lines, so match on a single line of it."""
    return re.sub(r"[ \t]*\n[ \t]*", " ", text)


def section(text, heading):
    """The body of the top-level markdown section `## heading`, up to the next `## `."""
    lines = text.split("\n")
    start = next(i for i, line in enumerate(lines) if line.strip() == "## " + heading)
    out = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        out.append(line)
    return "\n".join(out)


def bullet(text, start):
    """The markdown bullet that begins with `start`, up to the next top-level bullet."""
    lines = text.split("\n")
    first = next(i for i, line in enumerate(lines) if line.startswith(start))
    out = [lines[first]]
    for line in lines[first + 1:]:
        if line.startswith("- **") or line.startswith("## "):
            break
        out.append(line)
    return "\n".join(out)


def broken_links(path):
    return [
        target for target in LINK.findall(path.read_text(encoding="utf-8"))
        if not target.startswith(("http://", "https://", "mailto:", "#"))
        and target.split("#", 1)[0]
        and not (path.parent / target.split("#", 1)[0]).exists()
    ]


class TvisionHubNoteTest(unittest.TestCase):
    def test_note_exists_and_identifies_the_device(self):
        text = NOTE.read_text(encoding="utf-8")
        self.assertIn("SEI Robotics", text)
        self.assertIn("S905X2", text)
        self.assertIn("T-Mobile", text)
        self.assertIn("Google TV", text)

    def test_note_does_not_invent_a_fingerprint(self):
        """The report carried no build fingerprint, so the note must not pretend to have one."""
        text = NOTE.read_text(encoding="utf-8")
        self.assertIn("not recorded", text)
        self.assertNotRegex(text, r"ro\.build\.fingerprint\s*\|")

    def test_every_disabled_package_is_recorded(self):
        text = NOTE.read_text(encoding="utf-8")
        for package in PACKAGES:
            self.assertIn("`%s`" % package, text)

    def test_note_says_it_is_not_a_tested_list(self):
        text = NOTE.read_text(encoding="utf-8")
        self.assertIn("CONTRIBUTING", text)
        self.assertIn("one session", text.lower())
        self.assertFalse(
            (ROOT / "examples" / "tvision-hub").exists(),
            "an examples/ list would claim several days of use the report does not have",
        )

    def test_home_was_confirmed_and_the_stock_package_was_not_recorded(self):
        text = NOTE.read_text(encoding="utf-8")
        body = section(text, "Home")
        self.assertIn("confirmed as Home", body)
        self.assertIn("mFocusedApp", body)
        self.assertIn("does not name the stock Home package", flat(text))

    def test_both_connection_quirks_are_kept(self):
        text = NOTE.read_text(encoding="utf-8")
        body = section(text, "Two connection quirks")
        self.assertIn("until the hub was restarted", body)
        self.assertIn("adb disconnect", body)

    def test_note_links_resolve(self):
        self.assertEqual(broken_links(NOTE), [])

    def test_note_links_the_issue_it_transcribes(self):
        self.assertIn(ISSUE, NOTE.read_text(encoding="utf-8"))


class FireOsLimitTest(unittest.TestCase):
    def setUp(self):
        self.text = TROUBLE.read_text(encoding="utf-8")

    def test_bullet_lives_under_working_on_the_tv(self):
        body = section(self.text, "Working on the TV")
        self.assertIn("Every way of disabling a package is refused", body)

    def test_bullet_names_all_three_refusals(self):
        body = bullet(self.text, "- **Every way of disabling a package is refused**")
        self.assertIn("SecurityException", body)
        self.assertIn("DELETE_FAILED_INTERNAL_ERROR", body)
        self.assertIn("`pm hide`", body)
        self.assertIn("pm list packages -d", body)

    def test_bullet_says_pm_hide_is_the_one_that_lies(self):
        body = bullet(self.text, "- **Every way of disabling a package is refused**")
        self.assertIn("lies", body)

    def test_bullet_contrasts_fire_os_6_and_links_its_list(self):
        body = bullet(self.text, "- **Every way of disabling a package is refused**")
        self.assertIn("Fire OS 6", body)
        self.assertIn("examples/amazon-fire-tv-stick-4k-2018/debloat.txt", body)
        self.assertTrue(FIRE_STICK.is_file())

    def test_bullet_gives_the_dns_fallback_and_the_issue(self):
        body = bullet(self.text, "- **Every way of disabling a package is refused**")
        self.assertIn("DNS", body)
        self.assertIn(ISSUE, body)

    def test_bullet_does_not_promise_a_workaround(self):
        body = bullet(self.text, "- **Every way of disabling a package is refused**")
        self.assertNotIn("root the", body)
        self.assertIn("does not take a debloat list at all", body)


class PointersTest(unittest.TestCase):
    def test_readme_no_longer_promises_a_fire_tv_debloat(self):
        skip_standard_readme_test(self)
        text = flat(README.read_text(encoding="utf-8"))
        self.assertIn("on the 2015 Fire TV Box (Fire OS 5) even that half fails", text)
        self.assertIn("every `pm` route is refused", text)

    def test_examples_readme_lists_the_note(self):
        text = EXAMPLES_README.read_text(encoding="utf-8")
        self.assertIn("docs/devices/tvision-hub.md", text)
        self.assertIn("one-session", text)

    def test_prompt_tells_the_assistant_to_stop_retrying(self):
        text = PROMPT.read_text(encoding="utf-8")
        self.assertIn("refused for every package", text)
        self.assertIn("pm list packages -d", text)
        self.assertIn("docs/TROUBLESHOOTING.md", text)


if __name__ == "__main__":
    unittest.main()
