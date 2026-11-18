const CACHE='acolhe-v4'; const FILES=['/','/style.css','/fonts.css','/app.js','/vision.js','/logo.png','/icon.svg','/manifest.webmanifest','/lessons.json','/robo.html','/robot.js','/robot.css'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(FILES))));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))));
self.addEventListener('fetch',event=>{const url=new URL(event.request.url);if(event.request.method!=='GET'||url.origin!==location.origin||url.pathname.startsWith('/api/')||url.pathname==='/metrics')return;event.respondWith(fetch(event.request).catch(()=>caches.match(event.request).then(r=>r||new Response('Offline',{status:503}))));});
