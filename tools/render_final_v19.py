from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[1];B=R/'tools/runtime/blender/blender-4.5.15-windows-x64/blender.exe'
for args,label in [(['--final'],'perspectives'),(['--final','--pano'],'spheres')]:
 with (R/('logs/v19-final-'+label+'-render.log')).open('w',encoding='utf8') as out:
  p=subprocess.run([str(B),'-b',str(R/'06_blender/home-main-v19.blend'),'--python',str(R/'tools/render_deepening_v19.py'),'--',*args],stdout=out,stderr=subprocess.STDOUT)
  assert p.returncode==0
 print('V19_FINAL_NATIVE_READY',label,flush=True)
