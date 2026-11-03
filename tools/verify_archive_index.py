"""Verify the staged Git objects preserve each inventoried file's exact bytes."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'logs/repository-archive-manifest.json').read_text(encoding='utf-8'))
raw=subprocess.check_output(['git','ls-files','--stage','-z'],cwd=ROOT);index={}
for row in raw.split(b'\0'):
    if not row:continue
    meta,name=row.split(b'\t',1);mode,oid,stage=meta.split();assert stage==b'0';index[name.decode('utf-8')]=oid.decode('ascii')
for q in manifest['entries']:
    content=(ROOT/q['path']).read_bytes();assert len(content)==q['bytes'] and hashlib.sha256(content).hexdigest()==q['sha256'],q['path']
    oid=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest();assert index.get(q['path'])==oid,q['path']
print(json.dumps(dict(status='EXACT_ARCHIVE_BYTES_STAGED',files=len(manifest['entries']),active_model_revision=manifest['active_model_revision'])))
