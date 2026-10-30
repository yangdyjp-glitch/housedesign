"""Download public upstream sources to an audit area; do not execute vendor code."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64, hashlib, json, re, subprocess, sys, urllib.request, zipfile

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'logs/vendor-audit'
INSTALLER=Path(r'C:\Users\Administrator\.codex\skills\.system\skill-installer\scripts\install-skill-from-github.py')
SPECS=[
 ('interior-design-expert','curiositech/some_claude_skills','.claude/skills/interior-design-expert'),
 ('moodboard-aesthetic-iteration','gujun1502/arch-skills','skills/moodboard-aesthetic-iteration'),
 ('interior-designer','wonsukchoi/domain-experts','roles/interior-designer'),
 ('xiong-interior-design','xionglaoshi/xiong-interior-design','.'),
 ('interior-design-visualizer','RyanZhang10/interior-design-visualizer','interior-design-visualizer')]

def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'HomeDesign-local-setup','Accept':'application/vnd.github+json' if 'api.github.com' in url else '*/*'})
    with urllib.request.urlopen(req,timeout=45) as response:return response.read()

def api(url):return json.loads(get(url))

def skill(spec):
    name,repo,path=spec
    page=get('https://github.com/'+repo).decode()
    sha=re.search(r'"currentOid":"([0-9a-f]{40})"',page).group(1)
    branch=re.search(r'"defaultBranch":"([^"]+)"',page).group(1)
    row=dict(name=name,repo=repo,path=path,commit=sha,default_branch=branch,resolution='Official GitHub embedded currentOid; API403 and git HTTPS timeout fallback')
    for candidate in ['LICENSE','LICENSE.md','LICENSE.txt']:
        try:
            raw=get('https://raw.githubusercontent.com/'+repo+'/'+sha+'/'+candidate)
            target=AUDIT/'licenses'/name;target.mkdir(parents=True,exist_ok=True)
            (target/candidate).write_bytes(raw);row['license_file']=str(target/candidate);break
        except Exception as e:row['license_note']=str(e)
    dest=AUDIT/'skills'/name
    if not dest.exists():
        cmd=[sys.executable,str(INSTALLER),'--repo',repo,'--path',path,'--name',name,'--ref',sha,
             '--dest',str(AUDIT/'skills'),'--method','download']
        proc=subprocess.run(cmd,text=True,encoding='utf-8',errors='replace',capture_output=True,timeout=200)
        row.update(download_returncode=proc.returncode,download_output=(proc.stdout+proc.stderr)[-3000:])
    else:row['download_note']='existing audit folder preserved'
    print(json.dumps(dict(skill=name,downloaded=(dest/'SKILL.md').is_file(),commit=sha),ensure_ascii=True),flush=True)
    return row

AUDIT.mkdir(parents=True,exist_ok=True)
rows=[]
with ThreadPoolExecutor(max_workers=5) as pool:
    jobs={pool.submit(skill,s):s for s in SPECS}
    for job in as_completed(jobs):
        try:rows.append(job.result())
        except Exception as e:rows.append(dict(name=jobs[job][0],error=str(e)));print(json.dumps(rows[-1]),flush=True)
source_record=AUDIT/'skill-sources.json'
if source_record.exists() and not (AUDIT/'skill-sources-api-attempt.json').exists():
    (AUDIT/'skill-sources-api-attempt.json').write_bytes(source_record.read_bytes())
source_record.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')

tools={}
for key,url in [('uv','https://github.com/astral-sh/uv/releases/expanded_assets/0.13.6'),
                ('mcp','https://pypi.org/pypi/mcp-for-blender/json')]:
    try:
        if key=='uv':
            html=get(url).decode();names=['uv-x86_64-pc-windows-msvc.zip','uv-x86_64-pc-windows-msvc.zip.sha256']
            assets=[]
            for name in names:
                href='/astral-sh/uv/releases/download/0.13.6/'+name
                assert href in html, name+' missing from official release'
                assets.append(dict(name=name,url='https://github.com'+href))
            tools[key]=dict(version='0.13.6',assets=assets)
        else:
            meta=api(url)
            wheel=next(a for a in meta['urls'] if a['packagetype']=='bdist_wheel')
            target=ROOT/'logs/downloads'/wheel['filename'];raw=get(wheel['url']);target.write_bytes(raw)
            assert hashlib.sha256(raw).hexdigest()==wheel['digests']['sha256']
            unpack=AUDIT/'mcp-package';unpack.mkdir(exist_ok=True)
            with zipfile.ZipFile(target) as archive:
                for name in archive.namelist():
                    final=(unpack/name).resolve()
                    if not final.is_relative_to(unpack.resolve()):raise ValueError('Unsafe wheel path')
                archive.extractall(unpack)
            tools[key]=dict(version=meta['info']['version'],wheel=str(target),sha256=wheel['digests']['sha256'],requires_dist=meta['info']['requires_dist'],project_urls=meta['info']['project_urls'])
    except Exception as e:tools[key]=dict(error=str(e))
try:
    index=get('https://download.blender.org/release/Blender4.5/').decode()
    (AUDIT/'blender45-index.html').write_text(index,encoding='utf-8')
    files=sorted(set(re.findall(r'blender-4\.5\.\d+-windows-x64\.zip',index)),key=lambda s:[int(n) for n in re.findall(r'\d+',s)])
    tools['blender']=dict(channel='4.5 LTS',windows_zips=files,latest=files[-1] if files else None,base_url='https://download.blender.org/release/Blender4.5/')
except Exception as e:tools['blender']=dict(error=str(e))
(AUDIT/'tool-sources.json').write_text(json.dumps(tools,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(tools,ensure_ascii=True),flush=True)
