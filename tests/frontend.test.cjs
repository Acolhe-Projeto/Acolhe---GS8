const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../app/static/app.js'), 'utf8');
const visionSource = fs.readFileSync(require('node:path').join(__dirname, '../app/static/vision.js'), 'utf8');
const lesson = {id:'casa',icon:'book',word:'copo',translation:'vaso',title:{pt:'Casa',es:'Casa'},intro:{pt:'Leia',es:'Lee'},question:{pt:'Qual?',es:'Cual?'},options:['Copo','Mesa']};
function deferred(){let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b});return {promise,resolve,reject};}
async function harness({blocked=false,corrupt=false}={}){
 const nodes=new Map();
 function element(){return {children:[],listeners:{},dataset:{},classList:{add(){},remove(){}},textContent:'',value:'',innerHTML:'',disabled:false,append(...x){this.children.push(...x)},replaceChildren(...x){this.children=x},addEventListener(k,f){const previous=this.listeners[k];this.listeners[k]=event=>{if(previous)previous(event);return f(event)}},scrollIntoView(){},querySelector(){return this.button||(this.button=element())}}}
 const get=id=>{if(!nodes.has(id))nodes.set(id,element());return nodes.get(id)};
 const calls=[];const routes=new Map();const values=new Map(corrupt?[['acolhe-completed','{broken']]:[]);
 const storage={getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,v),removeItem:k=>values.delete(k)};
 const context={document:{getElementById:get,createElement:element,querySelectorAll:()=>[],documentElement:{}},navigator:{onLine:true},window:{addEventListener(){}},crypto:{randomUUID:()=>String(calls.length)},Set,console,fetch:async(path,options={})=>{const data=options.body?JSON.parse(options.body):null;calls.push({path,data});let result=routes.has(path)?await routes.get(path)(data):path==='/api/lessons'?[lesson]:path==='/api/sessions'?{id:'a'.repeat(32)}:path==='/api/attempts'?{correct:true}:{};return {ok:true,json:async()=>result}}};
 for(const name of ['localStorage','sessionStorage'])Object.defineProperty(context,name,{get(){if(blocked)throw Error('storage blocked');return storage}});
 vm.createContext(context);vm.runInContext(source,context);vm.runInContext(visionSource,context);
 const tick=()=>new Promise(resolve=>setImmediate(resolve));await tick();
 return {get,calls,routes,values,run:s=>vm.runInContext(s,context),tick};
}
test('corrupt progress storage does not prevent lesson initialization',async()=>{const h=await harness({corrupt:true});assert.equal(h.get('lessons').children.length,1)});
test('blocked storage allows answers in memory',async()=>{const h=await harness({blocked:true});h.run('openLesson(lessons[0])');await h.run('submitAnswer(0)');assert.equal(h.get('progress').textContent,'1 / 1')});
test('language switch ignores old answer and preserves submitted language',async()=>{const h=await harness();const pending=deferred();h.routes.set('/api/attempts',()=>pending.promise);h.run('openLesson(lessons[0])');const request=h.run('submitAnswer(0)');await h.tick();h.get('language').value='es';h.get('language').listeners.change();pending.resolve({correct:true});await request;assert.equal(h.get('feedback').textContent,'');assert.equal(h.calls.find(x=>x.path==='/api/attempts').data.language,'pt')});
test('reopening same lesson ignores old request failures',async()=>{const h=await harness();const pending=deferred();h.routes.set('/api/attempts',()=>pending.promise);h.run('openLesson(lessons[0])');const request=h.run('submitAnswer(0)');await h.tick();h.run('openLesson(lessons[0])');pending.reject(Error('old failure'));await request;assert.equal(h.get('feedback').textContent,'')});
test('erase waits for pending session creation and prevents answer submission',async()=>{const h=await harness();const pending=deferred();h.routes.set('/api/sessions',()=>pending.promise);h.run('openLesson(lessons[0])');const request=h.run('submitAnswer(0)');const erase=h.get('erase').listeners.click();pending.resolve({id:'b'.repeat(32)});await Promise.all([request,erase]);assert.equal(h.calls.filter(x=>x.path==='/api/attempts').length,0);assert.equal(h.calls.find(x=>x.path==='/api/sessions/delete').data.session_id,'b'.repeat(32));assert.equal(h.run('session'),null)});
test('erase waits for posted answer before deleting and cannot resurrect progress',async()=>{const h=await harness();const pending=deferred();h.routes.set('/api/attempts',()=>pending.promise);h.run('openLesson(lessons[0])');const request=h.run('submitAnswer(0)');await h.tick();const erase=h.get('erase').listeners.click();assert.equal(h.calls.filter(x=>x.path==='/api/sessions/delete').length,0);pending.resolve({correct:true});await Promise.all([request,erase]);assert.equal(h.run('completed.size'),0);assert.equal(h.run('session'),null);assert.equal(h.calls.filter(x=>x.path==='/api/sessions/delete').length,1)});
test('overlapping answers share one pending session creation',async()=>{const h=await harness();const pending=deferred();h.routes.set('/api/sessions',()=>pending.promise);h.run('openLesson(lessons[0])');const first=h.run('submitAnswer(0)');h.run('openLesson(lessons[0])');const second=h.run('submitAnswer(0)');pending.resolve({id:'c'.repeat(32)});await Promise.all([first,second]);assert.equal(h.calls.filter(x=>x.path==='/api/sessions').length,1);assert.equal(h.calls.filter(x=>x.path==='/api/attempts').length,1)});
test('failed deletion retains session for retry and releases erase button',async()=>{const h=await harness();h.run('openLesson(lessons[0])');await h.run('submitAnswer(0)');h.routes.set('/api/sessions/delete',()=>Promise.reject(Error('offline')));await h.get('erase').listeners.click();assert.equal(h.run('session'),'a'.repeat(32));assert.equal(h.get('erase').disabled,false);h.routes.delete('/api/sessions/delete');await h.get('erase').listeners.click();assert.equal(h.run('session'),null)});
test('switching view during session creation does not post a stale answer',async()=>{const h=await harness();const pending=deferred();h.routes.set('/api/sessions',()=>pending.promise);h.run('openLesson(lessons[0])');const request=h.run('submitAnswer(0)');h.get('close-lesson').listeners.click();pending.resolve({id:'d'.repeat(32)});await request;assert.equal(h.calls.filter(x=>x.path==='/api/attempts').length,0)});
test('storage write failures do not turn a saved answer into an error',async()=>{const h=await harness();h.run("globalThis.sessionStorage.setItem=()=>{throw Error('quota exceeded')}");h.run('openLesson(lessons[0])');await h.run('submitAnswer(0)');assert.equal(h.get('progress').textContent,'1 / 1');assert.match(h.get('feedback').textContent,/Muito bem/)});

