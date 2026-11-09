Hash20 packing handoff. No production edit by compression worker; decoder worker owns combined Hash20 + bulk write-batching integration.

confirmation.json: three alternating fresh-process pairs/input, Hash21/Search8 vs Hash20/Search8, quiet host with indexers suspended. Whole-process CPU includes compression, file output, and full-byte roundtrip. Peak RSS includes compressor context retained through verification; not direct production-packer or runtime memory. CPU idle before each run is recorded. packing-summary.json contains exact statistics and frame hashes. Expected frame hashes must be checked against the integrated production packer.

lookup table: earlier Hash23 reference 33.55 MB, previous Hash21 8.39 MB, final candidate Hash20 4.19 MB. Total reduction 29.36 MB; incremental 4.19 MB. allocation-chart-input.json retains exact values.

four-arm-results.json: original16+stream, Hash21+stream, Hash21+bulk, Hash20+bulk. Five fresh processes/arm/input, 14 rounds each with 2 warmups. Order rotates through first 4 trials and reverses for final trial. Candidate Hash20 without complementary write batching had consistent Rspack latency cost; those observations are research evidence, not the final combined profile. New combined-profile final timings must supersede them in the public headline. Raw results preserved for reproducibility.

Build standalone tune with cargo build --release --bin tune. Reproduction command: python3 confirm.py ./target/release/tune <swc.node> <rspack.node> hash20. The original script includes the recorded guard deadline; update that deadline for a newly authorized quiet session. Do not compare pre-pause screen timings to quiet data. Input versions and exact hashes are checked by the script.
