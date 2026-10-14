from minutes.diarize import assign_speakers


def seg(start, end, *words):
    return {"start": start, "end": end, "text": " ".join(w[2] for w in words),
            "words": [{"start": s, "end": e, "word": " " + t} for s, e, t in words]}


def test_no_turns_means_no_speakers():
    out = assign_speakers([seg(0, 1, (0, 1, "hi"))], [])
    assert out[0]["speaker"] is None


def test_segment_split_at_speaker_change():
    segments = [seg(0, 4, (0, 1, "Hello"), (1, 2, "there."), (2.5, 3, "Hi"), (3, 4, "back."))]
    turns = [(0.0, 2.2, "SPEAKER_07"), (2.2, 5.0, "SPEAKER_03")]
    out = assign_speakers(segments, turns)
    assert [(o["speaker"], o["text"]) for o in out] == [("Speaker 1", "Hello there."), ("Speaker 2", "Hi back.")]
    assert out[1]["start"] == 2.5 and out[1]["end"] == 4


def test_labels_numbered_by_first_appearance():
    segments = [seg(0, 1, (0, 1, "a")), seg(2, 3, (2, 3, "b")), seg(4, 5, (4, 5, "c"))]
    turns = [(0, 1.5, "SPEAKER_05"), (1.5, 3.5, "SPEAKER_00"), (3.5, 6, "SPEAKER_05")]
    assert [o["speaker"] for o in assign_speakers(segments, turns)] == ["Speaker 1", "Speaker 2", "Speaker 1"]


def test_word_in_gap_takes_nearest_turn():
    segments = [seg(10, 11, (10, 11, "late"))]
    turns = [(0, 2, "A"), (12, 14, "B")]
    assert assign_speakers(segments, turns)[0]["speaker"] == "Speaker 1"  # B is nearest, first seen


def test_overlapping_turns_pick_largest_overlap():
    segments = [seg(0, 4, (1, 3, "word"))]
    turns = [(0, 1.5, "A"), (1.2, 4, "B")]
    assert assign_speakers(segments, turns)[0]["speaker"] == "Speaker 1"
    assert {o["speaker"] for o in assign_speakers(segments, turns)} == {"Speaker 1"}


def test_segment_without_words_uses_segment_span():
    segments = [{"start": 5, "end": 6, "text": "no words", "words": []}]
    out = assign_speakers(segments, [(4, 7, "X")])
    assert out[0]["speaker"] == "Speaker 1" and out[0]["text"] == "no words"
