const fs=require('node:fs');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const {chromium}=require('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root='D:/AI-Yang.cn/HomeDesign';
const geometry=JSON.parse(fs.readFileSync(root+'/02_geometry/geometry-master-v14.json','utf8'));
const previous=JSON.parse(fs.readFileSync(root+'/03_layout/widget-layout-v12-initial.json','utf8'));
const previousTen=JSON.parse(fs.readFileSync(root+'/03_layout/widget-layout-v10-user-latest.json','utf8'));
const summarizedInput=JSON.parse(fs.readFileSync(root+'/03_layout/widget-layout-v10-user-latest-v13-input.json','utf8'));
// Reconstructed migration fixture, not a claimed raw current snapshot: historical
// full v10 positions with only the three summarized latest absolute values merged.
const revisionTenFixture=structuredClone(previousTen);
for(const item of summarizedInput.furniturePositions){
 const current=revisionTenFixture.furniturePositions.find(q=>q.id===item.id);
 assert.ok(current);Object.assign(current,item.current);
}
assert.equal(geometry.revision,14);
assert.equal(geometry.furnitureObjects.length,27);
assert.equal(geometry.features.masterSuite.extensionMm,800);
assert.ok(geometry.compatiblePlacementRevisions.includes(12));
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
assert.equal(geometry.detailParts.length,25);assert.equal(geometry.detailParts.filter(p=>p.collidable).length,3);
assert.equal(geometry.features.publicRefinement.palette.wall,'#F3F1EA');
assert.equal(geometry.features.balconyTeaSet.chairCount,2);assert.equal(geometry.features.balconyTeaSet.tableDiameterMm,700);
assert.equal(geometry.features.balconyTeaSet.tableHeightMm,380);assert.equal(geometry.features.balconyTeaSet.chairSeatHeightMm,230);
assert.equal(geometry.features.referenceRefinement.entry.localMirrorClearWidthMm,1254);
assert.equal(geometry.curtainParts.length,45);assert.equal(geometry.furnitureObjects.some(q=>q.id==='entry-return-cabinet'),false);

(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const page=await browser.newPage({viewport:{width:820,height:1400},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(root+'/09_delivery/house-v14-preview.html').href);
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
   for(const q of geometry.detailParts){const top=Math.min(q.y+q.h,cut);if(top<=q.y)continue;for(const x of [q.x,q.x+q.w])for(const z of [q.z,q.z+q.d])for(const y of [q.y,top])points.push([x,y,z]);}
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
  assert.equal(await frame.locator('#house-item-v1 option').count(),28);
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
   if(q.id==='entry-shoe-cabinet'){const note=await frame.locator('[data-hover-note]').innerText();assert.match(note,/一字柜/);assert.match(note,/1254/);assert.doesNotMatch(note,/盲角|L形/);}
   if(q.id==='tv-low')assert.match(await frame.locator('[data-hover-note]').innerText(),/离地180/);
   const tip=await frame.locator('[data-furniture-tooltip]').boundingBox(),canvas=await frame.locator('canvas').boundingBox();
   assert.ok(tip.x>=canvas.x-1&&tip.x+tip.width<=canvas.x+canvas.width+1,'Tooltip width '+q.id);
   await page.mouse.click(p.x,p.y);
   assert.equal((await state()).modelContent.selectedFurniture,q.id,'Click '+q.id);
   const direction=q.id.startsWith('entry-')?'up':['bookcase','dining-table','washer','dryer','master-bed','master-vanity'].includes(q.id)?'left':'right';
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

  // The closed flush guest-room leaf also blocks a chair crossing its opening.
  await choose('office-chair-1');await frame.locator('#house-offset-x-v1').fill('-700');await frame.locator('#house-offset-x-v1').dispatchEvent('change');
  await frame.locator('#house-offset-z-v1').fill('3800');await frame.locator('#house-offset-z-v1').dispatchEvent('change');
  assert.match(await frame.locator('[data-move-status]').innerText(),/偏移/);
  assert.ok((await position('office-chair-1')).z<6145-560);
  await frame.locator('[data-move="down"]').click();assert.match(await frame.locator('[data-move-status]').innerText(),/房门边/);
  await frame.locator('[data-undo]').click();await frame.locator('[data-undo]').click();

  // Unmodified v12 positions migrate onto the v14 baseline without reversing
  // the latest three already-baked changes.
  const oldState={modelContent:{revision:12,view:'plan',selectedRoom:'open',furniturePositions:previous.furniturePositions||previous.positions||previous.objects},privateContent:{dims:false}};
  if(!oldState.modelContent.furniturePositions){
   const key=Object.keys(previous).find(k=>Array.isArray(previous[k]));oldState.modelContent.furniturePositions=previous[key];
  }
  assert.ok(oldState.modelContent.furniturePositions?.length>=13,'Previous snapshot shape');
  await page.frames()[1].evaluate(s=>window.dispatchEvent(new CustomEvent('openai:set_globals',{detail:{globals:{widgetState:s}}})),oldState);
  await choose('double-desk');
  assert.equal((await position('double-desk')).x,5300);assert.equal((await position('double-desk')).z,2000);
  await choose('sofa-modular');assert.equal((await position('sofa-modular')).x,3100);assert.equal((await position('sofa-modular')).z,1300);
  assert.equal((await position('sofa-modular')).dx,0);assert.equal((await position('sofa-modular')).dz,0);
  await choose('side-table');assert.equal((await position('side-table')).z,2650);
  await choose('ottoman');assert.equal((await position('ottoman')).z,4350);
  const legacyState={modelContent:{revision:10,view:'plan',selectedRoom:'open',furniturePositions:revisionTenFixture.furniturePositions},privateContent:{dims:false}};
  // Restoring the same received legacy layout twice must remain idempotent.
  for(let restore=0;restore<2;restore++){
   await page.frames()[1].evaluate(s=>window.dispatchEvent(new CustomEvent('openai:set_globals',{detail:{globals:{widgetState:s}}})),legacyState);
   for(const item of summarizedInput.furniturePositions){
    await choose(item.id);const got=await position(item.id);
    assert.equal(got.x,item.current.x);assert.equal(got.z,item.current.z);
    assert.equal(got.dx,0);assert.equal(got.dz,0);
   }
   assert.equal((await state()).modelContent.furniturePositions.length,27);
   assert.equal((await state()).modelContent.furniturePositions.some(q=>q.id==='entry-return-cabinet'),false);
   for(const id of ['entry-shoe-cabinet','balcony-tea-table','balcony-tea-chair-1','balcony-tea-chair-2']){
    const expected=geometry.furnitureObjects.find(q=>q.id===id),got=await position(id);
    assert.equal(got.x,expected.x);assert.equal(got.z,expected.z);
   }
  }
  await choose('sofa-modular');
  for(const mode of ['privacy','sheer','open']){await frame.locator('select[data-curtain-mode]').selectOption(mode);assert.equal((await state()).modelContent.curtainMode,mode);assert.equal(await frame.locator('canvas').getAttribute('data-curtain-mode'),mode);}
  await choose('balcony-tea-table');await frame.locator('#house-offset-z-v1').fill('-200');await frame.locator('#house-offset-z-v1').dispatchEvent('change');assert.equal((await position('balcony-tea-table')).z,170);await frame.locator('[data-move="up"]').click();assert.equal((await position('balcony-tea-table')).z,170);assert.match(await frame.locator('[data-move-status]').innerText(),/窗帘活动区/);await frame.locator('[data-undo]').click();assert.equal((await position('balcony-tea-table')).z,270);await choose('sofa-modular');
  const saved=await state();assert.ok(JSON.stringify(saved).length<16384);
  assert.equal(saved.modelContent.revision,14);assert.equal(saved.modelContent.cabinetSelection.lower,'奶黄色');assert.equal(saved.modelContent.cabinetSelection.topGapMm,0);
  assert.equal(saved.modelContent.masterSuiteApplied,true);
  await frame.locator('[data-bath-door-toggle]').click();assert.equal((await state()).modelContent.masterBathDoorOpen,true);
  await frame.locator('[data-bath-door-toggle]').click();assert.equal((await state()).modelContent.masterBathDoorOpen,false);
  await frame.locator('[data-shower-toggle]').click();assert.equal((await state()).modelContent.masterShowerOpen,true);
  await frame.locator('[data-shower-toggle]').click();assert.equal((await state()).modelContent.masterShowerOpen,false);
  await choose('master-toilet');await frame.locator('#house-offset-z-v1').fill('1000');await frame.locator('#house-offset-z-v1').dispatchEvent('change');
  assert.equal((await position('master-toilet')).z,5550,'Shower screen blocks fixture crossing');
  await frame.locator('[data-move="down"]').click();assert.match(await frame.locator('[data-move-status]').innerText(),/淋浴隔断/);
  await frame.locator('[data-undo]').click();assert.equal((await position('master-toilet')).z,5350);
  const v13=JSON.parse(fs.readFileSync(root+'/02_geometry/geometry-master-v13.json','utf8'));
  const v13state={modelContent:{revision:13,view:'plan',furniturePositions:v13.furnitureObjects.map(q=>({id:q.id,x:q.x,z:q.z,dx:0,dz:0}))},privateContent:{dims:false}};
  await page.frames()[1].evaluate(s=>window.dispatchEvent(new CustomEvent('openai:set_globals',{detail:{globals:{widgetState:s}}})),v13state);
  await choose('sofa-modular');assert.equal((await position('sofa-modular')).z,1300);
  assert.deepEqual(saved.modelContent.balconyOpeningProvisionalMm,[5675,2270]);
  const other=await browser.newPage({viewport:{width:820,height:1400}});
  await other.goto(pathToFileURL(root+'/09_delivery/house-v14-preview.html').href);
  await other.frameLocator('iframe').locator('canvas').waitFor();
  await other.frames()[1].evaluate(s=>window.dispatchEvent(new CustomEvent('openai:set_globals',{detail:{globals:{widgetState:s}}})),saved);
  assert.equal(await other.frameLocator('iframe').locator('#house-item-v1').inputValue(),'sofa-modular');await other.close();

  const [cx,cz,cy]=pointFor(geometry.furnitureObjects.find(o=>o.id==='side-table'));
  await frame.locator('[data-view="3d"]').click();
  let p=await pointAt(cx,cz,cy);await page.mouse.move(p.x,p.y);
  assert.equal(await frame.locator('canvas').getAttribute('data-hover-furniture'),'side-table','3D hover');
  await page.screenshot({path:root+'/07_renders/widget-v14-3d-hover.png',fullPage:true});
  await frame.locator('[data-view="plan"]').click();await frame.locator('[data-dims]').uncheck();
  p=await pointAt(cx,cz);await page.mouse.move(p.x,p.y);
  await page.screenshot({path:root+'/07_renders/widget-v14-plan-hover.png',fullPage:true});
  await frame.locator('[data-door-toggle]').click();await page.screenshot({path:root+'/07_renders/widget-v14-door-open.png',fullPage:true});
  await frame.locator('[data-door-toggle]').click();
  await page.setViewportSize({width:320,height:1400});
  p=await pointAt(cx,cz);await page.mouse.move(p.x,p.y);
  const overflow=await page.frames()[1].evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth);
  assert.equal(overflow,false);
  const mt=await frame.locator('[data-furniture-tooltip]').boundingBox(),mc=await frame.locator('canvas').boundingBox();
  assert.ok(mt&&mt.x>=mc.x-1&&mt.x+mt.width<=mc.x+mc.width+1);
  await page.screenshot({path:root+'/07_renders/widget-v14-mobile-hover.png',fullPage:true});
  await page.emulateMedia({colorScheme:'dark'});await page.setViewportSize({width:736,height:1400});
  p=await pointAt(cx,cz);await page.mouse.move(p.x,p.y);await page.screenshot({path:root+'/07_renders/widget-v14-dark-hover.png',fullPage:true});
  assert.equal(errors.length,0,errors.join('\n'));
  const result={revision:14,runtimeErrors:errors,hovered,clicked,nudged,dimensionTooltips:27,masterBathDoorToggle:true,masterShowerToggle:true,balconyTeaFurniture:3,entryLocalClearWidthMm:1254,curtainModes:3,curtainActivityZoneGuard:true,latestUserPlacementsBakedWithoutDoubleOffsets:true,slidingDoorToggle:true,doorClosingCollisionGuard:true,publicDetailParts:25,publicDoorLeaves:3,doorWidthMm:1691,doorClearOpeningMm:800.5,cabinetSelection:'C with milk yellow lower',cabinetTopGapMm:0,balconyWindowFivePanes:true,centralMullions:0,linkedLaundryMove:true,canvasDrag100mm:true,threeDimensionalHover:true,stepMm:100,undo:true,wallBoundary:true,oldStateMigrationWithoutDoubleOffsets:true,revision12StateMigration:true,revision10SummarizedFixtureTwiceIdempotent:true,removedEntryLegNotReintroduced:true,currentEntryAndTeaPositionsPreserved:true,newStateRestoration:true,mobileOverflow:false,stateBytes:JSON.stringify(saved).length};
  fs.writeFileSync(root+'/logs/widget-v14-verification.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