test('expired session clears old progress before a fresh session is created',async()=>{
 const h=await harness();h.run('openLesson(lessons[0])');await h.run('submitAnswer(0)');
 assert.equal(h.get('progress').textContent,'1 / 1');
 h.run('openLesson(lessons[0])');h.routes.set('/api/attempts',()=>Promise.reject(Error('Sessao expirada. Comece novamente.')));
 await h.run('submitAnswer(0)');
 assert.equal(h.run('session'),null);assert.equal(h.get('progress').textContent,'0 / 1');
 assert.equal(h.values.has('acolhe-completed'),false);
 h.routes.delete('/api/attempts');await h.run('submitAnswer(0)');
 assert.equal(h.calls.filter(x=>x.path==='/api/sessions').length,2);assert.equal(h.get('progress').textContent,'1 / 1');
});

test('vision refuses invalid files before sending and clears selection',async()=>{
 const h=await harness();h.get('vision-file').files=[{type:'image/png',size:8*1024*1024+1}];h.get('vision-file').value='object.png';
 await h.get('vision-form').listeners.submit({preventDefault(){}});
 assert.equal(h.calls.filter(x=>x.path==='/api/vision/predict').length,0);
 assert.match(h.get('vision-output').textContent,/8 MiB/);assert.equal(h.get('vision-file').value,'');
});

test('vision renders bilingual vocabulary and releases file after real-response contract',async()=>{
 const h=await harness();h.get('vision-file').files=[{type:'image/jpeg',size:100}];h.get('vision-file').value='object.jpg';
 h.run("fetch=async(path,options)=>{globalThis.visionRequest={path,options};return {ok:true,json:async()=>({detections:[{pt:'copo',es:'vaso',confidence:0.9}]})}} ");
 await h.get('vision-form').listeners.submit({preventDefault(){}});
 assert.equal(h.run('visionRequest.path'),'/api/vision/predict');
 assert.equal(h.run('visionRequest.options.headers["Content-Type"]'),'image/jpeg');
 assert.equal(h.get('vision-output').children[0].textContent,'copo / vaso · 90%');
 assert.equal(h.get('vision-file').value,'');assert.equal(h.get('vision-submit').disabled,false);
});

test('vision reports missing model in selected language and permits retry',async()=>{
 const h=await harness();h.get('language').value='es';h.get('vision-file').files=[{type:'image/png',size:100}];
 h.run('fetch=async()=>({ok:false,status:503,json:async()=>({})})');
 await h.get('vision-form').listeners.submit({preventDefault(){}});
 assert.match(h.get('vision-output').textContent,/Modelo no disponible/);
 assert.equal(h.get('vision-submit').disabled,false);assert.equal(h.get('vision-file').value,'');
});
