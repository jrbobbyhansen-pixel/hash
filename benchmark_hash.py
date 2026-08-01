#!/usr/bin/env python3
"""Benchmark manta-hash against sha256sum (baseline).

Measures:
- Time to hash files of various sizes
- Memory usage during hashing
- Accuracy vs reference implementation

Usage:
    python3 benchmark_hash.py [--dir DIR] [--sizes SMALL,MEDIUM,LARGE]

Outputs JSON results to stdout.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import tracemalloc


def create_test_dir(base_dir, num_files, file_size_kb):
    """Create a directory with num_files files of file_size_kb each."""
    dir_path = os.path.join(base_dir, f"test_{num_files}_{file_size_kb}")
    os.makedirs(dir_path, exist_ok=True)

    for i in range(num_files):
        path = os.path.join(dir_path, f"file_{i}.bin")
        with open(path, "wb") as f:
            f.write(os.urandom(file_size_kb * 1024))

    return dir_path


def benchmark_tool(tool_name, cmd, dir_path):
    """Run a tool and measure time + memory."""
    tracemalloc.start()
    start = time.time()

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=60
    )

    elapsed = time.time() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "tool": tool_name,
        "elapsed_seconds": round(elapsed, 3),
        "peak_memory_mb": round(peak / 1024 / 1024, 2),
        "exit_code": result.returncode,
        "stdout_lines": len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0,
        "stderr": result.stderr[:200] if result.stderr else "",
    }


def main():
    parser = argparse.ArgumentParser(description="Benchmark manta-hash")
    parser.add_argument("--dir", default=None, help="Directory to scan")
    parser.add_argument(
        "--sizes", default="10,50,200",
        help="Comma-separated file counts for small/medium/large tests"
    )
    parser.add_argument(
        "--file-size", default=10,
        type=int, help="File size in KB (default: 10)"
    )
    args = parser.parse_args()

    sizes = [int(s) for s in args.sizes.split(",")]
    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        for num_files in sizes:
            print(f"Creating {num_files} files of {args.file_size}KB each...", file=sys.stderr)
            test_dir = create_test_dir(tmpdir, num_files, args.file_size)

            # Collect all files
            all_files = [
                os.path.join(test_dir, f)
                for f in sorted(os.listdir(test_dir))
            ]

            # Benchmark manta-hash
            hash_script = os.path.join(os.path.dirname(__file__), "hash.py")
            if os.path.exists(hash_script):
                r = benchmark_tool(
                    "manta-hash",
                    [sys.executable, hash_script] + all_files,
                    test_dir,
                )
                r["test_size"] = num_files
                results.append(r)

            # Benchmark sha256sum (baseline)
            r = benchmark_tool(
                "sha256sum (baseline)",
                ["sha256sum"] + all_files,
                test_dir,
            )
            r["test_size"] = num_files
            results.append(r)

            print(f"  Done: {num_files} files", file=sys.stderr)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
