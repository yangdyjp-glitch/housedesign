"""Keep original built-in outputs and copy project-bound images without resampling."""
from pathlib import Path
import json,hashlib,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];mapping=json.loads((ROOT/'07_renders/v18-entry/imagegen-output-map.json').read_text(encoding='utf-8'))
records=[]
for kind,folder,suffix in [('photos','v18-entry','-realistic.png'),('panoramas','vr-tour-v04','-ai-final.png')]:
    for ident,source in mapping[kind].items():
        src=Path(source);dst=ROOT/'07_renders'/folder/(ident+suffix);shutil.copy2(src,dst)
        digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        assert digest(src)==digest(dst)
        with Image.open(dst) as im:
            im.verify()
        with Image.open(dst) as im:
            size=list(im.size)
        if kind=='panoramas':assert size[0]==2*size[1]
        records.append(dict(kind=kind,id=ident,original=source,path=dst.relative_to(ROOT).as_posix(),sha256=digest(dst),resolution=size,upscaled=False))
(ROOT/'logs/v18-imagegen-outputs.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('V18_ORIGINAL_OUTPUTS_COLLECTED',len(records))
