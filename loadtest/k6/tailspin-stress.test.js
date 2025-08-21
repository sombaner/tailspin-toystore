import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

// Config
const BASE_URL = __ENV.BASE_URL || 'http://4.187.182.42';
const TIME_BETWEEN_REQUESTS = parseFloat(__ENV.THINK_TIME || '0.2'); // seconds

// Custom metrics
export const errors = new Rate('errors');
export const http5xx = new Counter('http_5xx');
export const http4xx = new Counter('http_4xx');
export const ttfb = new Trend('time_to_first_byte_ms');

// Ramping until failure. Adjust targets as needed.
export const options = {
  scenarios: {
    breaking_point: {
      executor: 'ramping-vus',
      startVUs: 10,
      stages: [
        { duration: '1m', target: 200 },
        { duration: '1m', target: 500 },
        { duration: '1m', target: 800 },
        { duration: '2m', target: 1200 },
        { duration: '2m', target: 1600 },
        { duration: '3m', target: 2000 },
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    errors: [{ threshold: 'rate<0.02', abortOnFail: true, delayAbortEval: '1m' }], // stop if >2% errors
    http_req_failed: ['rate<0.02'],
    http_req_duration: ['p(95)<2000'], // 95% under 2s
  },
  discardResponseBodies: true,
  noConnectionReuse: false,
};

const paths = [
  '/',
  '/api/games',
  '/game/1',
  '/game/2',
  '/game/3',
];

function pickPath() {
  // Heavier weight on home and API list
  const weighted = ['/', '/', '/api/games', '/api/games', '/game/1', '/game/2', '/game/3'];
  return weighted[Math.floor(Math.random() * weighted.length)];
}

export default function () {
  const path = pickPath();
  const url = `${BASE_URL}${path}`;
  const res = http.get(url, { tags: { path } });

  ttfb.add(res.timings.waiting);

  const ok = check(res, {
    'status is 2xx': (r) => r.status >= 200 && r.status < 300,
  });

  if (!ok) {
    errors.add(1);
  } else {
    errors.add(0);
  }

  if (res.status >= 500) http5xx.add(1);
  if (res.status >= 400 && res.status < 500) http4xx.add(1);

  sleep(TIME_BETWEEN_REQUESTS);
}

export function handleSummary(data) {
  return {
    'loadtest/results.json': JSON.stringify(data, null, 2),
  };
}
