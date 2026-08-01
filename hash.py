#!/usr/bin/env python3
"""hash — file hashing with multiple algorithms.

Reads files or stdin and outputs one or more hashes using stdlib only
(hashlib, argparse). Supports md5, sha1, sha256, sha512, and blake2b.

Usage:
    hash file.txt
    hash --sha256 --md5 file.txt
    cat file.txt | hash
    hash --help
"""

import argparse
import hashlib
import os
import sys

VERSION = "1.0.0"

ALGORITHMS = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
    "blake2b": lambda: hashlib.blake2b(),
}


def compute_hash(data: bytes, algo: str) -> str:
    """Compute a single hash of *data* using *algo*."""
    h = ALGORITHMS[algo]()
    h.update(data)
    return h.hexdigest()


def read_data(path: str) -> bytes:
    """Read *path* as raw bytes.  '-' means stdin."""
    if path == "-":
        return sys.stdin.buffer.read()
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except FileNotFoundError:
        print(f"error: no such file: '{path}'", file=sys.stderr)
        sys.exit(2)
    except IsADirectoryError:
        print(f"error: is a directory: '{path}'", file=sys.stderr)
        sys.exit(2)
    except PermissionError:
        print(f"error: permission denied: '{path}'", file=sys.stderr)
        sys.exit(2)
    except OSError as exc:
        print(f"error: cannot read '{path}': {exc}", file=sys.stderr)
        sys.exit(2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hash",
        description="Compute file hashes using one or more algorithms.",
        epilog="When no algorithm flag is given, defaults to --sha256.",
    )
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="*",
        default=["-"],
        help="File(s) to hash (default: stdin). Use '-' explicitly for stdin.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"hash {VERSION}",
    )
    for algo in ALGORITHMS:
        flag = f"--{algo}"
        parser.add_argument(
            flag,
            action="store_true",
            dest=algo,
            help=f"Output {algo.upper()} hash",
        )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Determine which algorithms to run.
    selected = [a for a in ALGORITHMS if getattr(args, a)]
    if not selected:
        selected = ["sha256"]

    for path in args.files:
        data = read_data(path)
        parts = []
        for algo in selected:
            parts.append(f"{algo}: {compute_hash(data, algo)}")
        label = path if path != "-" else "stdin"
        print(f"{label}: {'  '.join(parts)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
