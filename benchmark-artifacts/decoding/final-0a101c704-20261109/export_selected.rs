use std::{fs,io::Cursor};
use swc_native_addon::format::{pack,NativeTarget,Payload};
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<_>=std::env::args_os().collect();let raw=fs::read(&args[1])?;
 let bytes=pack(&raw,NativeTarget::host().ok_or("unsupported host")?)?;
 let payload=Payload::parse(&bytes)?;let mut decoded=Cursor::new(Vec::new());payload.decode_into(&mut decoded)?;assert_eq!(decoded.into_inner(),raw);
 fs::write(&args[2],bytes)?;Ok(())
}
