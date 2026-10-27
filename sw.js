// Nézőnapló service worker – offline indulás + borítóképek cache
const VERSION = 'sm-v12';
const IMG = 'sm-img';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icon-180.png', './icon-192.png', './icon-512.png', './hu-shows.json', './upcoming.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== VERSION && k !== IMG).map(k => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);

  // Saját fájlok: előbb hálózat (így frissül az app), offline esetén cache
  if (url.origin === location.origin) {
    e.respondWith(
      // no-cache: a böngésző ne a 10 percig tárolt régi fájlt adja vissza
      fetch(e.request, {cache: 'no-cache'}).then(res => {
        const copy = res.clone();
        caches.open(VERSION).then(c => c.put(e.request, copy));
        return res;
      }).catch(() => caches.match(e.request, {ignoreSearch: true}).then(r => r || caches.match('./index.html')))
    );
    return;
  }

  // Borítóképek (TVmaze, Wikimedia): előbb cache
  if (url.hostname === 'static.tvmaze.com' || url.hostname.endsWith('wikimedia.org')) {
    e.respondWith(
      caches.open(IMG).then(c => c.match(e.request).then(hit => hit || fetch(e.request).then(res => {
        c.put(e.request, res.clone());
        return res;
      })))
    );
  }
});
