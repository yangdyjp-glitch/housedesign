"""Record image-integrity checks after the operator has inspected all final views."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'07_renders/vr-tour-v01'
assert '--visual-reviewed' in sys.argv,'The flag must only follow actual final-image inspection.'
items=[]
for ident in ['living','dining','balcony','entry']:
    p=OUT/(ident+'-day.jpg')
    with Image.open(p) as im:
        assert im.size==(8192,4096);im.load();a=np.asarray(im)
        seam=float(np.abs(a[:,0,:].astype(float)-a[:,-1,:].astype(float)).mean())
        assert seam<8,(ident,seam)
        band=a[1024:3072,::16,:];assert float(band.std())>8 and float((band<3).all(axis=2).mean())<.5
    items.append(dict(id=ident,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),resolution=[8192,4096],seam_edge_mean_absolute_difference_255=round(seam,3),manually_reviewed=True))
assert len({q['sha256'] for q in items})==4
report=dict(revision=13,all_four_final_panoramas_reviewed=True,images=items,review_basis=['Native full-sphere images and matching perspective views were inspected','Four interior views retain the same v13 furniture geometry and finishes','Equirectangular unfold curves are projection; perspective viewer shows straight room geometry','Spherical axis orientation was tested with separate colored-axis scene','Single-eye panorama; not a measured site record, stereo capture or free walking'],originals='07_renders/vr-tour-v01/*-day.png',render_source='Blender Cycles 192 samples OptiX; no AI repaint',unchanged_context=['Window exterior neutral placeholder, kitchen and private rooms not furnished','Entry opening and equipment details still provisional'])
(ROOT/'logs/v13-panorama-visual-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('V13_FINAL_IMAGES_REVIEWED',json.dumps([dict(id=q['id'],seam=q['seam_edge_mean_absolute_difference_255']) for q in items]))
