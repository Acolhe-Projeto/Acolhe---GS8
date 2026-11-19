const test = require('node:test');
const assert = require('node:assert/strict');
const {pcm16} = require('../app/static/robot.js');
const vm=require('node:vm'),fs=require('node:fs');
const source=fs.readFileSync(require('node:path').join(__dirname,'../app/static/robot.js'),'utf8');
const deferred=()=>{let resolve;const promise=new Promise(r=>{resolve=r});return {promise,resolve};};

async function panel({chat,media,serverBusy=false,robotStatus={}}={}) {
  const nodes=new Map(),requests=[],intervals=[],timers=[];let microphoneCalls=0;
  function element(id='') {
    const node={id,dataset:{},value:'',textContent:'',children:[],listeners:{},disabled:false,
      classList:{toggle(){}},addEventListener(type,listener){this.listeners[type]=listener;},
      append(...children){this.children.push(...children);},replaceChildren(...children){this.children=children;},
      add(child){this.children.push(child);},removeAttribute(){},load(){},pause(){},play:async()=>{},
      remove(){for(const parent of nodes.values())parent.children=parent.children.filter(child=>child!==this);}};
    Object.defineProperty(node,'firstElementChild',{get(){return this.children[0];}});return node;
  }
  const get=id=>{if(!nodes.has(id))nodes.set(id,element(id));return nodes.get(id);};
  const context={document:{getElementById:get,createElement:element,querySelectorAll:()=>[]},
    navigator:{mediaDevices:{getUserMedia:async()=>{microphoneCalls++;return media?await media():{getTracks:()=>[]};}}},
    window:{addEventListener(){}},Option:function(text,value){this.text=text;this.value=value;},
    fetch:async(path,options={})=>{const route=path.split('/').pop();requests.push({route,data:options.body?JSON.parse(options.body):null});
      const result=route==='status'?{ports:[],voice:{busy:serverBusy,whisper_files:true,piper_files:true},robot:{connected:false,sensor:{valid:false},calibrations:{},...robotStatus}}:route==='chat'?await chat():{};
      return {ok:true,json:async()=>result};},
    AbortController,Float32Array,Uint8Array,DataView,ArrayBuffer,Blob,URL:{createObjectURL:()=> 'blob:test',revokeObjectURL(){}},
    atob:s=>Buffer.from(s,'base64').toString('binary'),btoa:s=>Buffer.from(s,'binary').toString('base64'),
    setInterval:f=>{intervals.push(f);},setTimeout:f=>{timers.push(f);return timers.length;},clearTimeout(){},console};
  vm.createContext(context);vm.runInContext(source,context);
  const tick=()=>new Promise(resolve=>setImmediate(resolve));await tick();
  return {get,requests,tick,context,run:s=>vm.runInContext(s,context),microphoneCalls:()=>microphoneCalls};
}

test('audio is downsampled to 16 kHz mono PCM16',()=>{
  const result=pcm16(new Float32Array(48000).fill(.5),48000);
  assert.equal(result.byteLength,32000);
  assert.equal(new DataView(result).getInt16(0,true),16383);
});
test('audio clips samples and bounds recording at fifteen seconds',()=>{
  const result=pcm16(new Float32Array(16000*16).fill(-2),16000);
  assert.equal(result.byteLength,480000);
  assert.equal(new DataView(result).getInt16(0,true),-32768);
});

test('panel never opens microphone automatically and disconnected readings are absent',async()=>{
  const h=await panel();assert.equal(h.microphoneCalls(),0);
  assert.equal(h.get('temperature').textContent,'—');assert.equal(h.get('motor-state').textContent,'Bloqueados');
});

test('practice explains missing calibration and offers setup without sending a pulse',async()=>{
  const h=await panel({robotStatus:{connected:true,port:'COM5',motors_enabled:false},chat:async()=>({transcript:'Oi',answer:'Isso mesmo!',audio_wav:null,mode:'guided_practice',elapsed_seconds:.5,motor_reaction:{sent:false,motor:'arm'}})});
  assert.match(h.get('gesture-guidance').textContent,/0 de 2/);
  h.get('prepare-gestures').listeners.click();
  assert.equal(h.get('calibration').open,true);
  h.get('robot-question').value='Oi';h.get('robot-form').listeners.submit({preventDefault(){}});
  await h.tick();await h.tick();
  assert.match(h.get('latency').textContent,/registrar.*braço direito.*braço esquerdo/i);
  assert.equal(h.requests.some(x=>['pulse','calibrate'].includes(x.route)),false);
});
test('stop suppresses a late answer and sends physical STOP',async()=>{
  const pending=deferred(),h=await panel({chat:()=>pending.promise});
  h.get('robot-question').value='Olá';h.get('robot-form').listeners.submit({preventDefault(){}});await h.tick();
  await h.get('stop').listeners.click();
  pending.resolve({transcript:'Olá',answer:'Resposta antiga',audio_wav:null,model:'test',elapsed_seconds:1});
  await h.tick();await h.tick();
  assert.equal(h.get('messages').children.length,0);
  assert.ok(h.requests.some(x=>x.route==='stop'));
  assert.equal(h.get('send-text').disabled,false);
});
test('microphone denial leaves text input available with a clear error',async()=>{
  const denied=Error('denied');denied.name='NotAllowedError';
  const h=await panel({media:()=>Promise.reject(denied)});
  await h.get('talk').listeners.click();
  assert.match(h.get('robot-error').textContent,/negada/);
  assert.equal(h.get('send-text').disabled,false);
});
test('microphone granted after stop is immediately released',async()=>{
  const pending=deferred();let stopped=0;
  const h=await panel({media:()=>pending.promise});
  const starting=h.get('talk').listeners.click();await h.tick();
  await h.get('stop').listeners.click();
  pending.resolve({getTracks:()=>[{stop(){stopped++;}}]});await starting;
  assert.equal(stopped,1);
  assert.equal(h.requests.filter(x=>x.route==='chat').length,0);
});
test('stop keeps input disabled while cancelled inference is still finishing',async()=>{
  const h=await panel({serverBusy:true});
  await h.get('stop').listeners.click();
  assert.equal(h.get('interaction-state').textContent,'Interrompendo');
  assert.equal(h.get('send-text').disabled,true);
});
test('motor test shows the parameters actually returned by the backend',async()=>{
  const h=await panel({chat:async()=>({transcript:'Mova o braço',answer:'Pulso enviado.',audio_wav:null,mode:'motor_test',elapsed_seconds:.1,motor_test:{motor:'arm',duration_ms:100,motor_control:'direction_only'}})});
  h.get('robot-question').value='Mova o braço';h.get('robot-form').listeners.submit({preventDefault(){}});
  await h.tick();await h.tick();
  assert.match(h.get('latency').textContent,/100 ms/);
  assert.match(h.get('latency').textContent,/acionamento total/);
  assert.doesNotMatch(h.get('latency').textContent,/PWM/);
  assert.match(h.get('latency').textContent,/não confirmado/);
});
