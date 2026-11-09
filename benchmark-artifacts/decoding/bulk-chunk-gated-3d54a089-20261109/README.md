# Bulk decoding with chunked writes: rejected

The final candidate reduced peak process memory but increased elapsed decoding in the reversed-order confirmation on both inputs. It is not part of production. These results are separate from the earlier 128 KiB streaming-buffer experiment.

Baseline: SWC commit `3d54a0896fa3ba5c4af023c3c259db277cca99ac`, unchanged streaming decoder, current SearchLog 8 compressed frames. Both variants receive identical input bytes; exact raw/frame hashes are in `inputs.json`. The candidate uses bounded bulk decompression followed by the existing hash/write chunk sizes. It keeps the manual window guard, exact length and full-byte integrity checks, and native-image validation. The final gate requires advertised history covering the complete output and caps bulk output at 64 MiB, preserving streaming for legacy small-window frames and larger outputs.

## Separate batches

`initial-*` records an ungated prototype using the same bulk path for these inputs. Initial process-median elapsed values were SWC 135.391→133.016 ms and Rspack 206.302→152.258 ms. This was provisional and did not justify adoption.

`final-*` records the rebuilt, gated candidate in reversed process order. Final process-median elapsed values were SWC 146.184→156.767 ms and Rspack 270.378→316.316 ms. Each input was slower in four of five paired process medians. Peak process RSS fell from 71.074→44.384 MB and 105.841→65.126 MB, respectively. The batches use different binaries and are not pooled. Source patches, binary hashes, and full samples preserve both results.

Both batches use five fresh process pairs per input, alternating process order, with 14 decodes/process and the first two rounds excluded from summaries. Timed work is Payload::decode_into, including full BLAKE3 and fresh tempfile writes. Independent full-byte SHA-512 verification runs outside timing. CPU uses CLOCK_PROCESS_CPUTIME_ID; elapsed uses Instant. Peak RSS is whole-process, including setup and independent validation. Each batch passed 280 independent verifications (560 total).

Heavy task-local work was serialized, but unrelated host compilation caused contention. Elapsed measurements are noisy; these results do not establish cold-start or cross-platform behavior. There is no fsync, addon loading, or full atomic cache publication in the timed region. The experiment did not alter payload bytes. The final release benchmark executable size is recorded in `final-environment.json`; carrier/package size was not measured after rejection.

## Reproduce

Check out the baseline commit in a disposable worktree and use the compiler recorded in `final-environment.json`. Build `cargo build -p swc_native_addon --release --example compare_decoding` and copy the example binary to `/tmp/swc-bulk-chunk-decode-before`. Apply `final-runtime.patch`, build again, and copy the result to `/tmp/swc-bulk-chunk-decode-after`. Use the exact input/frame hashes in `inputs.json` under `/tmp/swc-compression-bench`. `final-run.py` shows the exact alternating/reversed process order and benchmark commands. Its leading rebuild step and absolute paths reflect the local worktree/target; adapt those paths to the disposable checkout. Put the script in `/tmp/swc-decoding-bulk-chunk-confirm` (creating it first) and run it with other heavy work stopped. `analyze.py` reads results.json beside itself and regenerates the summary. The initial script/patch are retained separately for reproducing that prototype.

## Quality status

Baseline, initial prototype, and final gated release builds passed. All 560 decode outputs passed independent full-byte verification. Extra SHA-512 boundary and frame-mode fixtures were prepared but NOT run; `proposed-tests.patch` and the two fixture files are retained only as proposed follow-up coverage. The queued quality workflow was stopped during formatting after performance rejection, before crate tests, Clippy, or carrier builds. No claim is made that those checks passed. No runtime or test changes were retained in the production branch.
