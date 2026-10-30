"""Install pinned portable runtimes from their official, hash-checked archives."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib, json, re, urllib.request, zipfile

ROOT=Path(__file__).resolve().parents[1]
DOWNLOAD=ROOT/'logs/downloads'
RUNTIME=ROOT/'tools/runtime'
SPECS=[
 dict(name='Blender',version='4.5.15 LTS',file='blender-4.5.15-windows-x64.zip',
      url='https://download.blender.org/release/Blender4.5/blender-4.5.15-windows-x64.zip',
      checksum='https://download.blender.org/release/Blender4.5/blender-4.5.15.sha256',dest='blender'),
 dict(name='uv',version='0.13.6',file='uv-x86_64-pc-windows-msvc.zip',
      url='https://github.com/astral-sh/uv/releases/download/0.13.6/uv-x86_64-pc-windows-msvc.zip',
      checksum='https://github.com/astral-sh/uv/releases/download/0.13.6/uv-x86_64-pc-windows-msvc.zip.sha256',dest='uv')]

def request(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HomeDesign-local-setup'}),timeout=60)

def install(spec):
    with request(spec['checksum']) as response:checksum=response.read().decode()
    (DOWNLOAD/(spec['file']+'.official-sha256.txt')).write_text(checksum,encoding='utf-8')
    expected=None
    for line in checksum.splitlines():
        if spec['file'] in line or len(checksum.strip().split())==1:
            matches=re.findall(r'\b[a-fA-F0-9]{64}\b',line)
            if matches:expected=matches[0].lower();break
    if not expected:raise ValueError('Official checksum not found for '+spec['file'])
    archive=DOWNLOAD/spec['file']
    def digest(path):
        with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
    if not archive.exists() or digest(archive)!=expected:
        partial=archive.with_suffix('.download-part')
        with request(spec['url']) as response, partial.open('wb') as stream:
            size=0;last=0
            while chunk:=response.read(1024*1024):
                stream.write(chunk);size+=len(chunk)
                if size-last>=50*1024*1024:
                    print(json.dumps(dict(name=spec['name'],downloadedMiB=size//1024//1024)),flush=True);last=size
        if digest(partial)!=expected:raise ValueError('Checksum mismatch for '+spec['name'])
        partial.replace(archive)
    dest=RUNTIME/spec['dest'];dest.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as zipped:
        for item in zipped.namelist():
            if not (dest/item).resolve().is_relative_to(dest.resolve()):raise ValueError('Unsafe archive member')
        zipped.extractall(dest)
    result=dict(**spec,sha256=expected,archive=str(archive),installed=str(dest))
    print(json.dumps(dict(name=spec['name'],verified=True,installed=str(dest))),flush=True)
    return result

rows=[]
with ThreadPoolExecutor(max_workers=2) as pool:
    jobs={pool.submit(install,s):s for s in SPECS}
    for future in as_completed(jobs):
        try:rows.append(future.result())
        except Exception as error:
            rows.append(dict(name=jobs[future]['name'],error=str(error)))
            print(json.dumps(rows[-1]),flush=True)
(ROOT/'logs/runtime-install.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
if any('error' in row for row in rows):raise SystemExit(1)
