const C="sb-2026-09-12b";  // bump this string whenever you change index.html so returning visitors get the new version
self.addEventListener("install",e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(["./","index.html","manifest.json","icon.png"])));self.skipWaiting();});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))));self.clients.claim();});
self.addEventListener("fetch",e=>{const u=new URL(e.request.url); if(u.origin!==location.origin) return;
  // app shell and data: network first so updates show up; cache is the offline fallback
  e.respondWith(fetch(e.request).then(r=>{ if(r.ok) caches.open(C).then(c=>c.put(e.request,r.clone())); return r; }).catch(()=>caches.match(e.request).then(r=>r||caches.match("index.html"))));
});