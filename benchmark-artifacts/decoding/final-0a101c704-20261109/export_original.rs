use std::{fs, io::Cursor};
use sha2::{Digest, Sha512};
use swc_native_addon::format::{native_target, Header, NativeTarget, Payload};
fn main() -> Result<(), Box<dyn std::error::Error>> {
 let args:Vec<_>=std::env::args_os().collect();
 let raw=fs::read(&args[1])?;let target=NativeTarget::host().ok_or("unsupported host")?;
 native_target(&mut Cursor::new(&raw),raw.len() as u64,target)?;
 let frame=zstd::bulk::compress(&raw,16)?;
 let header=Header{target,compressed_len:frame.len() as u64,raw_len:raw.len() as u64,digest:Sha512::digest(&raw).into()};
 let payload:Vec<u8>=header.encode().into_iter().chain(frame).collect();
 let mut output=Cursor::new(Vec::new());Payload::parse(&payload)?.decode_into(&mut output)?;
 assert_eq!(output.into_inner(),raw);fs::write(&args[2],&payload)?;println!("payload_bytes={}",header.compressed_len);Ok(())
}
