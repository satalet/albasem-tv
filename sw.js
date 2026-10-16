const CACHE_NAME = 'albasem-v1';

self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(clients.claim());
});

self.addEventListener('fetch', (e) => {
  // تمرير الطلبات بشكل طبيعي
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
