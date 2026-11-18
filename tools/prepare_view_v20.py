from pathlib import Path
import json,re,subprocess,sys
R=Path('D:/AI-Yang.cn/HomeDesign');OUT=R/'09_delivery/main-integration-v20'
d=json.loads((R/'02_geometry/geometry-master-v20.json').read_text(encoding='utf-8'))
# History is preserved in master JSON; the view carries only currently rendered data.
view={k:v for k,v in d.items() if not k.startswith(('retired','provenance','assumptions'))}
for part in view['furniture']:
 if part.get('sourceObject','').startswith(('fridge-upper-','fridge-ceiling-closure')):part['planHidden']=True
fragment=(R/'tools/house-view-v20.template.html').read_text(encoding='utf-8').replace('HOUSE_DATA_PLACEHOLDER',json.dumps(view,ensure_ascii=False,separators=(',',':')))
assert len(fragment.encode('utf-8'))<1_000_000,len(fragment.encode('utf-8'))
assert '\\"' not in fragment[:fragment.index('<script type="application/json"')]
(R/'09_delivery/house-v20-fragment.html').write_text(fragment,encoding='utf-8')
renderer=Path('C:/Users/Administrator/.codex/plugins/cache/openai-bundled/visualize/1.0.50/skills/visualize/scripts/render.py')
subprocess.run([sys.executable,str(renderer),str(R/'09_delivery/house-v20-fragment.html'),str(R/'09_delivery/house-v20-preview.html'),'--force'],check=True)
scripts=re.findall(r'<script>([\s\S]*?)</script>',fragment)
assert len(scripts)==1
(OUT/'view-runtime.js').write_text(scripts[0],encoding='utf-8')
print('V20_VIEW_STAGED',len(fragment.encode('utf-8')),len(d['furnitureObjects']))
