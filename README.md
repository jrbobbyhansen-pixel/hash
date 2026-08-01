# hash

A zero-dependency CLI tool for computing file hashes using multiple algorithms (md5, sha1, sha256, sha512, blake2b). Reads files or stdin and outputs the requested hash(es). Built entirely on Python stdlib (`hashlib`, `argparse`).

```bash
# Install
pip install git+https://github.com/jrbobbyhansen-pixel/hash.git

# Hash a file (default: sha256)
hash ./somefile.iso

# Multiple algorithms
hash --md5 --sha256 --blake2b ./somefile.iso

# Pipe data via stdin
cat ./somefile.iso | hash --sha512
```

## Benchmarks

| Test | Files (1KB each) | manta-hash | sha256sum (baseline) |
|------|-----------------|-----------|---------------------|
| Small | 5 | 0.04s, 0.04MB | 0.005s, 0.07MB |
| Medium | 20 | 0.05s, 0.05MB | 0.006s, 0.07MB |
| Large | 50 | 0.04s, 0.05MB | 0.007s, 0.07MB |

Run your own: `python3 benchmark_hash.py`

## License

MIT
