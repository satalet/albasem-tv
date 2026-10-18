const CACHE_NAME = 'albasem-tv-v5';
self.addEventListener('install', e => self.skipWaiting());
self.addEventListener('activate', e => {
    e.waitUntil(
        caches.keys().then(keys => Promise.all(keys.map(k => caches.delete(k))))
        .then(() => self.clients.claim())
    );
});
self.addEventListener('fetch', event => {
    // عدم اعتراض أي طلبات بث فيديو أو API لمنع التقطيع والكاش الخاطئ
    return;
});
