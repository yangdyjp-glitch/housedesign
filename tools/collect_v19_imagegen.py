from pathlib import Path
import json,hashlib,shutil
from PIL import Image
R=Path(__file__).resolve().parents[1];m=json.loads((R/'07_renders/v19-deepening/imagegen-output-map.json').read_text(encoding='utf8'));records=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for kind,folder,suf in [('photos','v19-deepening','-realistic.png'),('panoramas','vr-tour-v05','-ai-final.png')]:
 for ident,path in m[kind].items():
  src=Path(path);dst=R/'07_renders'/folder/(ident+suf);shutil.copy2(src,dst);assert sha(src)==sha(dst)
  with Image.open(dst) as im:im.verify()
  with Image.open(dst) as im:size=list(im.size)
  if kind=='panoramas':assert size[0]==size[1]*2
  records.append(dict(kind=kind,id=ident,original=path,path=dst.relative_to(R).as_posix(),sha256=sha(dst),resolution=size,upscaled=False))
(R/'logs/v19-imagegen-outputs.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('V19_ORIGINALS_COLLECTED',len(records))
