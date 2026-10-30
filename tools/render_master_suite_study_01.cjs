const {chromium}=require('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');
(async()=>{const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{const page=await browser.newPage({viewport:{width:1700,height:1370},deviceScaleFactor:1});
 for(const name of ['主卧主卫-布局核对','主卧主卫-斜角入口备选']){
 await page.goto(pathToFileURL('D:/AI-Yang.cn/HomeDesign/09_delivery/master-suite-study-01/'+name+'.svg').href);
 await page.screenshot({path:'D:/AI-Yang.cn/HomeDesign/09_delivery/master-suite-study-01/'+name+'.png'});
 }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
