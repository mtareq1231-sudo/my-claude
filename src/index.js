import crypto from 'node:crypto';
import express from 'express';

import { business, config, missingCredentials } from './config.js';
import { buildWelcomeMessage } from './message.js';
import { extractInboundMessages } from './parse.js';
import { Scheduler } from './scheduler.js';
import { Store } from './store.js';

const store = new Store(config.dataDir);
const welcomeText = buildWelcomeMessage(business);
const scheduler = new Scheduler(store, welcomeText);

const app = express();

// The raw body is kept so the X-Hub-Signature-256 header can be verified — the
// signature is computed over the exact bytes Meta sent, not over re-serialized JSON.
app.use(express.json({ verify: (req, _res, buf) => { req.rawBody = buf; } }));

function signatureIsValid(req) {
  const header = req.get('x-hub-signature-256');
  if (!header || !req.rawBody) return false;

  const expected = 'sha256=' + crypto
    .createHmac('sha256', config.appSecret)
    .update(req.rawBody)
    .digest('hex');

  const a = Buffer.from(header);
  const b = Buffer.from(expected);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

// Meta calls this once when you save the webhook URL in the app dashboard.
app.get('/webhook', (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  if (mode === 'subscribe' && token === config.verifyToken) {
    return res.status(200).send(req.query['hub.challenge']);
  }
  return res.sendStatus(403);
});

app.post('/webhook', (req, res) => {
  if (!signatureIsValid(req)) {
    console.warn('[webhook] توقيع غير صحيح — تم رفض الطلب');
    return res.sendStatus(401);
  }

  // Meta retries anything it doesn't get a fast 200 for, so acknowledge first
  // and do the scheduling after.
  res.sendStatus(200);

  for (const message of extractInboundMessages(req.body)) {
    const scheduled = scheduler.schedule(message);
    const status = scheduled ? 'تمت الجدولة' : 'تم التخطي (تم الترحيب به قبل كده)';
    console.log(`[webhook] ${message.channel}:${message.senderId} — ${status}`);
  }
});

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', delaySeconds: config.delayMs / 1000, ...store.stats() });
});

// Handy for checking the wording without messaging the page from a real account.
app.get('/preview', (_req, res) => {
  res.type('text/plain; charset=utf-8').send(welcomeText);
});

const missing = missingCredentials();
if (missing.length) {
  console.warn('[config] متغيرات ناقصة، القنوات دي مش هتشتغل:', missing.join(', '));
}

const server = app.listen(config.port, () => {
  const restored = scheduler.restorePending();
  console.log(`[server] شغال على المنفذ ${config.port}، التأخير ${config.delayMs / 1000}ث`);
  if (restored) console.log(`[server] تم استئناف ${restored} رسالة مجدولة`);
});

for (const signal of ['SIGINT', 'SIGTERM']) {
  process.on(signal, () => {
    scheduler.stop();
    server.close(() => process.exit(0));
  });
}
