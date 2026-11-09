# Smaller native addon files and faster verified decoding

Final implementation: `0a101c7041509ce3290f2cb8dba659c4c1ae03d1`. The complete self-loading `.node` file embeds the compressed native addon and its verified loader.

| Measurement | SWC 1.16.2, original → final | Rspack 1.7.0, original → final |
| --- | ---: | ---: |
| Complete `.node` file | 8.989328 → 8.246288 MB (8.27% smaller) | 12.985232 → 11.697296 MB (9.92% smaller) |
| Verified decoding elapsed | 50.876 → 44.926 ms (11.70% lower) | 76.5055 → 68.401 ms (10.59% lower) |
| Peak decoding benchmark process memory | 45.989888 → 44.400640 MB (3.46% lower) | 72.204288 → 65.159168 MB (9.76% lower) |

The original control uses a level-16 frame and the streaming decoder. The final result uses level 22, long-distance matching, the existing bounded window, HashLog 20 / SearchLog 8, and bounded bulk decoding with batched output writes. The figures above use matched controls; all sizes are decimal MB. These are built files and measured process values, not estimates of npm transfer size or filesystem allocation.

## Implementation

When a frame's history window already covers its complete decoded image, zstd can use the output buffer as history instead of allocating a separate streaming history buffer. Bulk output is capped at 64 MiB; larger images and legacy small-window frames keep streaming. Hash chunks and their ordering stay unchanged, including larger parallel-hashing chunks. Smaller output writes are grouped into 256 KiB slices of the existing decoded buffer, adding no buffer allocation or copying.

The manual frame-window check remains before decompression. Configured window bounds, exact output length, single-frame validation, full-byte SHA-512/BLAKE3 verification, native target/image checks, cache security and atomic publication remain intact. `source.patch` records the combined change from 4ff6ace891c37a97f3eff06280d2e728c81d8fcb; the final source is available at the implementation commit.

## Runtime measurements

`results.json` contains three controls, each with five fresh processes per input and balanced ordering: `original16_stream`, `hash21_bulk`, and `hash20_batch256`. Each process runs 14 decodes; the first two are warmups and the remaining 12 determine its median. `summary.json` reports medians of those process medians. All 420 outputs passed independent full-byte SHA-512 checks. The final variant was faster in all five matched process pairs versus both original and Hash21 controls for both inputs.

The timed region invokes the real Payload::decode_into with full runtime BLAKE3 and a fresh temporary file. Independent SHA-512 verification runs outside timing. CPU uses CLOCK_PROCESS_CPUTIME_ID; elapsed uses Instant. Peak RSS is whole-process, including setup and independent validation. The benchmark excludes fsync, addon loading, cold input I/O and complete atomic cache publication. Results are local Darwin ARM64 measurements, not cross-platform startup guarantees.

Against the separate HashLog 21 + bulk control, the final table+batching combination reduces elapsed decoding from 48.3365→44.926 ms (7.06%) and 74.338→68.401 ms (7.99%). This incremental comparison uses a different baseline from the main chart. Its peak process RSS is 44.318720→44.400640 MB and 65.159168→65.159168 MB, respectively.

The user authorized guarded temporary suspension of 19 fff-mcp indexers; unrelated work remained active. Ten one-second host snapshots before trial groups recorded 71.49–81.84% idle CPU (median 78.49%); raw snapshots are in `host.json`. They are not continuous monitoring. The indexers were restored after the batch. The optional `quiet_host.py`, its README and tests are local reproduction aids with PID/start-time/command checks and timeout/parent-exit recovery; they are not production dependencies.

## File size and packing tradeoffs

`carrier-sizes.json` records actual final `.node` builds, including exact frame and file hashes. The production packer output matched both measured Hash20 frames byte-for-byte, and each file contained exactly the verified embedded payload. `original-carrier-sizes.json` records actual level-16/streaming controls. The original frames match the historical compressed sizes exactly: 8.446098 MB and 12.406049 MB.

The bounded decoder adds 0.016512 MB (0.20%) to the SWC file versus a fixed level-22 payload with streaming, while the Rspack file stays unchanged. The final batching/table change adds no further complete-file growth. Net complete-file savings versus the original controls are 0.743040 MB and 1.287936 MB.

The separate packing chart compares the configured HashLog 23 large-table control (33.554432 MB) with HashLog 20 (4.194304 MB): 29.360128 MB less table allocation, or 87.5%. This is not total packing-process memory. In quiet paired HashLog 21 → HashLog 20 measurements, median packing benchmark RSS falls 4.194304 MB on each input, while whole-process CPU rises 9.00% for SWC and 5.02% for Rspack. That lower-priority release-time CPU cost is retained alongside smaller tables and faster final decoding. `packing/` contains exact paired data, source, allocation accounting and reproduction instructions.

## Quality checks

Combined native crate release tests: 40 passed, 3 explicit platform/volume skips (APFS, btrfs, NTFS). Focused Clippy with all targets and warnings denied, cargo fmt --all and git diff --check passed. The fixture suite covers single-segment and explicit full-history frames, legacy small-window fallback, SHA-512/BLAKE3 corruption, output-write failures, malformed size/window claims and below/at/above the 64 MiB bulk boundary. Both actual final files passed embedded-payload equality checks. Validation used a private canonical TMPDIR under /private/tmp, preserving strict rejection of symlinked cache paths. Commands and output are in `validate-run.py` and `validation.log`. Full workspace/integration suites were not part of these focused checks.

## Reproduce

Use the compiler and exact source revisions/binary hashes in `environment.json`. The benchmark example is `compare_decoding.rs`, built with the repository release profile. `inputs.json` records raw input hashes; each row of `results.json` records frame and executable hashes. Build the streaming control at 4ff6ace89, the Hash21 bulk control at 5a1bada2b, and the final variant at 0a101c704; use the executable paths documented in `run.py` or adjust them together.

`export_original.rs` recreates original level-16 payloads with target and full-byte checks; `export_selected.rs` calls the actual final packer and verifies every decoded byte. The scripts `original-carriers.py` and `validate-run.py` show exact file-build commands and equality checks. Their temporary exporter example files are removed afterward. Adjust disposable worktree/target paths to the new environment.

The final timing runner expects original frames under /tmp/swc-decoding-quiet-final and Hash21/Hash20 frames beside the raw inputs under /tmp/swc-compression-bench. It includes an explicit guarded-window deadline: update it only for a new authorized quiet session. Run `analyze.py` to regenerate the summary and `chart.py` with matplotlib to regenerate the main chart. See `harness-README.md` for opt-in host control and restoration checks, and serialize heavy builds/benchmarks.
