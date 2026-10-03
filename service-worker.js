const CACHE_NAME = "songs-of-worship-praise-v6"; // Bumped from v5 to v6 to flush old cache

const FILES_TO_CACHE = [
    "./",
    "./index.html",
    "./manifest.json",
    "./songs_977.js",
    "./icon-192.png",
    "./icon-512.png",
    './eagle.png',
    "./Bald-eagle.jpg"
];


// ================================
// INSTALL
// ================================
self.addEventListener("install", event => {

    event.waitUntil(

        caches.open(CACHE_NAME)
            .then(cache => {

                return cache.addAll(FILES_TO_CACHE);

            })
            .then(() => {

                return self.skipWaiting();

            })

    );

});


// ================================
// ACTIVATE
// ================================
self.addEventListener("activate", event => {

    event.waitUntil(

        caches.keys()
            .then(cacheNames => {

                return Promise.all(

                    cacheNames
                        .filter(cacheName => {
                            return cacheName !== CACHE_NAME;
                        })
                        .map(cacheName => {
                            return caches.delete(cacheName);
                        })

                );

            })
            .then(() => {

                return self.clients.claim();

            })

    );

});


// ================================
// FETCH
// ================================
self.addEventListener("fetch", event => {

    const request = event.request;

    // Only handle GET requests
    if (request.method !== "GET") {
        return;
    }


    event.respondWith(

        caches.match(request)
            .then(cachedResponse => {

                // If the file is already cached,
                // use the cached copy immediately.
                if (cachedResponse) {

                    return cachedResponse;

                }


                // If it isn't cached, try the internet.
                return fetch(request)

                    .then(networkResponse => {

                        // Save successful same-origin
                        // responses for future offline use.
                        if (
                            networkResponse &&
                            networkResponse.ok &&
                            networkResponse.type === "basic"
                        ) {

                            const responseClone =
                                networkResponse.clone();


                            caches.open(CACHE_NAME)
                                .then(cache => {

                                    cache.put(
                                        request,
                                        responseClone
                                    );

                                });

                        }


                        return networkResponse;

                    })

                    .catch(() => {

                        // If the user is offline and
                        // this is a page navigation,
                        // open the cached app.
                        if (request.mode === "navigate") {

                            return caches.match(
                                "./index.html"
                            );

                        }


                        // Other missing resources
                        // return an offline response.
                        return new Response(
                            "",
                            {
                                status: 503,
                                statusText: "Offline"
                            }
                        );

                    });

            })

    );

});
