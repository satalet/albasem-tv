const CACHE_NAME = 'albasem-v2';

self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(clients.claim());
});

self.addEventListener('fetch', (e) => {
  const url = e.request.url;

  // استثناء البروكسي وتدفقات الفيديو وقوائم التشغيل تماماً ليتولاها المتصفح مباشرة
  if (url.includes('/api/proxy') || url.includes('.ts') || url.includes('.m3u8')) {
    return;
  }

  // تمرير الملفات العادية للموقع
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});
