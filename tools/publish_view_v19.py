from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
VIZ=Path('C:/Users/Administrator/.codex/visualizations/2026/10/29/01a187d1-69cc-73a1-805e-834e8e8bb476/house-structure.html')
template=(ROOT/'tools/house-view-v19.template.html').read_text(encoding='utf-8');data=(ROOT/'02_geometry/geometry-master-v19.json').read_text(encoding='utf-8')
fragment=template.replace('HOUSE_DATA_PLACEHOLDER',data);assert len(fragment.encode())<1_000_000
VIZ.write_text(fragment,encoding='utf-8');(ROOT/'09_delivery/house-v19-fragment.html').write_text(fragment,encoding='utf-8')
render=Path('C:/Users/Administrator/.codex/plugins/cache/openai-bundled/visualize/1.0.50/skills/visualize/scripts/render.py')
subprocess.run([sys.executable,str(render),str(VIZ),str(ROOT/'09_delivery/house-v19-preview.html'),'--force'],check=True)
print('V19_VIEW_PUBLISHED',len(fragment.encode()))
