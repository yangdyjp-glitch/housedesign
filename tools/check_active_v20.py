import json,hashlib,re
from pathlib import Path
from urllib.parse import urlparse,unquote
R=Path('D:/AI-Yang.cn/HomeDesign')
a=json.loads((R/'06_blender/active-model.json').read_text(encoding='utf-8'))
p=json.loads((R/'06_blender/active-presentation.json').read_text(encoding='utf-8'))
assert a['revision']==p['geometry_revision']==20
assert hashlib.sha256((R/'06_blender'/a['filename']).read_bytes()).hexdigest()==a['model_sha256']==p['model_sha256']
assert (R/'02_geometry/geometry-master.json').read_bytes()==(R/a['geometry']).read_bytes()
VIZ=Path('C:/Users/Administrator/.codex/visualizations/2026/10/29/01a187d1-69cc-73a1-805e-834e8e8bb476/house-structure.html')
assert VIZ.read_bytes()==(R/'09_delivery/house-v20-fragment.html').read_bytes()
h=(R/'09_delivery/index.html').read_text(encoding='utf-8');targets=re.findall(r'(?:href|src)="([^"]+)"',h)
checked=[t for t in targets if not urlparse(t).scheme and not t.startswith('#')]
assert all((R/'09_delivery'/unquote(t)).exists() for t in checked),checked
result={'status':'passed','activeRevision':20,'furniture':a['furniture_count'],'activeModelHashMatches':True,'geometryAliasMatches':True,'inlineModelMatches':True,'homepageLocalTargets':len(checked),'gallery':a['current_perspective_renders'],'tour':a['panorama_tour']}
(R/'09_delivery/main-integration-v20/活动版本最终核对.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
