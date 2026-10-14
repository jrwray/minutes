"""CPU/GPU choice: detection, the settings flag, and falling back to the CPU."""

import numpy as np
import pytest

from minutes import config, device, transcribe


@pytest.fixture
def gpu(monkeypatch):
    """Pretend the machine has (or lacks) a usable NVIDIA GPU."""
    state = {"available": False, "detected": False, "name": None, "reason": "No NVIDIA GPU detected."}
    monkeypatch.setattr(device, "gpu_info", lambda: state)
    return state


def make_gpu_usable(state):
    state.update(available=True, detected=True, name="NVIDIA RTX 4070", reason=None)


class FakeSegment:
    def __init__(self, start, end, text):
        self.start, self.end, self.text, self.words = start, end, text, []


class FakeWhisper:
    """Records how it was built; can fail on CUDA at load or on first decode."""
    built = []
    fail_cuda = None  # None | "load" | "decode"

    def __init__(self, name, device, compute_type, cpu_threads):
        FakeWhisper.built.append((device, compute_type))
        if device == "cuda" and FakeWhisper.fail_cuda == "load":
            raise RuntimeError("CUDA driver version is insufficient")
        self.device = device

    def transcribe(self, audio, **kwargs):
        info = type("Info", (), {"language": "en", "language_probability": 0.9})()

        def segments():
            if self.device == "cuda" and FakeWhisper.fail_cuda == "decode":
                raise RuntimeError("Library cublas64_12.dll is not found or cannot be loaded")
            yield FakeSegment(0.0, 1.0, "Hello there.")
        return segments(), info


@pytest.fixture
def whisper(monkeypatch):
    import faster_whisper

    FakeWhisper.built, FakeWhisper.fail_cuda = [], None
    monkeypatch.setattr(faster_whisper, "WhisperModel", FakeWhisper)
    monkeypatch.setattr(transcribe, "_model", None)
    monkeypatch.setattr(transcribe, "_model_key", None)
    return FakeWhisper


def run(setting):
    settings = {**config.DEFAULTS, "device": setting}
    return transcribe.transcribe(np.zeros(16000, "float32"), settings, lambda *a: None, lambda: False)


def test_device_is_unset_until_chosen(isolated):
    assert config.load()["device"] == ""


@pytest.mark.parametrize("setting", ["", "cpu", "gpu"])
def test_resolve_without_gpu_is_always_cpu(gpu, setting):
    assert device.resolve(setting) == "cpu"


def test_resolve_with_gpu(gpu):
    make_gpu_usable(gpu)
    assert device.resolve("gpu") == "cuda"
    assert device.resolve("cpu") == "cpu"
    assert device.resolve("") == "cpu"


def test_cpu_uses_int8(gpu, whisper):
    r = run("cpu")
    assert whisper.built == [("cpu", "int8")]
    assert r["device"] == "cpu" and r["gpu_fallback"] is None
    assert r["segments"][0]["text"] == "Hello there."


def test_gpu_uses_float16(gpu, whisper):
    make_gpu_usable(gpu)
    r = run("gpu")
    assert whisper.built == [("cuda", "float16")]
    assert r["device"] == "cuda" and r["gpu_fallback"] is None


def test_gpu_chosen_but_missing_falls_back_with_reason(gpu, whisper):
    r = run("gpu")
    assert whisper.built == [("cpu", "int8")]
    assert r["device"] == "cpu" and r["gpu_fallback"] == "No NVIDIA GPU detected."


@pytest.mark.parametrize("failure", ["load", "decode"])
def test_gpu_failure_falls_back_to_cpu(gpu, whisper, failure):
    make_gpu_usable(gpu)
    whisper.fail_cuda = failure
    r = run("gpu")
    assert whisper.built[-1] == ("cpu", "int8")
    assert r["device"] == "cpu" and r["segments"][0]["text"] == "Hello there."
    assert r["gpu_fallback"].startswith("GPU failed to start")


def test_status_reports_devices(client, gpu):
    d = client.get("/api/status").json()["device"]
    assert d["setting"] == "" and d["active"] == "cpu"
    assert d["gpu"]["reason"] == "No NVIDIA GPU detected." and d["cpu"]


def test_status_reflects_choice(client, gpu):
    make_gpu_usable(gpu)
    client.post("/api/settings", json={"device": "gpu"})
    d = client.get("/api/status").json()["device"]
    assert d["setting"] == "gpu" and d["active"] == "cuda"


def test_job_warns_and_records_device(api, gpu, monkeypatch):
    # Real transcribe() fallback logic with the fake engine underneath.
    monkeypatch.setattr(transcribe, "transcribe", lambda audio, settings, p, c: {
        **api.fakes.transcribe(audio, settings, p, c), "device": "cpu", "gpu_fallback": "No NVIDIA GPU detected."})
    api.post("/api/settings", json={"device": "gpu"})
    job = api.wait(api.upload()["id"])
    assert "Used the CPU instead of the GPU: No NVIDIA GPU detected." in job["warnings"]
    assert api.get(f"/api/meetings/{job['meeting_id']}").json()["device"] == "cpu"


def test_detection_on_this_machine_does_not_crash():
    device.gpu_info.cache_clear()
    info = device.gpu_info()
    assert set(info) == {"available", "detected", "name", "reason"}
    assert isinstance(device.cpu_name(), str) and device.cpu_name()
