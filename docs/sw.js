/* Service worker : mise en cache de l'app pour un fonctionnement hors-ligne.
 * Strategie cache-first. Incrementer CACHE a chaque mise a jour des fichiers. */
const CACHE = "ipv4gen-v1";
const ASSETS = [
  "./", "./index.html", "./styles.css", "./app.js",
  "./questions.js", "./manifest.webmanifest", "./icon.svg",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request).then((cached) => {
      if (cached) return cached;
      return fetch(e.request).then((resp) => {
        const copy = resp.clone();
        if (resp.ok && new URL(e.request.url).origin === self.location.origin) {
          caches.open(CACHE).then((c) => c.put(e.request, copy));
        }
        return resp;
      }).catch(() => caches.match("./index.html"));
    })
  );
});
