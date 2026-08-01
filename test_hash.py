"""Tests for the hash CLI tool."""

import hashlib
import os
import subprocess
import sys
import tempfile

import pytest

# Path to the hash script
HASH_SCRIPT = os.path.join(os.path.dirname(__file__), "hash.py")


def run_hash(*args, input_data: bytes | None = None) -> subprocess.CompletedProcess:
    """Run hash.py with *args* and optional stdin *input_data*."""
    cmd = [sys.executable, HASH_SCRIPT, *args]
    proc = subprocess.run(
        cmd,
        input=input_data,
        capture_output=True,
        timeout=10,
    )
    # Decode stdout/stderr to str for easier assertions
    return subprocess.CompletedProcess(
        args=proc.args,
        returncode=proc.returncode,
        stdout=proc.stdout.decode("utf-8", errors="replace"),
        stderr=proc.stderr.decode("utf-8", errors="replace"),
    )


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def temp_file():
    """Yield a temporary file with known content, then clean up."""
    content = b"hello world\n"
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(content)
        f.flush()
        path = f.name
    yield path, content
    os.unlink(path)


# ── Happy path ────────────────────────────────────────────────────────


class TestHappyPath:
    def test_default_sha256(self, temp_file):
        """Default (no flags) should output sha256."""
        path, content = temp_file
        expected = hashlib.sha256(content).hexdigest()
        result = run_hash(path)
        assert result.returncode == 0
        assert expected in result.stdout

    def test_md5(self, temp_file):
        """--md5 flag produces md5 hash."""
        path, content = temp_file
        expected = hashlib.md5(content).hexdigest()
        result = run_hash("--md5", path)
        assert result.returncode == 0
        assert expected in result.stdout

    def test_sha1(self, temp_file):
        """--sha1 flag produces sha1 hash."""
        path, content = temp_file
        expected = hashlib.sha1(content).hexdigest()
        result = run_hash("--sha1", path)
        assert result.returncode == 0
        assert expected in result.stdout

    def test_sha512(self, temp_file):
        """--sha512 flag produces sha512 hash."""
        path, content = temp_file
        expected = hashlib.sha512(content).hexdigest()
        result = run_hash("--sha512", path)
        assert result.returncode == 0
        assert expected in result.stdout

    def test_blake2b(self, temp_file):
        """--blake2b flag produces blake2b hash."""
        path, content = temp_file
        expected = hashlib.blake2b(content).hexdigest()
        result = run_hash("--blake2b", path)
        assert result.returncode == 0
        assert expected in result.stdout

    def test_multiple_algorithms(self, temp_file):
        """Multiple algorithm flags produce all requested hashes."""
        path, content = temp_file
        result = run_hash("--md5", "--sha256", "--blake2b", path)
        assert result.returncode == 0
        assert hashlib.md5(content).hexdigest() in result.stdout
        assert hashlib.sha256(content).hexdigest() in result.stdout
        assert hashlib.blake2b(content).hexdigest() in result.stdout

    def test_stdin(self):
        """Reading from stdin works."""
        content = "stdin test data"
        result = run_hash(input_data=content.encode())
        assert result.returncode == 0
        expected = hashlib.sha256(content.encode()).hexdigest()
        assert expected in result.stdout
        assert "stdin" in result.stdout

    def test_multiple_files(self, temp_file):
        """Multiple file arguments each produce output."""
        path, content = temp_file
        result = run_hash(path, path)
        assert result.returncode == 0
        lines = result.stdout.strip().splitlines()
        assert len(lines) == 2

    def test_version(self):
        """--version prints version string and exits 0."""
        result = run_hash("--version")
        assert result.returncode == 0
        assert "hash " in result.stdout

    def test_help(self):
        """--help prints usage and exits 0."""
        result = run_hash("--help")
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()


# ── Error path ────────────────────────────────────────────────────────


class TestErrorPath:
    def test_nonexistent_file(self):
        """Missing file exits 2 with a clear error."""
        result = run_hash("/tmp/nonexistent-file-xyz-123")
        assert result.returncode == 2
        assert "no such file" in result.stderr.lower()

    def test_directory(self):
        """A directory argument exits 2 with a clear error."""
        result = run_hash("/tmp")
        assert result.returncode == 2
        assert "is a directory" in result.stderr.lower()

    def test_permission_denied(self):
        """An unreadable file exits 2 with a clear error."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"data")
            path = f.name
        os.chmod(path, 0o000)
        try:
            result = run_hash(path)
            assert result.returncode == 2
            assert "permission denied" in result.stderr.lower()
        finally:
            os.chmod(path, 0o644)
            os.unlink(path)
