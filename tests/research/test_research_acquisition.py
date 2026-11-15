"""Acquisition contract tests: no network; official MIT or official public AWS only."""
import urllib.request

import pytest

from scripts import prepare_research_ecg as prep


class OfflineReply:
    def __init__(self, content: bytes):
        self.content = content

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size: int) -> bytes:
        return self.content[:size]


@pytest.mark.parametrize("source", [prep.SOURCE, prep.SOURCE_AWS_PUBLIC])
def test_only_explicit_physionet_sources_fetch_fixed_bounded_files(source, tmp_path, monkeypatch):
    requested = []
    def fake_urlopen(url, timeout):
        requested.append((url, timeout))
        return OfflineReply(b"approved-offline-fixture")
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    prep.acquire(tmp_path, source)
    assert [url for url, timeout in requested] == [source + name for name in prep.FILES]
    assert all(timeout == 30 for _, timeout in requested)
    assert all((tmp_path / name).read_bytes() == b"approved-offline-fixture" for name in prep.FILES)


def test_oversized_source_is_rejected_without_dropping_bounds(tmp_path, monkeypatch):
    def fake_urlopen(url, timeout):
        return OfflineReply(b"x" * 11_000)
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(ValueError, match="size bound"):
        prep.acquire(tmp_path)


def test_public_aws_is_documented_not_untrusted_arbitrary_mirror():
    assert prep.SOURCE_AWS_PUBLIC == "https://physionet-open.s3.amazonaws.com/mitdb/1.0.0/"
    assert prep.SOURCE == "https://physionet.org/files/mitdb/1.0.0/"
    assert set(prep.FILES) == {"100.hea", "100.dat", "100.atr", "SHA256SUMS.txt"}
