import pytest

from minutes import export


@pytest.mark.parametrize("raw,expected", [
    ("Budget Review", "Budget Review"),
    ('Bad:/\\*?"<>| name.', "Bad name"),
    ("  lots   of   space  ", "lots of space"),
    ("", "Meeting"),
    ("...", "Meeting"),
    ("CON", "CON_"),
    ("con", "con_"),
    ("nul.txt", "nul.txt_"),
    ("COM1", "COM1_"),
    ("LPT9", "LPT9_"),
    ("Console", "Console"),
    ("COM10", "COM10"),
    ("Café ✓ Review", "Café ✓ Review"),
])
def test_clean_name(raw, expected):
    assert export.clean_name(raw) == expected


def test_clean_name_caps_length_without_trailing_space_or_dot():
    name = export.clean_name("a" * 99 + " b")
    assert len(name) <= 100 and not name.endswith((" ", "."))
    name = export.clean_name("a" * 99 + ".b")
    assert not name.endswith(".")


def test_reserved_name_folder_is_usable(tmp_path, meeting):
    m = export.write_meeting({**meeting, "name": "CON"}, tmp_path)
    assert m["name"] == "CON_"
    assert all((tmp_path / "CON_" / f).exists() for f in m["files"])


@pytest.mark.parametrize("title,expected", [
    ("Q4 Budget Review", "Q4-Budget-Review"),
    ("EcoRouter partnership intro", "EcoRouter-Partnership-Intro"),
    ("", ""),
])
def test_slug_title(title, expected):
    assert export.slug_title(title) == expected


def test_default_name_falls_back_to_file_name():
    assert export.default_name("2026-10-14", "", "Zoom-Call") == "2026-10-14_Zoom-Call"
