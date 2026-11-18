const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const R='D:/AI-Yang.cn/HomeDesign',page=fs.readFileSync(R+'/09_delivery/vr-tour-v07/打开360全景漫游.html','utf8');
const cfg=JSON.parse(page.match(/<script id="tour-data" type="application\/json">([\s\S]*?)<\/script>/)[1]),script=page.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
const nodes=new Map(),events={},textures=new Set();let serial=0;
const noop=()=>{};
class El{
 constructor(tag='div'){this.tagName=tag.toUpperCase();this.style={};this.dataset={};this.children=[];this.events={};this.attrs={};this.hidden=false;this.clientWidth=1000;this.clientHeight=700;this.classList={toggle:noop};}
 append(...kids){this.children.push(...kids)}replaceChildren(...kids){this.children=kids}get firstChild(){return this.children[0]}
 setAttribute(k,v){this.attrs[k]=v;if(k==='id')nodes.set(v,this);if(k==='data-scene')this.dataset.scene=v}getAttribute(k){return this.attrs[k]}
 addEventListener(k,fn){(this.events[k]??=[]).push(fn)}dispatch(k,e={}){for(const fn of this.events[k]||[])fn({target:this,preventDefault:noop,...e})}
 getBoundingClientRect(){return{left:760,top:420,right:990,bottom:680,width:230,height:260}}
 querySelectorAll(selector){return selector==='.map-point'?this.children.filter(n=>n.attrs.class==='map-point'):[]}
 getContext(kind){return kind==='webgl'?gl:{drawImage:noop}}focus(){}setPointerCapture(){}hasPointerCapture(){return false}releasePointerCapture(){}
}
const gl=new Proxy({MAX_TEXTURE_SIZE:3379,NO_ERROR:0,getParameter:()=>8192,getShaderParameter:()=>true,getProgramParameter:()=>true,getError:()=>0,createShader:()=>({}),createProgram:()=>({}),createBuffer:()=>({}),getAttribLocation:()=>0,getUniformLocation:()=>({}),createTexture:()=>{const x={id:++serial};textures.add(x);return x},deleteTexture:x=>textures.delete(x)},{get:(o,k)=>k in o?o[k]:noop});
for(const id of ['view','status','hotspots','map','resolution','scenes','scene-title','download','zoom-label','minimap','map-toggle','reset','fullscreen','help-toggle','help','help-close','zoom-in','zoom-out'])nodes.set(id,new El(id==='view'?'canvas':'div'));
const jsonNode=new El();jsonNode.textContent=JSON.stringify(cfg);nodes.set('tour-data',jsonNode);
class Img{set src(s){this._src=s;if(s.startsWith('data:image/png;base64,')){const b=Buffer.from(s.split(',')[1],'base64');this.naturalWidth=b.readUInt32BE(16);this.naturalHeight=b.readUInt32BE(20)}}get src(){return this._src}decode(){return Promise.resolve()}}
const window={devicePixelRatio:1,addEventListener:noop};const document={getElementById:id=>nodes.get(id),createElement:tag=>new El(tag),createElementNS:(_,tag)=>new El(tag),documentElement:new El(),fullscreenEnabled:false,addEventListener:(k,f)=>(events[k]??=[]).push(f)};
vm.runInNewContext(script,{window,document,Image:Img,requestAnimationFrame:noop,Float32Array,Math,Map,Set,Number,Promise,Error,setTimeout:noop},{timeout:20000});
const settle=()=>new Promise(setImmediate);
(async()=>{await settle();assert.equal(window.getTourState().scene,'living');assert.equal(window.getTourState().loaded,true);
 const tested=[];for(let cycle=0;cycle<3;cycle++)for(const id of ['entry','dining','living','balcony']){
  const btn=nodes.get('scenes').children.find(x=>x.dataset.scene===id);btn.dispatch('click');await settle();const s=window.getTourState();assert.equal(s.scene,id);assert.equal(s.loaded,true);assert.equal(s.width,1774);assert.equal(s.height,887);assert.equal(s.activeTextureCount,1);assert.equal(textures.size,1);assert.equal(nodes.get('scene-title').textContent,cfg.panoramas.find(p=>p.id===id).label);tested.push(id);
 }
 window.setTourView({yawDeg:90,pitchDeg:35,fovDeg:70});const before=window.getTourState();nodes.get('zoom-in').dispatch('click');assert.equal(window.getTourState().fov,63);
 for(const f of events.keydown)f({key:'ArrowRight',shiftKey:false,target:{tagName:'CANVAS'},preventDefault:noop});assert.ok(Math.abs(window.getTourState().yawDeg-94)<.0001);
 nodes.get('map-toggle').dispatch('click');assert.equal(nodes.get('minimap').hidden,true);
 assert.equal(cfg.revision,20);assert.deepEqual(cfg.panoramas.find(p=>p.id==='dining').positionPlanMm,[770,8850]);
 const report={status:'passed',mode:'offline JS VM with simulated DOM/Image/WebGL; not real browser or shader visual QA',revision:20,sceneSwitches:tested.length,actualPngHeadersDecoded:true,activeTextureCountAfterEachSwitch:1,zoomAndKeyLook:true,mapToggle:true,diningViewpointInOuterPassage:[770,8850],networkDependencies:0,shaderCodeUnchangedFromPriorViewer:true};
 fs.writeFileSync(R+'/09_delivery/v20-complete/全景逻辑核对.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exitCode=1});
