const {chromium}=require('C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {pathToFileURL}=require('node:url');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{const page=await browser.newPage({viewport:{width:1600,height:1270},deviceScaleFactor:1});
 await page.goto(pathToFileURL('D:/AI-Yang.cn/HomeDesign/09_delivery/v10主卫门位研究.svg').href);
 await page.screenshot({path:'D:/AI-Yang.cn/HomeDesign/09_delivery/v10主卫门位研究.png'});
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
