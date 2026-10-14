from minutes import export


def test_srt_timestamps_and_speakers(meeting):
    srt = export.render_srt(meeting)
    blocks = srt.strip().split("\n\n")
    assert len(blocks) == 3
    assert blocks[0].split("\n") == ["1", "00:00:00,000 --> 00:00:04,200", "Speaker 1: Let's start with the budget."]
    assert export._srt_time(3725.5) == "01:02:05,500"


def test_txt_groups_consecutive_speaker_lines(meeting):
    txt = export.render_txt(meeting)
    assert txt.count("Speaker 1:") == 1 and txt.count("Speaker 2:") == 1
    assert "[00:09] Speaker 2:" in txt


def test_txt_without_speakers(meeting):
    for s in meeting["segments"]:
        s["speaker"] = None
    txt = export.render_txt(meeting)
    assert "None" not in txt and "[00:00]" in txt


def test_summary_markdown_sections(meeting):
    md = export.render_summary_md(meeting)
    for heading in ("# Budget Review", "## Overview", "## Decisions", "## Action items", "## Topics"):
        assert heading in md
    assert "## Open questions" not in md  # empty sections are omitted
    assert "- [ ] Send the report (**Speaker 2** — due Friday)" in md


def test_summary_markdown_without_summary(meeting):
    meeting["summary"] = None
    assert "_No summary was generated._" in export.render_summary_md(meeting)


def test_replace_names_whole_words_only():
    data = {"overview": "Speaker 1 met Speaker 10 and Speaker 1.", "topics": [{"start": 1.0, "topic": "Speaker 1 intro"}]}
    out = export.replace_names(data, {"Speaker 1": "Priya"})
    assert out["overview"] == "Priya met Speaker 10 and Priya."
    assert out["topics"] == [{"start": 1.0, "topic": "Priya intro"}]


def test_replace_names_swap_is_simultaneous_safe():
    # Longest-first replacement means "Speaker 1" doesn't clobber "Speaker 12".
    out = export.replace_names("Speaker 12 thanked Speaker 1", {"Speaker 1": "Ann", "Speaker 12": "Bo"})
    assert out == "Bo thanked Ann"
