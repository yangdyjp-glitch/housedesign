from pathlib import Path
import json,re,subprocess,sys
R=Path('D:/AI-Yang.cn/HomeDesign');OUT=R/'09_delivery/v20-complete'
d=json.loads((R/'02_geometry/geometry-master-v20-complete.json').read_text(encoding='utf8'))
view={k:v for k,v in d.items() if not k.startswith(('retired','provenance','assumptions'))}
for p in view['furniture']:
    if p.get('sourceObject','').startswith(('fridge-upper-','fridge-ceiling-closure')):p['planHidden']=True
fragment=(R/'tools/house-view-v20-complete.template.html').read_text(encoding='utf8').replace('HOUSE_DATA_PLACEHOLDER',json.dumps(view,ensure_ascii=False,separators=(',',':')))
assert len(fragment.encode())<1_000_000
(R/'09_delivery/house-v20-complete-fragment.html').write_text(fragment,encoding='utf8')
renderer=Path('C:/Users/Administrator/.codex/plugins/cache/openai-bundled/visualize/1.0.50/skills/visualize/scripts/render.py')
subprocess.run([sys.executable,str(renderer),str(R/'09_delivery/house-v20-complete-fragment.html'),str(R/'09_delivery/house-v20-complete-preview.html'),'--force'],check=True)
scripts=re.findall(r'<script>([\s\S]*?)</script>',fragment);assert len(scripts)==1
(OUT/'view-runtime.js').write_text(scripts[0],encoding='utf8')
print('V20_COMPLETE_VIEW_STAGED',len(fragment.encode()),len(d['furnitureObjects']))
