import urllib.request,tarfile,io,hashlib,json,pathlib
p=pathlib.Path('/tmp/swc-btrfs-bench')
url='https://registry.npmjs.org/@swc/core-linux-arm64-gnu/-/core-linux-arm64-gnu-1.16.2.tgz'
b=urllib.request.urlopen(url).read()
with tarfile.open(fileobj=io.BytesIO(b),mode='r:gz') as t:
 m=next(m for m in t.getmembers() if m.name.endswith('.node'))
 raw=t.extractfile(m).read()
(p/'swc.linux-arm64-gnu.node').write_bytes(raw)
(p/'input.json').write_text(json.dumps({'package':'@swc/core-linux-arm64-gnu','version':'1.16.2','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'source':url},indent=2))
print((p/'input.json').read_text())
