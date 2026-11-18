const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const R='D:/AI-Yang.cn/HomeDesign',fragment=fs.readFileSync(R+'/09_delivery/house-v20-fragment.html','utf8');
const geometry=JSON.parse(fragment.match(/<script type="application\/json" id="house-data-v1">([\s\S]*?)<\/script>/)[1]);
let saved=null;const listeners={},map=new Map();
const noop=()=>{};const context2d=new Proxy({measureText:s=>({width:String(s).length*7})},{get:(o,k)=>k in o?o[k]:noop,set:(o,k,v)=>(o[k]=v,true)});
class Element {
 constructor(id=''){this.id=id;this.value='';this.checked=false;this.hidden=false;this.disabled=false;this.style={};this.dataset={};this.attrs={};this.events={};this.children=[];this.textContent='';this.offsetWidth=310;this.offsetHeight=85;this.classList={toggle:noop};}
 addEventListener(k,fn){(this.events[k]??=[]).push(fn)}
 dispatch(k,e={}){for(const fn of this.events[k]||[])fn({target:this,preventDefault:noop,...e})}
 appendChild(e){this.children.push(e);return e}remove(){}
 setAttribute(k,v){this.attrs[k]=v}getAttribute(k){return this.attrs[k]}
 get valueAsNumber(){return Number(this.value)}
 getBoundingClientRect(){return{left:0,top:0,width:736,height:630}}
 getContext(){return context2d}querySelector(s){assert(map.has(s),'Missing selector '+s);return map.get(s)}
 querySelectorAll(s){return s==='[data-view]'?viewButtons:s==='[data-move]'?moveButtons:[]}
 setPointerCapture(){}hasPointerCapture(){return false}releasePointerCapture(){}
}
const root=new Element('house-structure-v1'),canvas=new Element('canvas');map.set('canvas',canvas);
for(const s of ['[data-dims]','[data-removed]','[data-furniture]','#house-cut-v1','[data-height-value]','[data-detail]','[data-height-control]','#house-item-v1','#house-offset-x-v1','#house-offset-z-v1','[data-undo]','[data-move-status]','[data-furniture-tooltip]','[data-hover-name]','[data-hover-size]','[data-hover-note]','[data-door-toggle]','[data-curtain-mode]','[data-bath-door-toggle]','[data-shower-toggle]','[data-removed-legend]','[data-beam-legend]'])map.set(s,new Element(s));
const viewButtons=['3d','ortho','plan'].map(v=>{const e=new Element();e.dataset.view=v;return e}),moveButtons=['left','up','down','right'].map(v=>{const e=new Element();e.dataset.move=v;return e});
const dataNode=new Element();dataNode.textContent=JSON.stringify(geometry);
const win={devicePixelRatio:1,openai:{widgetState:{},setWidgetState:v=>{saved=structuredClone(v);return Promise.resolve()}},addEventListener:(k,f)=>(listeners[k]??=[]).push(f),matchMedia:()=>({addEventListener:noop})};
const sandbox={window:win,document:{getElementById:id=>id==='house-structure-v1'?root:id==='house-data-v1'?dataNode:null,createElement:()=>new Element(),documentElement:new Element()},getComputedStyle:()=>({fontSize:'14px',fontFamily:'sans-serif',color:'rgb(70,80,70)'}),ResizeObserver:class{observe(){}},MutationObserver:class{observe(){}},console,Map,Set,Math,Number,Array,Object,JSON};
vm.runInNewContext(fs.readFileSync(R+'/09_delivery/main-integration-v20/view-runtime.js','utf8'),sandbox,{timeout:20000});
assert.equal(map.get('#house-item-v1').children.length,26);
const choose=id=>{map.get('#house-item-v1').value=id;map.get('#house-item-v1').dispatch('change')};
const nudge=dir=>moveButtons.find(e=>e.dataset.move===dir).dispatch('click');
const positions=()=>saved.modelContent.furniturePositions;
const results=[];
for(const id of ['refrigerator','dining-sideboard-island','office-divider','double-desk','bookcase']){
 choose(id);const before=positions().find(p=>p.id===id),direction=id==='bookcase'?'up':'left';
 nudge(direction);const after=positions().find(p=>p.id===id);
 assert.equal(direction==='up'?after.z:after.x,(direction==='up'?before.z:before.x)-100,id);
 map.get('[data-undo]').dispatch('click');const undo=positions().find(p=>p.id===id);assert.equal(undo.x,before.x);assert.equal(undo.z,before.z);
 results.push({id,clickSelection:true,step100AndUndo:true});
}
// Derive hit points using the independent plan projection equation used by this model view.
const points=geometry.floor.map(([x,z])=>[x,z]);
for(const p of [...geometry.walls,...geometry.glass,...geometry.windowParts,...geometry.doorParts,...geometry.detailParts,...geometry.referenceParts,...geometry.bathParts,...geometry.curtainParts,...geometry.furniture]){
 if(p.kind!=='furniture'&&p.y>=1200)continue;points.push([p.x,p.z],[p.x+p.w,p.z+p.d]);
}
const xs=points.map(p=>p[0]),zs=points.map(p=>p[1]),minX=Math.min(...xs),maxX=Math.max(...xs),minZ=Math.min(...zs),maxZ=Math.max(...zs),scale=Math.min((736-56)/(maxX-minX),(630-58)/(maxZ-minZ));
const pointer=(x,z)=>({clientX:368+(x-(minX+maxX)/2)*scale,clientY:315+(z-(minZ+maxZ)/2)*scale});
const hovers=[];
for(const [id,x,z] of [['refrigerator',2700,6700],['dining-sideboard-island',1420,8130],['office-divider',6100,4500],['double-desk',5700,3550],['bookcase',7020,3500]]){
 canvas.dispatch('pointermove',pointer(x,z));assert.equal(canvas.dataset.hoverFurniture,id,id+' hover at plan point');
 const q=geometry.furnitureObjects.find(q=>q.id===id),d=q.dimensionsMm;assert.equal(map.get('[data-hover-size]').textContent,`长 ${d.length} × 宽 ${d.width} × 高 ${d.height} mm`);
 hovers.push(id);
}
const old=JSON.parse(fs.readFileSync(R+'/03_layout/widget-layout-v19-initial.json','utf8'));
for(let i=0;i<2;i++)for(const fn of listeners['openai:set_globals'])fn({detail:{globals:{widgetState:{modelContent:{revision:19,view:'plan',furniturePositions:old.furniturePositions},privateContent:{dims:false}}}}});
choose('double-desk');assert.equal(saved.modelContent.revision,20);assert.equal(positions().length,26);
for(const p of old.furniturePositions){const now=positions().find(q=>q.id===p.id);if(now){assert.equal(now.x,p.x,p.id);assert.equal(now.z,p.z,p.id)}}
assert.equal(saved.modelContent.diningChairsVisible,0);assert.equal(saved.modelContent.diningTableAgainstWall,false);
const report={status:'passed',mode:'offline JavaScript VM with DOM/canvas stubs; not a browser visual check',furnitureCount:26,selectionMoveUndo:results,hoverDimensions:hovers,revision19MigrationAppliedTwiceWithoutDoubleOffset:true,sourceMeshGeometryParsed:true};
fs.writeFileSync(R+'/09_delivery/main-integration-v20/交互逻辑核对.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));
