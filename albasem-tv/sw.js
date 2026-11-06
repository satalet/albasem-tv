const CACHE_NAME = 'albasem-tv-v3.1-shell';
const SHELL_ASSETS = [
    '/manifest.json',
    '/icon-192.png',
    '/icon-512.png'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_ASSETS)).catch(() => {})
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => Promise.all(
            keys.filter((k) => k.startsWith('albasem-tv-') && k !== CACHE_NAME)
                .map((k) => caches.delete(k))
        )).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
    const req = event.request;
    const url = new URL(req.url);

    // استثناء روابط البث المباشر وواجهات الـ API من الكاش تماماً
    if (
        req.method !== 'GET' ||
        url.origin !== self.location.origin ||
        url.pathname.endsWith('.m3u8') ||
        url.pathname.endsWith('.ts')
    ) {
        return;
    }

    event.respondWith(
        fetch(req, { cache: 'no-store' }).catch(() => caches.match(req))
    );
});
