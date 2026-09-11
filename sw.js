const CACHE_NAME = 'pitwall-shell-v54';
const SHELL_FILES = [
  './',
  './index.html',
  './login.html',
  './reset-password.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(SHELL_FILES)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  // Cache-first for the app shell. All live data (Schedule, and later the
  // logbook) is fetched directly by the page from Supabase, not through here.
  event.respondWith(
    caches.match(event.request).then(cached => cached || fetch(event.request))
  );
});
