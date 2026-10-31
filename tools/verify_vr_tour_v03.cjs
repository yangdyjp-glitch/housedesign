// Offline end-to-end verification. Pass --html=<file> for calibration or a staged build.
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const {pathToFileURL}=require('node:url');
const {chromium}=require('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root='D:/AI-Yang.cn/HomeDesign';
const input=process.argv.find(x=>x.startsWith('--html='));
const html=input?input.slice(7):root+'/09_delivery/vr-tour-v03/打开360全景漫游.html';
const config=JSON.parse(fs.readFileSync(path.join(path.dirname(html),'漫游机位与来源.json'),'utf8'));
const initial=id=>config.panoramas.find(s=>s.id===id);
const logArgument=process.argv.find(x=>x.startsWith('--log='));
const log=logArgument?logArgument.slice(6):root+'/logs/vr-tour-v03-verification.json';
const stamp=path.basename(path.dirname(html));
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const wait=p=>p.waitForFunction(()=>window.getTourState?.().loaded,{timeout:60000});
const state=p=>p.evaluate(()=>window.getTourState());
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const report={status:'running',html,htmlSha256:hash(fs.readFileSync(html)),calibrationOnly:html.includes('calibration'),renderQuality:html.includes('draft')?'draft':html.includes('partial')?'partial':'final',modelRevision:config.revision,modelSha256:config.modelSha256,tests:[],screenshots:[],headsetTested:false,physicalPhoneTested:false,mobileTestMethod:'Chrome touch-device emulation via Playwright/CDP'};
 const errors=[],requests=[];
 try{
  const context=await browser.newContext({viewport:{width:1440,height:900},deviceScaleFactor:1,offline:true});
  const page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>requests.push(r.url()));
  await page.goto(pathToFileURL(html).href,{timeout:60000});await wait(page);
  let s=await state(page);const firstScene=initial(s.scene),firstYaw=firstScene.initialYawDeg||0,firstPitch=firstScene.initialPitchDeg||0,firstFov=firstScene.initialFovDeg||75;assert.equal(s.webgl,true);assert.equal(s.perspectiveProjection,true);assert.equal(s.networkDependencies,0);assert.deepEqual(s.scenes.toSorted(),['balcony','dining','entry','living']);assert.equal(s.width,s.height*2);assert.ok(s.width>=(config.minimumPanoramaWidth||2048));report.tests.push('Local file opens offline; spherical WebGL projection; 2:1 image decode');
  const first=hash(await page.locator('canvas').screenshot());
  await page.locator('canvas').hover();await page.mouse.move(650,450);await page.mouse.down();await page.mouse.move(1020,540,{steps:12});await page.mouse.up();
  await page.waitForTimeout(80);s=await state(page);assert.ok(Math.abs(s.yawDeg-firstYaw)>15);assert.ok(Math.abs(s.pitchDeg-firstPitch)>2);const changed=hash(await page.locator('canvas').screenshot());assert.notEqual(changed,first);report.tests.push('Mouse drag changes yaw/pitch and rendered pixel output');
  const fov=s.fov;await page.mouse.wheel(0,-220);assert.ok((await state(page)).fov<fov);await page.locator('#reset').click();assert.equal((await state(page)).fov,firstFov);report.tests.push('Wheel zoom and reset');
  await page.locator('canvas').focus();await page.keyboard.press('ArrowRight');await page.keyboard.press('ArrowUp');s=await state(page);assert.ok(Math.abs(s.yawDeg-firstYaw)>3.9);assert.ok(s.pitchDeg>firstPitch);await page.keyboard.press('Home');assert.ok(Math.abs((await state(page)).yawDeg-firstYaw)<.0001);await page.keyboard.press('+');assert.equal((await state(page)).fov,firstFov-5);await page.keyboard.press('-');assert.equal((await state(page)).fov,firstFov);report.tests.push('Arrow keys, Home and keyboard zoom');
  const decoded=[];for(const id of ['dining','entry','living','balcony']){await page.locator(`.scene[data-scene="${id}"]`).click();await wait(page);s=await state(page);assert.equal(s.scene,id);assert.equal(s.width,s.height*2);assert.equal(await page.locator(`.scene[data-scene="${id}"]`).getAttribute('aria-pressed'),'true');assert.equal(await page.locator('#scene-title').innerText(),{dining:'餐厅',entry:'门厅',living:'客厅',balcony:'阳台'}[id]);decoded.push({id,width:s.width,height:s.height,textureWidth:s.textureWidth,textureHeight:s.textureHeight});const shot=root+`/logs/${stamp}-${id}-perspective.png`;await page.locator('canvas').screenshot();const bitmap=await page.evaluate(()=>document.getElementById('view').toDataURL('image/png'));fs.writeFileSync(shot,Buffer.from(bitmap.split(',')[1],'base64'));report.screenshots.push(shot);}
  report.decodedImages=decoded;report.tests.push('All four model image scenes decode, upload and switch');
  await page.locator('#map-toggle').click();assert.equal(await page.locator('#minimap').isVisible(),false);await page.locator('#map-toggle').click();await page.locator('.map-point[data-scene="living"]').click();await wait(page);assert.equal((await state(page)).scene,'living');report.tests.push('Map toggles and switches scene');
  // Find a hotspot by turning through a full revolution, then use the real button.
  let spot=page.locator('.spot:not([hidden])').first();for(let i=0;i<40&&!(await spot.count());i++){await page.locator('canvas').focus();await page.keyboard.press('Shift+ArrowRight');await page.waitForTimeout(20);}
  assert.ok(await spot.count(),'At least one walk-through hotspot is visible');const target=await spot.getAttribute('data-target');await spot.click();await wait(page);assert.equal((await state(page)).scene,target);report.tests.push('Projected hotspot uses world direction and switches observation point');
  await page.locator('.scene[data-scene="living"]').click();await wait(page);await page.locator('#reset').click();const desktopShot=root+`/logs/${stamp}-desktop.png`;await page.screenshot({path:desktopShot});report.screenshots.push(desktopShot);
  await page.locator('#help-toggle').click();assert.equal(await page.locator('#help').isVisible(),true);await page.locator('#help-close').click();assert.equal(await page.locator('#help').isVisible(),false);report.tests.push('Chinese usage help opens/closes');
  // Actual touch events, not a state-mutating test hook.
  const mobile=await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true,offline:true});
  const mp=await mobile.newPage();mp.on('pageerror',e=>errors.push(String(e)));mp.on('request',r=>requests.push(r.url()));await mp.goto(pathToFileURL(html).href,{timeout:60000});await wait(mp);const cdp=await mobile.newCDPSession(mp);
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:140,y:440,id:0}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:270,y:510,id:0}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});assert.ok(Math.abs((await state(mp)).yawDeg-firstYaw)>5);report.tests.push('Mobile single-finger spherical rotation');
  await mp.locator('#reset').tap();await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:130,y:420,id:0},{x:240,y:420,id:1}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:120,y:420,id:0},{x:250,y:420,id:1}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:80,y:420,id:0},{x:290,y:420,id:1}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});assert.ok((await state(mp)).fov<firstFov-5);report.tests.push('Mobile two-finger pinch changes field of view');
  await mp.locator('.scene[data-scene="entry"]').tap();await wait(mp);assert.equal((await state(mp)).scene,'entry');await mp.locator('#reset').tap();assert.equal(await mp.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);const mshot=root+`/logs/${stamp}-mobile.png`;await mp.screenshot({path:mshot});report.screenshots.push(mshot);report.tests.push('Mobile scene switch, reset and no horizontal overflow at 390px');
  await mp.setViewportSize({width:320,height:700});assert.equal(await mp.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);report.tests.push('320px viewport has no horizontal overflow');
  // Maximum pitch, seam wrapping and repeated scene changes exercise full sphere.
  await page.locator('canvas').focus();for(let i=0;i<10;i++)await page.keyboard.press('Shift+ArrowUp');assert.ok((await state(page)).pitchDeg>85);for(let i=0;i<20;i++)await page.keyboard.press('Shift+ArrowDown');assert.ok((await state(page)).pitchDeg<-85);for(let i=0;i<40;i++)await page.keyboard.press('Shift+ArrowRight');s=await state(page);assert.ok(s.yawDeg>=-180&&s.yawDeg<=180);report.tests.push('Zenith/nadir and continuous 360-degree yaw wrap');
  if(report.renderQuality==='final'&&!report.calibrationOnly){
   const previews=root+'/09_delivery/vr-tour-v03-预览';fs.mkdirSync(previews,{recursive:true});
   for(const id of ['living','dining','balcony','entry'])fs.copyFileSync(root+`/logs/${stamp}-${id}-perspective.png`,previews+'/'+id+'.png');
   report.previewFolder=previews;
  }
  if(!report.calibrationOnly&&(report.renderQuality==='final'||(report.renderQuality==='partial'&&initial('living').imageWidth>=8192))){
   await page.setViewportSize({width:900,height:600});await page.locator('.scene[data-scene="living"]').click();await wait(page);
   report.sphereReviewAngles=[];
   for(const shot of [{name:'seam-left',yawDeg:179,pitchDeg:0},{name:'seam-right',yawDeg:-179,pitchDeg:0},{name:'zenith',yawDeg:0,pitchDeg:89},{name:'nadir',yawDeg:0,pitchDeg:-89}]){
    const beforeFrame=(await state(page)).frame;await page.evaluate(v=>window.setTourView({...v,fovDeg:60}),shot);await page.waitForFunction(n=>window.getTourState().frame>n,beforeFrame);const bitmap=await page.evaluate(()=>document.getElementById('view').toDataURL('image/png')),file=root+`/logs/vr-tour-v03-final-${shot.name}.png`;fs.writeFileSync(file,Buffer.from(bitmap.split(',')[1],'base64'));report.sphereReviewAngles.push({...shot,file});
   }
   report.tests.push('Native-resolution living view exports both 360 seam sides, zenith and nadir for visual review');
  }
  assert.equal(requests.some(url=>/^https?:/i.test(url)),false);assert.deepEqual(errors,[]);report.tests.push('No network requests, CDN or page errors under browser offline mode');
  report.requests=requests.map(x=>x.slice(0,180));report.errors=errors;report.webglState=await state(page);
  await mobile.close();await context.close();
  // Exercise the fallback path on a simulated 1024-pixel GPU texture limit.
  const limited=await browser.newContext({viewport:{width:1000,height:700},offline:true});
  await limited.addInitScript(()=>{const original=WebGLRenderingContext.prototype.getParameter;WebGLRenderingContext.prototype.getParameter=function(p){const value=original.call(this,p);return p===0x0D33?Math.min(1024,value):value;};});
  const lp=await limited.newPage();await lp.goto(pathToFileURL(html).href,{timeout:60000});await wait(lp);const limitedState=await state(lp);assert.equal(limitedState.textureWidth,Math.min(limitedState.width,1024));assert.equal(limitedState.textureWidth,limitedState.textureHeight*2);assert.equal(limitedState.error,null);report.textureLimitSimulation={reportedLimit:1024,originalWidth:limitedState.width,uploadedWidth:limitedState.textureWidth,uploadedHeight:limitedState.textureHeight};report.tests.push('Simulated 1024px GPU limit downsamples display texture, preserving 2:1 and original download');await limited.close();
  report.status='passed';
 }catch(e){report.status='failed';report.error=String(e.stack||e);throw e;}
 finally{fs.writeFileSync(log,JSON.stringify(report,null,2));await browser.close();}
 console.log(JSON.stringify({status:'VR_TOUR_VIEWER_VERIFIED',tests:report.tests.length,calibrationOnly:report.calibrationOnly,report:log}));
})().catch(e=>{console.error(e);process.exitCode=1;});
