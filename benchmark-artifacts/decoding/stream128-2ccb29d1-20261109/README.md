# Streaming output-buffer experiment (not adopted)

A 128 KiB decoder buffer reduced measured CPU use, but SWC elapsed decoding increased 5.66%. Production stays on its existing 64 KiB streaming buffer (with larger hashing batches on macOS x86_64). No decoder speedup is claimed.

The candidate patch only raises the streaming output buffer to zstd's recommended output size, 128 KiB. It retains full BLAKE3 verification, exact decoded length, native image validation, bounded window checks, and single-frame decoding. The payload bytes are identical between variants. The release example grew from 452,064 to 452,080 bytes; total carrier/package size was not measured because the candidate was rejected.

## Results and limitations

`summary.json` reports the median of five process medians. Each process runs 14 decodes, discarding its first two rounds. `results.json` retains all rounds. Processes alternate variant order. Every timed decode writes a fresh tempfile and hashes every byte with runtime BLAKE3. Independent SHA-512 verification runs outside the timed region. CPU time uses CLOCK_PROCESS_CPUTIME_ID; wall time uses Instant. Peak RSS is whole-process, including setup and independent validation.

This is a warm-input Darwin ARM64 microbenchmark, not cold startup, full cache publication, fsync, addon loading, npm transfer size, or cross-platform validation. Elapsed results are noisy; SWC was slower in four of five paired process medians, while Rspack was faster in all five. The mixed result does not justify a universal decoder change.

## Reproduce

1. Check out SWC commit `2ccb29d1a290658d58d35536f945f991324df93c` in a disposable worktree. Use the compiler in `environment.json` and its release profile.
2. Obtain the two Darwin ARM64 addons and the selected zstd frames identified by exact SHA-256 in `inputs.json`. The frames use level 22, long-distance matching, ceil(log2(raw length)) window capped at 26, HashLog 23, SearchLog 7. Generate frames with the compression benchmark sources linked from PR #12740 if needed; verify the hashes.
3. Build the baseline with `cargo build -p swc_native_addon --release --example compare_decoding`, and copy it to `/tmp/swc-block-decode-before`.
4. Apply `stream128-experimental.patch`, repeat the build, and copy it to `/tmp/swc-block-decode-after`. Do not ship this experimental patch.
5. Place the four input files in `/tmp/swc-compression-bench`. Create `/tmp/swc-decoding-block-bench`; put `run.py` and `analyze.py` there. Run `python3 run.py` with other heavy builds/benchmarks stopped, then `python3 analyze.py`. Paths in the small scripts can be adjusted together.
6. Run `chart.py` with matplotlib installed to regenerate the chart.

Both focused release builds passed, and all 280 decodes passed independent full-byte SHA-512 validation. No new production code was retained; no claim is made that this rejected experiment passed the full workspace test suite.
