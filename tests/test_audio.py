import numpy as np
import pytest

from minutes import audio


def test_wav_round_trip(tmp_path):
    t = np.linspace(0, 1, audio.SAMPLE_RATE, endpoint=False)
    tone = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    path = tmp_path / "tone.wav"
    audio.write_wav(tone, path)
    back = audio.load_audio(path)
    assert back.dtype == np.float32
    assert abs(len(back) - len(tone)) < 100
    assert np.max(np.abs(back - tone[: len(back)])) < 0.01


def test_not_media_gives_friendly_error(tmp_path):
    bad = tmp_path / "upload-1234.mp4"
    bad.write_text("this is not a video")
    with pytest.raises(audio.AudioError) as e:
        audio.load_audio(bad, "Team call.mp4")
    msg = str(e.value)
    assert "Team call.mp4" in msg and "couldn't be read" in msg
    assert "upload-1234" not in msg and "Errno" not in msg  # no internal paths/codes


def test_video_without_audio_track(tmp_path):
    import av

    path = tmp_path / "silent-video.mp4"
    with av.open(str(path), "w") as out:
        stream = out.add_stream("mpeg4", rate=10)
        stream.width = stream.height = 64
        stream.pix_fmt = "yuv420p"
        for _ in range(5):
            frame = av.VideoFrame.from_ndarray(np.zeros((64, 64, 3), np.uint8), format="rgb24")
            for packet in stream.encode(frame):
                out.mux(packet)
        for packet in stream.encode():
            out.mux(packet)
    with pytest.raises(audio.AudioError, match="has no audio track"):
        audio.load_audio(path, "screen-recording.mp4")


def test_missing_file(tmp_path):
    with pytest.raises(audio.AudioError, match="could not be found"):
        audio.load_audio(tmp_path / "gone.mp4", "gone.mp4")
