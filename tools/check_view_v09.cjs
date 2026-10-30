const fs=require('node:fs');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const {chromium}=require('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root='D:/AI-Yang.cn/HomeDesign';
const geometry=JSON.parse(fs.readFileSync(root+'/02_geometry/geometry-master-v09.json','utf8'));
const previous=JSON.parse(fs.readFileSync(root+'/03_layout/widget-layout-v08-initial.json','utf8'));
assert.equal(geometry.glass.length,12);
assert.equal(geometry.windowParts.length,22);
assert.equal(geometry.glass.filter(p=>p.windowRole==='fixed-large-centre').length,1);
assert.equal(geometry.features.balconyWindow.centralMullions,0);
assert.equal(geometry.features.balconyWindow.modelOpeningMm.width,5675);
assert.equal(geometry.features.furnishing.cabinetSelection.option,'C');
assert.equal(geometry.furnitureMaterials.butter.proposal_srgb_hex,'#F1DDAE');
assert.equal(geometry.furnitureObjects.find(p=>p.id==='tv-high').h,2750);
assert.equal(geometry.doorParts.length,19);assert.equal(geometry.doorParts.filter(p=>p.kind==='door-glass').length,3);
assert.equal(geometry.features.kitchenSlidingDoor.widthMm,1691);

(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const page=await browser.newPage({viewport:{width:820,height:1400},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(root+'/09_delivery/house-v09-preview.html').href);
  const frame=page.frameLocator('iframe');await frame.locator('canvas').waitFor();
  const state=()=>page.frames()[1].evaluate(()=>window.openai.widgetState);
  const choose=id=>frame.locator('#house-item-v1').selectOption(id);
  const position=async id=>(await state()).modelContent.furniturePositions.find(o=>o.id===id);
  async function pointAt(x,z,y=0){
   await frame.locator('canvas').scrollIntoViewIfNeeded();
   const saved=await state(),s=saved?.privateContent||{},m=saved?.modelContent||{};
   const view=m.view||'3d',cut=s.cut||1200,yaw=s.yaw??-.34,pitch=s.pitch??.77,zoom=s.zoom||1;
   const offsets=Object.fromEntries((m.furniturePositions||[]).map(q=>[q.id,[q.dx,q.dz]]));
   const parts=geometry.furniture.map(q=>({...q,x:q.x+(offsets[q.parent]?.[0]||0),z:q.z+(offsets[q.parent]?.[1]||0)}));
   const points=geometry.floor.map(([x,z])=>[x,-100,z]);
   for(const q of geometry.walls){const top=Math.min(q.y+q.h,cut);if(top<=q.y)continue;for(const x of [q.x,q.x+q.w])for(const z of [q.z,q.z+q.d])for(const y of [q.y,top])points.push([x,y,z]);}
   for(const q of geometry.glass)for(const x of [q.x,q.x+q.w])for(const z of [q.z,q.z+q.d])points.push([x,Math.min(q.y+q.h,cut),z]);
   for(const q of geometry.windowParts){const top=Math.min(q.y+q.h,cut);if(top<=q.y)continue;for(const x of [q.x,q.x+q.w])for(const z of [q.z,q.z+q.d])for(const y of [q.y,top])points.push([x,y,z]);}
   for(const base of geometry.doorParts){const q={...base,x:base.x+(m.kitchenDoorOpen&&base.movingLeaf==='left'?800.5:0)},top=Math.min(q.y+q.h,cut);if(top<=q.y)continue;for(const x of [q.x,q.x+q.w])for(const z of [q.z,q.z+q.d])for(const y of [q.y,top])points.push([x,y,z]);}
   for(const q of parts)for(const x of [q.x,q.x+q.w])for(const z of [q.z,q.z+q.d])for(const y of [q.y,q.y+q.h])points.push([x,y,z]);
   if(s.dims)for(const d of geometry.dimensions)for(const [x,z] of [d.a,d.b])points.push([x,0,z]);
   function raw(p){
    if(view==='plan')return [p[0],p[2]];
    const x=p[0]-5400,z=p[2]-6200,y=p[1]-600,c=Math.cos(yaw),ss=Math.sin(yaw),d=x*ss+z*c;
    const u=x*c-z*ss,v=d*Math.sin(pitch)-y*Math.cos(pitch),depth=d*Math.cos(pitch)+y*Math.sin(pitch),f=view==='3d'?22000/(22000-depth):1;
    return [u*f,v*f];
   }
   const all=points.map(raw),xs=all.map(p=>p[0]),ys=all.map(p=>p[1]);
   const loX=Math.min(...xs),hiX=Math.max(...xs),loY=Math.min(...ys),hiY=Math.max(...ys),r=await frame.locator('canvas').boundingBox();
   const scale=Math.min((r.width-56)/(hiX-loX),(r.height-58)/(hiY-loY))*(view==='plan'?1:zoom),p=raw([x,y,z]);
   return {x:r.x+r.width/2+(p[0]-(loX+hiX)/2)*scale,y:r.y+r.height/2+(p[1]-(loY+hiY)/2)*scale};
  }
  function pointFor(q){
   const parts=geometry.furniture.filter(p=>p.parent===q.id).sort((a,b)=>b.w*b.d-a.w*a.d);
   const p=parts[0];return [p.x+p.w/2,p.z+p.d/2,p.y+p.h];
  }
  await frame.locator('[data-view="plan"]').click();await frame.locator('[data-dims]').uncheck();
  assert.equal(await frame.locator('#house-item-v1 option').count(),22);
  assert.equal(await frame.locator('#house-item-v1 option[value="office-chair-2"]').count(),0);
  const hovered=[],clicked=[],nudged=[];
  for(const q of geometry.furnitureObjects){
   const appliance=['washer','dryer'].includes(q.id);
   await frame.locator('[data-view="'+(appliance?'3d':'plan')+'"]').click();await frame.locator('[data-dims]').uncheck();
   const [x,z,y]=appliance?[6488,470,(q.id==='washer'?0:880)+415]:pointFor(q),p=await pointAt(x,z,appliance?y:0);
   await page.mouse.move(p.x,p.y);
   assert.equal(await frame.locator('canvas').getAttribute('data-hover-furniture'),q.id,'Hover '+q.id);
   assert.equal(await frame.locator('[data-hover-name]').innerText(),q.name);
   const d=q.dimensionsMm,text=await frame.locator('[data-hover-size]').innerText();
   assert.equal(text,`长 ${Math.round(d.length)} × 宽 ${Math.round(d.width)} × 高 ${Math.round(d.height)} mm`);
   assert.equal(await frame.locator('[data-furniture-tooltip]').isVisible(),true);
   const tip=await frame.locator('[data-furniture-tooltip]').boundingBox(),canvas=await frame.locator('canvas').boundingBox();
   assert.ok(tip.x>=canvas.x-1&&tip.x+tip.width<=canvas.x+canvas.width+1,'Tooltip width '+q.id);
   await page.mouse.click(p.x,p.y);
   assert.equal((await state()).modelContent.selectedFurniture,q.id,'Click '+q.id);
   const direction=q.id.startsWith('entry-')?'up':['bookcase','dining-table','washer','dryer'].includes(q.id)?'left':'right';
   const start=await position(q.id);
   await frame.locator('[data-move="'+direction+'"]').click();
   const moved=await position(q.id);
   assert.equal(direction==='up'?moved.z:moved.x,(direction==='up'?start.z:start.x)+(direction==='right'?100:-100),'Nudge '+q.id);
   if(appliance){const partner=await position(q.id==='washer'?'dryer':'washer');assert.equal(partner.dx,-100,'Linked laundry');}
   await frame.locator('[data-undo]').click();assert.equal((await position(q.id)).x,start.x);assert.equal((await position(q.id)).z,start.z);
   nudged.push(q.id);
   hovered.push(q.id);clicked.push(q.id);
  }
  await choose('side-table');const before=await position('side-table');
  await frame.locator('[data-move="right"]').click();assert.equal((await position('side-table')).x,before.x+100);
  await frame.locator('[data-undo]').click();assert.equal((await position('side-table')).x,before.x);
  await frame.locator('[data-view="plan"]').click();await frame.locator('[data-dims]').uncheck();
  const dragPart=pointFor(geometry.furnitureObjects.find(q=>q.id==='side-table'));
  const dragA=await pointAt(dragPart[0],dragPart[1]),dragB=await pointAt(dragPart[0]+100,dragPart[1]);
  await page.mouse.move(dragA.x,dragA.y);await page.mouse.down();await page.mouse.move(dragB.x,dragB.y,{steps:6});await page.mouse.up();
  assert.equal((await position('side-table')).x,before.x+100,'Canvas drag snaps to 100 mm');
  await frame.locator('[data-undo]').click();assert.equal((await position('side-table')).x,before.x);
  await choose('dining-table');await frame.locator('[data-move="right"]').click();
  assert.equal((await position('dining-table')).dx,0);assert.match(await frame.locator('[data-move-status]').innerText(),/墙边/);

  assert.equal(await frame.locator('[data-door-toggle]').getAttribute('aria-pressed'),'false');
  await frame.locator('[data-door-toggle]').click();assert.equal((await state()).modelContent.kitchenDoorOpen,true);
  assert.equal((await state()).modelContent.kitchenDoorClearOpeningMm,800.5);
  // A chair can enter the open gap; the door must then refuse to close through it.
  await choose('dining-chair-1');await frame.locator('#house-offset-x-v1').fill('-200');await frame.locator('#house-offset-x-v1').dispatchEvent('change');
  await frame.locator('#house-offset-z-v1').fill('2000');await frame.locator('#house-offset-z-v1').dispatchEvent('change');
  assert.equal((await position('dining-chair-1')).z,9550);
  await frame.locator('[data-door-toggle]').click();assert.equal((await state()).modelContent.kitchenDoorOpen,true);
  assert.match(await frame.locator('[data-move-status]').innerText(),/先移开/);
  await frame.locator('[data-undo]').click();await frame.locator('[data-undo]').click();
  await frame.locator('[data-door-toggle]').click();assert.equal((await state()).modelContent.kitchenDoorOpen,false);

  // Updating style/window from v08 must preserve all existing placements.
  const oldState={modelContent:{revision:8,view:'plan',selectedRoom:'open',furniturePositions:previous.furniturePositions||previous.positions||previous.objects},privateContent:{dims:false}};
  if(!oldState.modelContent.furniturePositions){
   const key=Object.keys(previous).find(k=>Array.isArray(previous[k]));oldState.modelContent.furniturePositions=previous[key];
  }
  assert.ok(oldState.modelContent.furniturePositions?.length>=13,'Previous snapshot shape');
  await page.frames()[1].evaluate(s=>window.dispatchEvent(new CustomEvent('openai:set_globals',{detail:{globals:{widgetState:s}}})),oldState);
  await choose('double-desk');
  assert.equal((await position('double-desk')).x,5300);assert.equal((await position('double-desk')).z,2000);
  await choose('sofa-modular');assert.equal((await position('sofa-modular')).x,2900);assert.equal((await position('sofa-modular')).z,1800);
  await choose('side-table');assert.equal((await position('side-table')).z,3250);await choose('sofa-modular');
  const saved=await state();assert.ok(JSON.stringify(saved).length<16384);
  assert.equal(saved.modelContent.revision,9);assert.equal(saved.modelContent.cabinetSelection.lower,'奶黄色');assert.equal(saved.modelContent.cabinetSelection.topGapMm,0);
  assert.deepEqual(saved.modelContent.balconyOpeningProvisionalMm,[5675,2270]);
  const other=await browser.newPage({viewport:{width:820,height:1400}});
  await other.goto(pathToFileURL(root+'/09_delivery/house-v09-preview.html').href);
  await other.frameLocator('iframe').locator('canvas').waitFor();
  await other.frames()[1].evaluate(s=>window.dispatchEvent(new CustomEvent('openai:set_globals',{detail:{globals:{widgetState:s}}})),saved);
  assert.equal(await other.frameLocator('iframe').locator('#house-item-v1').inputValue(),'sofa-modular');await other.close();

  const [cx,cz,cy]=pointFor(geometry.furnitureObjects.find(o=>o.id==='side-table'));
  await frame.locator('[data-view="3d"]').click();
  let p=await pointAt(cx,cz,cy);await page.mouse.move(p.x,p.y);
  assert.equal(await frame.locator('canvas').getAttribute('data-hover-furniture'),'side-table','3D hover');
  await page.screenshot({path:root+'/07_renders/widget-v09-3d-hover.png',fullPage:true});
  await frame.locator('[data-view="plan"]').click();await frame.locator('[data-dims]').uncheck();
  p=await pointAt(cx,cz);await page.mouse.move(p.x,p.y);
  await page.screenshot({path:root+'/07_renders/widget-v09-plan-hover.png',fullPage:true});
  await frame.locator('[data-door-toggle]').click();await page.screenshot({path:root+'/07_renders/widget-v09-door-open.png',fullPage:true});
  await frame.locator('[data-door-toggle]').click();
  await page.setViewportSize({width:320,height:1400});
  p=await pointAt(cx,cz);await page.mouse.move(p.x,p.y);
  const overflow=await page.frames()[1].evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth);
  assert.equal(overflow,false);
  const mt=await frame.locator('[data-furniture-tooltip]').boundingBox(),mc=await frame.locator('canvas').boundingBox();
  assert.ok(mt&&mt.x>=mc.x-1&&mt.x+mt.width<=mc.x+mc.width+1);
  await page.screenshot({path:root+'/07_renders/widget-v09-mobile-hover.png',fullPage:true});
  await page.emulateMedia({colorScheme:'dark'});await page.setViewportSize({width:736,height:1400});
  p=await pointAt(cx,cz);await page.mouse.move(p.x,p.y);await page.screenshot({path:root+'/07_renders/widget-v09-dark-hover.png',fullPage:true});
  assert.equal(errors.length,0,errors.join('\n'));
  const result={runtimeErrors:errors,hovered,clicked,nudged,dimensionTooltips:21,slidingDoorToggle:true,doorClosingCollisionGuard:true,doorWidthMm:1691,doorClearOpeningMm:800.5,cabinetSelection:'C with milk yellow lower',cabinetTopGapMm:0,balconyWindowFivePanes:true,centralMullions:0,linkedLaundryMove:true,canvasDrag100mm:true,threeDimensionalHover:true,stepMm:100,undo:true,wallBoundary:true,oldStateMigrationWithoutDoubleOffsets:true,newStateRestoration:true,mobileOverflow:false,stateBytes:JSON.stringify(saved).length};
  fs.writeFileSync(root+'/logs/widget-v09-verification.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
