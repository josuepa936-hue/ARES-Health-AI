"""Explicit, bounded acquisition/preparation of PhysioNet MITDB 1.0.0 record 100.

Run from repo root: python -m scripts.prepare_research_ecg --download --acknowledge-license
Never downloads on import, API startup, or HTTP request. No user-selected ECG uploads.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import urllib.request

from src.ares_health.research import ARTIFACT_PATH, analyze_segment, envelope, read_official_record

SOURCE = 'https://physionet.org/files/mitdb/1.0.0/'
# PhysioNet's official page lists this public, unsigned AWS distribution.
SOURCE_AWS_PUBLIC = 'https://physionet-open.s3.amazonaws.com/mitdb/1.0.0/'
FILES = {'100.hea': 10000, '100.dat': 2000000, '100.atr': 100000, 'SHA256SUMS.txt': 100000}


def acquire(directory: Path, source: str = SOURCE) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for name, limit in FILES.items():
        with urllib.request.urlopen(source+name, timeout=30) as response:
            payload = response.read(limit+1)
        if len(payload) > limit:
            raise ValueError('Official input exceeds acquisition size bound.')
        (directory/name).write_bytes(payload)


def verify(directory: Path) -> dict[str, str]:
    for name, limit in FILES.items():
        path = directory/name
        if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
            raise ValueError('Missing, linked, or oversized approved input file.')
    expected = {}
    for line in (directory/'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        parts = line.split()
        if len(parts) == 2:
            expected[parts[1].lstrip('*').removeprefix('./')] = parts[0]
    hashes = {}
    for name in ('100.hea', '100.dat', '100.atr'):
        digest = hashlib.sha256((directory/name).read_bytes()).hexdigest()
        if expected.get(name) != digest:
            raise ValueError(f'Official SHA-256 manifest mismatch/missing entry: {name}')
        hashes[name] = digest
    hashes['SHA256SUMS.txt'] = hashlib.sha256((directory/'SHA256SUMS.txt').read_bytes()).hexdigest()
    return hashes


def prepare(directory: Path, acquisition: str) -> dict:
    hashes = verify(directory)
    signal, samples, symbols = read_official_record(directory)
    result = analyze_segment(signal, 360, samples, symbols)
    source = SOURCE_AWS_PUBLIC if acquisition == 'official-public-aws' else SOURCE
    note = (
        'Files and checksum manifest acquired over HTTPS from the public AWS '
        'distribution linked by the official PhysioNet MIT-BIH page.'
        if acquisition == 'official-public-aws' else
        'Files and checksum manifest acquired over verified HTTPS from PhysioNet.'
        if acquisition == 'official-https' else
        'Local files and manifest are operator-supplied; matching hashes alone do not authenticate their origin.'
    )
    result['acquisition'] = {'method': acquisition, 'source_url': source,
                             'sha256': hashes, 'license_acknowledged': True,
                             'note': note}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--download', action='store_true')
    group.add_argument('--aws-public', action='store_true',
                       help='Use the public AWS distribution explicitly linked by PhysioNet.')
    group.add_argument('--official-files', type=Path)
    parser.add_argument('--acknowledge-license', action='store_true', required=True,
                        help='I reviewed the official source terms/citation and approve this public research use.')
    args = parser.parse_args()
    try:
        with tempfile.TemporaryDirectory() as temp:
            directory = args.official_files or Path(temp)
            if args.download:
                acquire(directory)
            if args.aws_public:
                acquire(directory, SOURCE_AWS_PUBLIC)
            mode = ('official-public-aws' if args.aws_public else
                    'official-https' if args.download else 'official-local-files')
            result = prepare(directory, mode)
    except Exception as exc:
        # Invalidate old scores on failed preparation; never retain a stale success.
        result = envelope('abstained', [f'Preparation failed ({type(exc).__name__}); verify network, optional dependencies, official files/checksums and metadata.'])
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    staged = ARTIFACT_PATH.with_suffix('.tmp')
    staged.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8')
    staged.replace(ARTIFACT_PATH)
    print(f"Research preparation: {result['status']}. Artifact: {ARTIFACT_PATH}")
    return 0 if result['status'] == 'benchmarked' else 1


if __name__ == '__main__':
    raise SystemExit(main())
