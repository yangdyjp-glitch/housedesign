"""Inventory exact project bytes selected by Git; never traverse ignored runtimes."""
from pathlib import Path
import hashlib,json,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1];MANIFEST='logs/repository-archive-manifest.json'
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
out=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT)
paths=sorted(set(p.decode('utf-8') for p in out.split(b'\x00') if p))
entries=[];archive_checks=[]
for rel in paths:
    if rel==MANIFEST:continue
    p=ROOT/rel
    if not p.is_file():continue
    size=p.stat().st_size;assert size<100*1024*1024,(rel,size)
    assert not rel.startswith('tools/runtime/') and '/__pycache__/' not in rel
    entries.append(dict(path=rel,bytes=size,sha256=sha(p)))
    if p.suffix.lower()=='.zip':
        with zipfile.ZipFile(p) as z:
            bad=[n for n in z.namelist() if Path(n).name.lower() in ['.env','credentials.json'] or Path(n).suffix.lower() in ['.pem','.pfx','.p12']]
            assert not bad,(rel,bad);archive_checks.append(dict(path=rel,entries=len(z.namelist()),credential_filenames=[]))
active=json.loads((ROOT/'06_blender/active-model.json').read_text(encoding='utf-8'))
assert active['revision']==13
for key,path in [('geometry_sha256',active['geometry']),('style_sha256',active['style']),('model_sha256','06_blender/'+active['filename'])]:assert sha(ROOT/path)==active[key],(key,path)
source=ROOT/'09_delivery/house-v13-fragment.html';host=Path(r'C:\Users\Administrator\.codex\visualizations\2026\10\29\01a187d1-69cc-73a1-805e-834e8e8bb476\house-structure.html')
assert sha(source)==sha(host),'Project copy must include the latest durable interactive source'
report=dict(date='2026-10-31',repository='https://github.com/yangdyjp-glitch/housedesign',repository_visibility_at_upload='public',active_model_revision=13,scope='All current project sources, references, historical models, renders, panoramas, deliveries, scripts and design/review records selected by .gitignore',new_advice_status='proposal only; no model or furniture placements changed',excluded=['Local tools/runtime software and Python environments','Downloaded third-party software installers','Interpreter/browser/tool caches and machine credentials'],manifest_self_excluded_from_entries=True,files=len(entries),bytes=sum(q['bytes'] for q in entries),largest=max(entries,key=lambda q:q['bytes']),exact_bytes_preserved=True,current_model_sha256=active['model_sha256'],interactive_source_matches_durable=True,archives=archive_checks,entries=entries)
(ROOT/MANIFEST).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(files=report['files'],bytes=report['bytes'],largest=report['largest'],archive_count=len(archive_checks),active_revision=13),ensure_ascii=False))
