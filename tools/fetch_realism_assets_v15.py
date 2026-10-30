"""Fetch a small, explicitly selected set of CC0 render assets from their primary API."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import urllib.request,json,hashlib,time
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'08_assets/photoreal-v15';OUT.mkdir(parents=True,exist_ok=True)
HEADER={'User-Agent':'HomeDesign-personal-local-render/1.0 (noncommercial selected assets)'}
def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url,headers=HEADER),timeout=60).read()
assets=['wood_floor','poly_wool_herringbone','green_point_park','potted_plant_01','potted_plant_02']
jobs=[];catalog={}
for asset in assets:
    raw=fetch('https://api.polyhaven.com/files/'+asset);catalog[asset]=json.loads(raw)
    folder=OUT/asset;folder.mkdir(exist_ok=True)
    (folder/'api-files.json').write_bytes(raw)
    if asset.startswith('potted_'):
        main=catalog[asset]['blend']['1k']['blend'];jobs.append((asset,folder/(asset+'_1k.blend'),main))
        for rel,item in main.get('include',{}).items():jobs.append((asset,folder/rel,item))
    elif asset=='green_point_park':jobs.append((asset,folder/(asset+'_4k.exr'),catalog[asset]['hdri']['4k']['exr']))
    else:
        for key in ['Diffuse','Rough','nor_gl']:
            rec=catalog[asset][key]['2k']['jpg'];jobs.append((asset,folder/Path(rec['url']).name,rec))
def download(job):
    asset,path,rec=job;path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists() or hashlib.md5(path.read_bytes()).hexdigest()!=rec['md5']:
        blob=fetch(rec['url']);assert hashlib.md5(blob).hexdigest()==rec['md5'];path.write_bytes(blob)
    assert path.stat().st_size==rec['size']
    return dict(asset=asset,path=path.relative_to(ROOT).as_posix(),url=rec['url'],bytes=path.stat().st_size,md5=rec['md5'],sha256=hashlib.sha256(path.read_bytes()).hexdigest(),source='https://polyhaven.com/a/'+asset,license='CC0',license_source='https://polyhaven.com/license')
entries=[]
with ThreadPoolExecutor(max_workers=4) as pool:
    for f in as_completed([pool.submit(download,j) for j in jobs]):
        row=f.result();entries.append(row);print('ASSET_READY',row['path'],flush=True)
report=dict(date='2026-10-31',purpose='PBR materials, foliage and environment lighting for a consistent true spherical VR render; outdoor HDRI is illustrative, not site scenery',license='CC0',entries=sorted(entries,key=lambda r:r['path']))
(OUT/'asset-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('REALISM_ASSETS_COMPLETE',len(entries),sum(q['bytes'] for q in entries))
