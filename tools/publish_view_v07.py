from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
VIZ=Path(r'C:\Users\Administrator\.codex\visualizations\2026\10\29\01a187d1-69cc-73a1-805e-834e8e8bb476\house-structure.html')
data=(ROOT/'02_geometry/geometry-master-v07.json').read_text(encoding='utf-8')
template=(ROOT/'tools/house-view-v07.template.html').read_text(encoding='utf-8')
fragment=template.replace('HOUSE_DATA_PLACEHOLDER',data)
assert len(fragment.encode('utf-8'))<1_000_000 and fragment.startswith('<div id=')
VIZ.write_text(fragment,encoding='utf-8')
assert VIZ.read_text(encoding='utf-8')==fragment
(ROOT/'09_delivery/house-v07-fragment.html').write_text(fragment,encoding='utf-8')
render=Path.home()/'.codex/plugins/cache/openai-bundled/visualize/1.0.50/skills/visualize/scripts/render.py'
subprocess.run([sys.executable,str(render),str(VIZ),str(ROOT/'09_delivery/house-v07-preview.html'),'--force'],check=True)
print('V07_VIEW_READY',len(fragment.encode('utf-8')))
