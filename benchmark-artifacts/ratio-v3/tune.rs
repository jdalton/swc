use std::time::Instant;
use zstd::zstd_safe::CParameter::*;
fn main(){
 let args:Vec<_>=std::env::args().collect();let raw=std::fs::read(&args[1]).unwrap();let variant=&args[2];
 let t=Instant::now();let mut c=zstd::bulk::Compressor::new(22).unwrap();
 c.set_parameter(EnableLongDistanceMatching(true)).unwrap();c.set_parameter(WindowLog((64-(raw.len() as u64-1).leading_zeros()).clamp(10,26))).unwrap();
 let params=match variant.as_str(){
 "full"=>vec![],"selected"=>vec![HashLog(23),SearchLog(7)],"hash24"=>vec![HashLog(24)],"hash23"=>vec![HashLog(23)],"search7"=>vec![SearchLog(7)],"chain25"=>vec![ChainLog(25)],"compact"=>vec![ChainLog(25),HashLog(23),SearchLog(7)],_=>panic!("unknown variant")};
 for p in params {c.set_parameter(p).unwrap();}
 let packed=c.compress(&raw).unwrap();let seconds=t.elapsed().as_secs_f64();
 std::fs::write(format!("{}.{}.zst",args[1],variant),&packed).unwrap();
 let decoded=zstd::bulk::decompress(&packed,raw.len()).unwrap();assert_eq!(decoded,raw);
 println!("variant={variant} bytes={} pack_s={seconds:.6}",packed.len());
}
