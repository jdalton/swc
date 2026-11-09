//! Compare payload sizes and packing times using the same stripped host addon.
use std::{fs, io::Cursor, time::Instant};

use sha2::{Digest, Sha512};
use swc_native_addon::format::{native_target, pack, NativeTarget, Payload, HEADER_LEN};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let path = std::env::args_os()
        .nth(1)
        .ok_or("expected a stripped native addon path")?;
    let raw = fs::read(path)?;
    let target = NativeTarget::host().ok_or("unsupported host")?;
    // Alternate order to expose warmup and host-load effects. Timing is
    // diagnostic; exact sizes and decoded bytes are deterministic checks.
    for changed_first in [false, true] {
        for changed in [changed_first, !changed_first] {
            let start = Instant::now();
            let bytes = if changed {
                pack(&raw, target)?
            } else {
                native_target(&mut Cursor::new(&raw), raw.len() as u64, target)?;
                let compressed = zstd::bulk::compress(&raw, 16)?;
                std::hint::black_box(Sha512::digest(&raw));
                compressed
            };
            let seconds = start.elapsed().as_secs_f64();
            let mut output = Cursor::new(Vec::new());
            let size = if changed {
                Payload::parse(&bytes)?.decode_into(&mut output)?;
                bytes.len() - HEADER_LEN
            } else {
                output = Cursor::new(zstd::bulk::decompress(&bytes, raw.len())?);
                bytes.len()
            };
            assert_eq!(output.into_inner(), raw);
            println!("changed={changed} compressed_bytes={size} pack_seconds={seconds:.3}");
        }
    }
    Ok(())
}
