/* Standalone Acolhe panel; no Talos code, no persistent conversation storage. */
'use strict';
function pcm16(samples, sampleRate) {
  const ratio=sampleRate/16000, count=Math.min(240000,Math.floor(samples.length/ratio));
  const buffer=new ArrayBuffer(count*2), view=new DataView(buffer);
  for(let i=0;i<count;i++) {
    const start=Math.floor(i*ratio),end=Math.min(samples.length,Math.max(start+1,Math.floor((i+1)*ratio)));
    let total=0;for(let j=start;j<end;j++)total+=samples[j];
    const value=Math.max(-1,Math.min(1,total/(end-start)));
    view.setInt16(i*2,value<0?value*32768:value*32767,true);
  }
  return buffer;
}
if(typeof module!=='undefined')module.exports={pcm16};
if(typeof document!=='undefined') {
  const el=id=>document.getElementById(id), player=el('voice-player');
  let recording=null,busy=false,recordingPending=false,request=null,epoch=0,audioURL=null,polling=false,lastStatus=null;
  let tested=null, latestActivity=null,stopping=false;
  const state=value=>{el('interaction-state').textContent=value;el('conversa').dataset.state=value;};
  const error=message=>{el('robot-error').textContent=message||'';};
  async function api(route,data,signal) {
    const response=await fetch('/api/robot/'+route,{method:data===undefined?'GET':'POST',headers:data===undefined?{}:{'Content-Type':'application/json'},body:data===undefined?undefined:JSON.stringify(data),signal});
    const result=await response.json();
    if(!response.ok)throw Error(result.error||'Serviço indisponível.');
    return result;
  }
  function buttons() {
    el('talk').disabled=(busy&&!recording)||recordingPending;
    el('talk').textContent=recording?'■ Encerrar pergunta':'● Falar com Acolhe';
    el('send-text').disabled=busy||!!recording||recordingPending;
    el('clear-chat').disabled=busy||!!recording||recordingPending;
    document.querySelectorAll('[data-question], #heat-question').forEach(button=>{button.disabled=busy||!!recording||recordingPending;});
  }
  function addMessage(text,user=false) {
    const message=document.createElement('p');message.className='message'+(user?' user':'');
    const label=document.createElement('small');label.textContent=user?'VOCÊ':'ACOLHE';
    const content=document.createElement('span');content.textContent=text;
    message.append(label,content);el('messages').append(message);
    while(el('messages').children.length>6)el('messages').firstElementChild.remove();
    el('messages').scrollTop=el('messages').scrollHeight;
  }
  function resetPlayer() {
    player.pause();player.removeAttribute('src');player.load();
    if(audioURL)URL.revokeObjectURL(audioURL);audioURL=null;
  }
  async function send(data) {
    if(busy||recording||recordingPending)return;
    const own=++epoch;busy=true;buttons();error('');resetPlayer();state('Pensando');
    request=new AbortController();
    try {
      const result=await api('chat',data,request.signal);
      if(own!==epoch)return;
      addMessage(result.transcript,true);addMessage(result.answer);
      el('latency').textContent=result.motor_test?`Teste enviado: ${result.motor_test.motor==='arm'?'braço esquerdo':'braço direito'} · ${result.motor_test.duration_ms} ms · acionamento total · movimento ainda não confirmado`:`Resposta preparada em ${result.elapsed_seconds} s · ${result.model||'Resposta de escopo'}`;
      if(result.mode==='guided_practice')el('latency').textContent=`Atividade guiada · ${result.elapsed_seconds} s`+(result.motor_reaction?(result.motor_reaction.sent?` · gesto enviado: ${result.motor_reaction.motor==='arm'?'braço esquerdo':'braço direito'}`:' · sem gesto: confira conexão, calibração e intervalo entre movimentos'):'');
      if(result.motor_reaction?.sent===false&&lastStatus?.robot.connected&&!lastStatus.robot.motors_enabled)el('latency').textContent='Acerto ou tentativa reconhecidos. Para mover, falta registrar o movimento do braço direito e do braço esquerdo em Preparar gestos do treino.';
      el('robot-question').value='';
      if(result.errors?.length)error(result.errors.map(x=>x.message).join(' '));
      if(result.audio_wav) {
        const bytes=Uint8Array.from(atob(result.audio_wav),c=>c.charCodeAt(0));
        audioURL=URL.createObjectURL(new Blob([bytes],{type:'audio/wav'}));player.src=audioURL;
        try {await player.play();state('Falando');await api('state',{state:'SPEAK'});}catch {state('Pronto');error('A resposta está pronta. Use o controle de áudio para ouvi-la.');}
      } else state('Pronto');
    } catch(exc) {if(own===epoch&&exc.name!=='AbortError'){state('Indisponível');error(exc.message);}}
    finally {if(own===epoch){busy=false;request=null;buttons();}}
  }
  async function disposeRecording() {
    if(!recording)return null;
    const capture=recording;recording=null;clearTimeout(capture.timer);
    capture.processor.onaudioprocess=null;capture.processor.disconnect();capture.source.disconnect();capture.mute.disconnect();
    capture.stream.getTracks().forEach(track=>track.stop());
    await capture.context.close();buttons();return capture;
  }
  async function finishRecording() {
    const own=epoch;
    const capture=await disposeRecording();if(!capture||own!==epoch)return;
    const count=capture.chunks.reduce((sum,x)=>sum+x.length,0),samples=new Float32Array(count);
    let offset=0;for(const chunk of capture.chunks){samples.set(chunk,offset);offset+=chunk.length;}
    const bytes=new Uint8Array(pcm16(samples,capture.sampleRate));
    if(bytes.length<3200){state('Pronto');error('Fale por um pouco mais de tempo e tente novamente.');return;}
    let binary='';for(let i=0;i<bytes.length;i+=8192)binary+=String.fromCharCode(...bytes.subarray(i,i+8192));
    await send({pcm16:btoa(binary)});
  }
  async function startRecording() {
    if(busy||recordingPending)return;
    if(!navigator.mediaDevices?.getUserMedia){error('Microfone indisponível. Abra o Acolhe em localhost e use um navegador atualizado.');return;}
    const own=++epoch;recordingPending=true;buttons();error('');resetPlayer();
    let stream,context;
    try {
      stream=await navigator.mediaDevices.getUserMedia({audio:{channelCount:1,echoCancellation:true,noiseSuppression:true},video:false});
      if(own!==epoch){stream.getTracks().forEach(track=>track.stop());return;}
      context=new AudioContext();await context.resume();
      if(own!==epoch){stream.getTracks().forEach(track=>track.stop());await context.close();return;}
      const source=context.createMediaStreamSource(stream),processor=context.createScriptProcessor(4096,1,1),mute=context.createGain();mute.gain.value=0;
      recording={stream,context,source,processor,mute,chunks:[],sampleRate:context.sampleRate,timer:setTimeout(finishRecording,15000)};
      processor.onaudioprocess=event=>{if(recording)recording.chunks.push(new Float32Array(event.inputBuffer.getChannelData(0)));};
      source.connect(processor);processor.connect(mute);mute.connect(context.destination);
      state('Ouvindo');api('state',{state:'LISTEN'}).catch(()=>{});
    } catch(exc) {
      if(stream)stream.getTracks().forEach(track=>track.stop());if(context&&context.state!=='closed')await context.close();
      if(own===epoch){state('Indisponível');error(exc.name==='NotAllowedError'?'Permissão de microfone negada. Você pode escrever a pergunta ou liberar o microfone no navegador.':exc.message);}
    } finally {recordingPending=false;buttons();}
  }
  async function refresh() {
    if(polling)return;polling=true;
    try {
      const status=await api('status');lastStatus=status;
      if(stopping&&!status.voice.busy){stopping=false;busy=false;state('Pronto');buttons();}
      const robot=status.robot,sensor=robot.sensor,select=el('serial-port'),selected=select.value;
      const ports=JSON.stringify(status.ports);
      if(select.dataset.ports!==ports){select.replaceChildren(new Option('Selecione uma porta',''));for(const port of status.ports)select.add(new Option(`${port.device} · ${port.description}`,port.device));select.value=selected;select.dataset.ports=ports;}
      select.disabled=robot.connected;el('connect').textContent=robot.connected?'Desconectar':'Conectar';
      el('connection-status').textContent=robot.connected?`Arduino conectado · ${robot.port}`:'Arduino desconectado';
      el('temperature').textContent=sensor.valid?sensor.temperature.toLocaleString('pt-BR',{maximumFractionDigits:1}):'—';
      el('humidity').textContent=sensor.valid?sensor.humidity.toLocaleString('pt-BR',{maximumFractionDigits:1}):'—';
      el('sensor-note').textContent=sensor.valid?`Leitura real · há ${sensor.age_seconds.toLocaleString('pt-BR')} s`:robot.connected?'Sensor sem leitura válida. Confira a conexão do DHT11.':'Conecte o robô para receber leituras reais.';
      el('lcd-state').textContent=robot.connected?(robot.lcd_enabled===false?'Desativado no firmware':robot.lcd_ok?'Detectado':'Não detectado'):'Não verificado';
      el('voice-state').textContent=status.voice.whisper_files&&status.voice.piper_files?'Arquivos disponíveis':'Preparação necessária';
      el('motor-state').textContent=robot.motors_enabled?'Gestos das atividades habilitados':robot.connected?'Teste por comando disponível':'Bloqueados';
      el('test-pulse').disabled=!robot.connected;el('confirm-movement').disabled=!robot.connected||!tested;
      const calibrated=Object.keys(robot.calibrations).map(x=>x==='head'?'braço direito':'braço esquerdo');
      el('gesture-setup').classList.toggle('hidden',!!robot.motors_enabled);
      el('prepare-gestures').classList.toggle('hidden',!robot.connected);
      el('gesture-guidance').textContent=robot.connected?`Gestos do treino: ${calibrated.length} de 2 motores confirmados. Testar um pulso não habilita os gestos: observe e registre braço direito e braço esquerdo abaixo.`:'Você pode conversar agora. Para usar os movimentos no treino, conecte o Arduino e confirme os dois motores.';
      el('calibration-status').textContent=calibrated.length?`Confirmados nesta conexão: ${calibrated.join(' e ')}. ${robot.motors_enabled?'Gestos nas atividades habilitados.':''}`:'Confirme os dois motores para permitir gestos nas atividades.';
      if(robot.error)error(robot.error);
      latestActivity=sensor.valid?robot.activity:null;
      el('heat-activity').classList.toggle('hidden',!latestActivity);
      if(!robot.connected)tested=null;
    } catch(exc) {el('connection-status').textContent='Servidor indisponível';el('temperature').textContent='—';el('humidity').textContent='—';el('sensor-note').textContent='Sem comunicação. Leituras indisponíveis.';}
    finally {polling=false;}
  }
  function parameters() {return {motor:el('motor').value,duration_ms:Number(el('pulse-ms').value),direction:Number(el('direction').value)};}
  async function action(callback) {try{error('');await callback();await refresh();}catch(exc){error(exc.message);}}
  el('robot-form').addEventListener('submit',event=>{event.preventDefault();const text=el('robot-question').value.trim();if(text)send({text});});
  el('talk').addEventListener('click',()=>recording?finishRecording():startRecording());
  el('stop').addEventListener('click',async()=>{++epoch;if(request)request.abort();stopping=true;busy=true;await disposeRecording();resetPlayer();tested=null;buttons();state('Interrompendo');await action(()=>api('stop',{}));});
  el('clear-chat').addEventListener('click',()=>action(async()=>{await api('clear',{});el('messages').replaceChildren();resetPlayer();error('');}));
  el('connect').addEventListener('click',()=>action(async()=>{el('connect').disabled=true;try{tested=null;await api(lastStatus?.robot.connected?'disconnect':'connect',{port:el('serial-port').value});}finally{el('connect').disabled=false;}}));
  el('refresh-ports').addEventListener('click',refresh);
  el('prepare-gestures').addEventListener('click',()=>{el('calibration').open=true;});
  el('test-pulse').addEventListener('click',()=>action(async()=>{if(!el('wiring-confirmed').checked)throw Error('Confirme a montagem antes de testar.');const params=parameters();await api('pulse',{...params,wiring_confirmed:true});tested=params;el('confirm-movement').disabled=false;el('calibration-status').textContent='Pulso enviado. Confirme somente se observou movimento seguro.';}));
  el('confirm-movement').addEventListener('click',()=>action(async()=>{if(!tested||JSON.stringify(tested)!==JSON.stringify(parameters()))throw Error('Teste estes parâmetros antes de confirmar.');await api('calibrate',{...tested,observed:true});tested=null;}));
  document.querySelectorAll('#motor, #pulse-ms, #direction, #wiring-confirmed').forEach(input=>input.addEventListener('change',()=>{tested=null;el('confirm-movement').disabled=true;}));
  document.querySelectorAll('[data-question]').forEach(button=>button.addEventListener('click',()=>send({text:button.dataset.question})));
  el('heat-question').addEventListener('click',()=>{if(latestActivity)send({text:'O sensor observou calor. Vamos aprender a palavra quente?'});});
  player.addEventListener('ended',()=>{state('Pronto');api('state',{state:'READY'}).catch(()=>{});});
  player.addEventListener('play',()=>{state('Falando');api('state',{state:'SPEAK'}).catch(()=>{});});
  player.addEventListener('pause',()=>{if(!busy&&!recording){state('Pronto');api('state',{state:'READY'}).catch(()=>{});}});
  window.addEventListener('pagehide',()=>{if(recording){clearTimeout(recording.timer);recording.stream.getTracks().forEach(track=>track.stop());recording.context.close();}if(request)request.abort();resetPlayer();fetch('/api/robot/stop',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}',keepalive:true}).catch(()=>{});});
  refresh();setInterval(refresh,2000);
}
