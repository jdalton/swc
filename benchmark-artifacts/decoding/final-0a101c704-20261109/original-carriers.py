import pathlib,subprocess,os,shutil,json,hashlib,time
root=pathlib.Path('/Users/jdalton/projects/swc-native-decode-pass');p=pathlib.Path(__file__).parent
source=root/'crates/swc_native_addon/src/format.rs';candidate=source.read_bytes();example=root/'crates/swc_native_addon/examples/export_original_temp.rs';rows=[]
def run(args,env=None):
 if time.time()>=1794256830:raise RuntimeError('quiet-host deadline')
 subprocess.run(args,cwd=root,env=env,check=True)
try:
 shutil.copy2(p/'export_original.rs',example)
 run(['cargo','build','-p','swc_native_addon','--release','--example','export_original_temp','--target-dir','/tmp/swc-decode-pass-target'])
 for name,file,expected in [('SWC','swc-1.16.2.node',8446098),('Rspack','rspack-1.7.0.node',12406049)]:
  payload=p/(name+'-original16.swcn')
  run(['/tmp/swc-decode-pass-target/release/examples/export_original_temp','/tmp/swc-compression-bench/'+file,str(payload)])
  assert len(payload.read_bytes())-96==expected
  rows.append({'input':name,'payload_bytes':expected,'payload_sha256':hashlib.sha256(payload.read_bytes()).hexdigest()})
 example.unlink();source.write_bytes((p/'baseline-format.rs').read_bytes())
 for row in rows:
  name=row['input'];payload=p/(name+'-original16.swcn');env=os.environ.copy();env['SWC_NATIVE_BINDING_PAYLOAD']=str(payload)
  run(['cargo','build','-p','binding_native_addon','--release','--features','embedded-payload','--target-dir','/tmp/swc-decode-pass-target'],env)
  data=pathlib.Path('/tmp/swc-decode-pass-target/release/libbinding_native_addon.dylib').read_bytes();assert data.count(payload.read_bytes())==1
  (p/(name+'-carrier-original16.node')).write_bytes(data);row.update(carrier_bytes=len(data),carrier_sha256=hashlib.sha256(data).hexdigest(),embedded_payload_matches=True)
finally:
 source.write_bytes(candidate)
 if example.exists():example.unlink()
(p/'original-carrier-sizes.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
