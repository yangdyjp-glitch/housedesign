// Check the real homepage, current gallery/model routes, then the current spherical tour.
const fs=require('node:fs'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url');
const {chromium}=require('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root='D:/AI-Yang.cn/HomeDesign';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',args:['--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 try{
  const c=await browser.newContext({viewport:{width:1440,height:900},offline:true}),p=await c.newPage(),errors=[];
  p.on('pageerror',e=>errors.push(String(e)));const home=pathToFileURL(root+'/09_delivery/index.html').href;
  await p.goto(home);await p.locator('.hero-image img').evaluate(im=>im.decode());
  assert.equal(await p.locator('.hero-image img').getAttribute('src'),'vr-tour-v04-预览/living.png');
  assert.equal(await p.locator('.choice-meta').first().innerText().then(t=>t.includes('8K')),false);
  await p.setViewportSize({width:390,height:844});assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  await p.locator('#model-title').click();const f=p.frameLocator('iframe');await f.locator('#house-item-v1').waitFor();assert.equal(await f.locator('#house-item-v1 option').count(),29);assert.ok(p.url().includes('house-v18-preview.html'));
  await p.goto(home);await p.locator('[data-current-gallery]').click();assert.equal(await p.locator('figure img').count(),5);await p.locator('figure img').evaluateAll(imgs=>Promise.all(imgs.map(im=>im.decode())));assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  await p.goto(home);await p.locator('#vr-title').click();await p.waitForFunction(()=>window.getTourState?.().loaded);assert.ok(p.url().includes('vr-tour-v04/'));const s=await p.evaluate(()=>window.getTourState());assert.equal(s.width,1774);assert.equal(s.height,887);assert.deepEqual(errors,[]);
  fs.writeFileSync(root+'/logs/v18-entry-verification.json',JSON.stringify({status:'passed',homepage_opens_current_tour:true,homepage_opens_28_item_model:true,gallery_five_images_decode:true,native_image_dimensions:[s.width,s.height],mobile_390px_no_overflow:true,errors},null,2));console.log('V18_ENTRY_LINKS_VERIFIED');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
