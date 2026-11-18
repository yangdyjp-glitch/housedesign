from pathlib import Path
import json,hashlib,base64,shutil,html
from PIL import Image
R=Path('D:/AI-Yang.cn/HomeDesign');OUT=R/'09_delivery/main-integration-v20';PH=R/'07_renders/v20-photographic';TOUR=R/'09_delivery/vr-tour-v06'
TOUR.mkdir(exist_ok=True);(TOUR/'全景原图').mkdir(exist_ok=True);(OUT/'photos').mkdir(exist_ok=True)
def read(path):return json.loads((R/path).read_text(encoding='utf-8-sig'))
def write(path,data):(R/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
g=read('02_geometry/geometry-master-v20.json');audit=read('09_delivery/main-integration-v20/主模型回读.json');assert audit['status']=='passed'
assert audit['modelSha256']==sha(R/'06_blender/home-main-v20.blend')
labels={'living':'客厅','dining':'餐厅','balcony':'阳台','entry':'门厅'};images=[];scenes=[]
positions={'living':[1800,4500],'dining':[770,8850],'balcony':[2050,850],'entry':[635,10100]}
views={'living':[-50,-10,70],'dining':[-25,-15,75],'balcony':[-8,-26,60],'entry':[-90,-12,95]}
for key,label in labels.items():
 for kind in ['photo','pano']:
  source=PH/f'{key}-{kind}.png';assert source.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
  with Image.open(source) as im:im.verify()
  with Image.open(source) as im:w,h=im.size
  if kind=='pano':assert w==h*2,(key,w,h)
  target=(OUT/'photos'/f'{key}.png') if kind=='photo' else (TOUR/'全景原图'/f'{key}.png');shutil.copy2(source,target)
  images.append({'id':key,'kind':kind,'path':source.relative_to(R).as_posix(),'deliveryPath':target.relative_to(R).as_posix(),'resolution':[w,h],'sha256':sha(source)})
  if kind=='pano':
   y,p,f=views[key];scenes.append({'id':key,'label':label,'image':source.relative_to(R).as_posix(),'imageData':'data:image/png;base64,'+base64.b64encode(source.read_bytes()).decode(),'positionPlanMm':positions[key],'eyeHeightMm':1600,'initialYawDeg':y,'initialPitchDeg':p,'initialFovDeg':f,'headingAtImageCenterDeg':0,'imageWidth':w,'imageHeight':h,'downloadName':label+'-360全景-v20.png'})
cfg={'title':'餐岛与办公半墙已整合 · 四区360°','revision':20,'geometry':'02_geometry/geometry-master-v20.json','geometrySha256':sha(R/'02_geometry/geometry-master-v20.json'),'model':'06_blender/home-main-v20.blend','modelSha256':audit['modelSha256'],'renderSourceModel':'06_blender/home-v20-render-source.blend','renderSourceModelSha256':sha(R/'06_blender/home-v20-render-source.blend'),'defaultScene':'living','northPlanDirection':'down','projection':'monoscopic equirectangular360x180','panoramas':scenes,'floor':g['floor'],'mapWalls':[dict(x=p['x'],z=p['z'],w=p['w'],d=p['d']) for p in g['walls'] if p.get('y',0)<1200],'nativeImageResolution':[scenes[0]['imageWidth'],scenes[0]['imageHeight']],'nativeAnchorResolution':[4096,2048],'method':'same-model full spherical native anchors + built-in image_gen photographic concepts; no raster upscaling','officeVariant':'B temporary preview; A/C retained as independent candidates','allModelFurnitureCount':26,'notConstructionDrawings':True}
template=(R/'09_delivery/vr-tour-v05/viewer.template.html').read_text(encoding='utf-8')
template=template.replace('当前方案采用暖白浅木、深木绿蓝，电视墙留白，书柜到顶，餐厅弧背四椅与柔光吊灯。家具保持现位。','当前主模型为v20整合版：胡桃木U餐岛、白色双开门冰箱、圆端餐边柜，以及沙发后高台和接书柜的近端半墙。餐椅暂不摆，办公区从阳台端进入，材质先以B作临时预览。其余家具位置保留。')
(TOUR/'viewer.template.html').write_text(template,encoding='utf-8');(TOUR/'打开360全景漫游.html').write_text(template.replace('__TOUR_DATA__',json.dumps(cfg,ensure_ascii=False,separators=(',',':'))),encoding='utf-8')
publiccfg={**cfg,'panoramas':[{k:v for k,v in s.items() if k!='imageData'} for s in scenes]}
write('09_delivery/vr-tour-v06/漫游机位与来源.json',publiccfg)
write('09_delivery/vr-tour-v06/viewer-manifest.json',{'revision':20,'modelSha256':audit['modelSha256'],'geometrySha256':cfg['geometrySha256'],'panoramas':[r for r in images if r['kind']=='pano'],'viewerSha256':sha(TOUR/'打开360全景漫游.html'),'networkDependencies':0,'previousTourPreserved':'09_delivery/vr-tour-v05/打开360全景漫游.html','browserVisualQA':False})
(TOUR/'使用说明.txt').write_text('双击“打开360全景漫游.html”。鼠标拖动环顾、滚轮缩放，点击区域名切换。四个固定机位，单眼全景，非自由行走或头显实测。图像为同版模型基础上的摄影感概念，外景为示意；家具移动后需重新渲染。原始4K几何球面图另存于07_renders/v20-integrated-native，不将AI原生图冒充4K。',encoding='utf-8')
write('09_delivery/main-integration-v20/图像交付清单.json',images)

css='''*{box-sizing:border-box}body{margin:0;background:#f5f4ee;color:#293e33;font:16px/1.85 "Microsoft YaHei",sans-serif}main{max-width:1220px;padding:40px 28px 80px;margin:auto}h1{font-size:36px;line-height:1.4;font-weight:500}h2{font-size:25px;font-weight:500;margin:0 0 12px}section{background:#fffef9;border:1px solid #d8dfd2;border-radius:18px;padding:28px;margin:28px 0}nav,.links{display:flex;gap:14px 24px;flex-wrap:wrap}a{color:#426b54;text-underline-offset:4px}img{display:block;width:100%;height:auto;border-radius:12px}.hint{color:#71816f;font-size:14px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:22px}table{width:100%;border-collapse:collapse}th,td{padding:12px 10px;text-align:left;border-bottom:1px solid #dee3d5;vertical-align:top}th{font-weight:500}summary{cursor:pointer;color:#57755c}details{margin-top:20px}@media(max-width:650px){main{padding:24px 15px 60px}h1{font-size:28px}section{padding:20px 15px}.pair{grid-template-columns:1fr}table{font-size:13px}th,td{padding:9px 6px}}'''
page=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>餐岛与办公区已整合｜主模型v20</title><style>'+css+'</style><main><nav><a href="../house-v20-preview.html">打开可移动主模型</a><a href="../vr-tour-v06/打开360全景漫游.html">四区360°全景</a><a href="../../06_blender/home-main-v20.blend">完整Blender主模型</a></nav><h1>餐岛与办公区，已经回到同一套房子里</h1><p>已完成餐边柜11与办公区02的实体整合，并同步交互模型、四区摄影感概念图和四点全景。办公材质先用B深木框景作临时预览，A浅木与C奶油仍保留；这不代表替你选定了材质。</p><section><h2>本轮实装清单</h2><table><tr><th>区域</th><th>已并入主模型</th><th>暂拟尺度／使用状态</th></tr><tr><td>餐区</td><td>白色双开门冰箱、齐平餐边柜、胡桃木连续U台面、三横抽、完整上柜及下拉托盘、R100圆端、柜内柔光与纸灯</td><td>柜段2200×800×2750；餐面1800×550×880；内侧取物净深600；餐椅暂不摆</td></tr><tr><td>办公区</td><td>圆角桌、950高沙发背长高台、接到右书柜的暖白近端半墙；阳台端入口敞开</td><td>桌2400×700×750；长高台2400×200×950；半墙长1735、墙身120、压顶200；一屏一椅</td></tr><tr><td>书柜接口</td><td>北端800模块改平移实门的闭合实体形态，避开近端半墙</td><td>门叶／五金仍为设计提案；动态原理保留在独立02，不虚称主模型支持全部机构开合</td></tr><tr><td>旧家具</td><td>原餐桌和四张餐椅退役隐藏留档；其余家具坐标保持</td><td>当前26个可选整组，全部保留长宽高提示与100 mm步进移动</td></tr></table><p class="hint">这次完成已定形方案的整合。早先v20中的空调设备选型、构造节点、柜内容量细分、主卫门位及墙线等未完成事项继续单独跟踪，不以版本号声称全部深化完成。</p></section>']
descriptions={
 'living':('客厅｜把办公区藏在沙发背后','暖白留白电视墙、浅木茶几与米灰沙发延续，深木高台勾出办公边界；近端有实体半墙，阳台端保持入口。'),
 'dining':('餐厅｜餐边柜与餐岛形成一体','冰箱位于客厅端、U形台面之外。置物区、连接臂与餐面统一胡桃木和880高，根部齐平，末端白柜用柔和圆边收住。'),
 'balcony':('阳台｜保留低茶席和开阔视线','低圆茶桌与两把低茶椅沿窗相对，绿植延续至电视侧。办公区的阳台端入口没有新增横台或端柜。'),
 'entry':('门厅｜左侧换鞋临挂，右侧收鞋','钢琴键挂区、换鞋凳、通顶鞋柜与奶黄通长柜继续沿用，入口到新餐岛的连续关系在同版全景中查看。')}
for key,label in labels.items():
 title,desc=descriptions[key];rec=next(r for r in images if r['kind']=='photo' and r['id']==key)
 page.append(f'<section id="{key}"><h2>{title}</h2><p>{desc}</p><a href="photos/{key}.png"><img src="photos/{key}.png" alt="{label}同版摄影感概念" width="{rec["resolution"][0]}" height="{rec["resolution"][1]}"></a><p class="hint">同版模型基础上的摄影感概念，非现场摄影。窗景、光影和细纹理为表现，尺寸以模型与现场为准。</p></section>')
page.append('''<section><h2>实体核对与使用尺度</h2><div class="pair"><div><a href="../../07_renders/v20-integrated-native/office-native.png"><img src="../../07_renders/v20-integrated-native/office-native.png" alt="主模型内办公半墙实体参考"></a><p class="hint">同版原生模型：近端半墙接右书柜，阳台端敞开。</p></div><div><a href="../../07_renders/v20-integrated-native/dining-native.png"><img src="../../07_renders/v20-integrated-native/dining-native.png" alt="主模型内餐岛实体参考"></a><p class="hint">同版原生模型：U形、白冰箱、齐平根部与圆端柜。</p></div></div><p>办公椅后约408仍紧；餐岛外空场约732、厨房端约673，均不等于就座后净距。餐椅本轮不排。所有新增尺寸、板厚、五金、承重与机电条件仍需深化和现场核对。</p><details><summary>查看去顶观察副本与核对记录</summary><a href="../../07_renders/v20-integrated-native/overview-observation.png"><img src="../../07_renders/v20-integrated-native/overview-observation.png" alt="去顶观察副本，完整主模型保留全墙与顶面"></a><p class="hint">这是观察副本。正式主模型保留完整62墙、12玻璃及原有顶面。</p><div class="links"><a href="主模型回读.json">模型重开与尺度核对</a><a href="交互逻辑核对.json">交互逻辑核对</a><a href="图像交付清单.json">图像来源</a><a href="四区表现提示词-首批.json">出图记录</a><a href="四区表现提示词-餐厅.json">餐厅出图记录</a></div></details></section><section><h2>后续设计的回写规则</h2><p>按本轮要求，之后完成的设计默认同步到主模型，保留旧版本和变更记录。尚未定形的多方案先标明候选；如你另行要求仅做独立研究，则以那次要求为准。</p><p>当前可移动模型与全景已为同一几何版本。家具移动后，已烘焙全景不会自动变化；需按新位置重新生成。</p><div class="links"><a href="../office-study-02/办公区半墙与敞开端-三套修正版.html">办公A／B／C候选</a><a href="../sideboard-U-study-11/短连接与长餐台.html">餐区设计来源</a><a href="最终交付核对.json">最终交付核对</a></div></section></main></html>''')
(OUT/'index.html').write_text(''.join(page),encoding='utf-8')
print('V20_DELIVERY_ASSEMBLED',len(images),'images',len(scenes),'spheres')
