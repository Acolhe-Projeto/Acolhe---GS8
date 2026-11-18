"use strict";
// Explicit object upload only; the browser never opens a camera or persists bytes.
const visionForm=document.getElementById('vision-form');
const visionFile=document.getElementById('vision-file');
const visionButton=document.getElementById('vision-submit');
const visionOutput=document.getElementById('vision-output');
function visionText(pt,es){return document.getElementById('language').value==='es'?es:pt;}
function translateVision(){
 document.getElementById('vision-file-label').textContent=visionText('Foto de objetos (PNG/JPEG, até 8 MiB)','Foto de objetos (PNG/JPEG, hasta 8 MiB)');
 visionButton.textContent=visionText('Reconhecer objetos','Reconocer objetos');
 visionOutput.textContent='';
}
document.getElementById('language').addEventListener('change',translateVision);
translateVision();
visionForm.addEventListener('submit',async event=>{
 event.preventDefault();
 const file=visionFile.files?.[0];
 if(!file){visionOutput.textContent=visionText('Selecione uma foto de objetos.','Selecciona una foto de objetos.');return;}
 if(!['image/png','image/jpeg'].includes(file.type)||!file.size||file.size>8*1024*1024){
  visionOutput.textContent=visionText('Use PNG/JPEG de até 8 MiB.','Usa PNG/JPEG de hasta 8 MiB.');visionFile.value='';return;
 }
 visionButton.disabled=true;
 visionOutput.textContent=visionText('Reconhecendo objetos…','Reconociendo objetos…');
 try{
  const response=await fetch('/api/vision/predict',{method:'POST',headers:{'Content-Type':file.type},body:file});
  const result=await response.json();
  if(!response.ok)throw Error(response.status===503?visionText('Modelo indisponível. É necessário concluir o treino local.','Modelo no disponible. Es necesario completar el entrenamiento local.'):visionText('Não foi possível analisar esta imagem.','No se pudo analizar esta imagen.'));
  visionOutput.replaceChildren();
  for(const item of result.detections||[]){
   const line=document.createElement('p');
   line.textContent=`${item.pt} / ${item.es} · ${Math.round(item.confidence*100)}%`;
   visionOutput.append(line);
  }
  if(!result.detections?.length)visionOutput.textContent=visionText('Nenhum objeto das classes conhecidas foi reconhecido.','No se reconoció ningún objeto de las clases conocidas.');
 }catch(error){visionOutput.textContent=error instanceof TypeError?visionText('Sem conexão com o servidor.','Sin conexión con el servidor.'):error.message;}
 finally{visionFile.value='';visionButton.disabled=false;}
});
