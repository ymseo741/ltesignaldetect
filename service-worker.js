// service-worker.js

const CACHE_NAME = 'lte-app-cache-v1';
const urlsToCache = [
  '/',
  '/index.html',
  // 필요에 따라 CSS, JS, 이미지 파일 등도 추가
];

// 설치 단계: 파일 캐싱
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
  self.skipWaiting();
});

// 활성화 단계: 이전 캐시 정리
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(key => key !== CACHE_NAME)
            .map(key => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

// 요청 가로채기 및 캐시 제공
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
