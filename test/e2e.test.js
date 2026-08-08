import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { after, before, test } from 'node:test';

/**
 * Runs the real server as a child process against a stand-in for the Graph API,
 * and drives it with the webhook payloads Meta actually sends. This is what
 * proves the whole path works — signature check, parsing, the delay, the
 * once-per-customer rule, and the outbound call for each of the three channels.
 */

const APP_SECRET = 'test-app-secret';
const VERIFY_TOKEN = 'test-verify-token';
const PHONE_NUMBER_ID = '111222333';

let botPort;
let botProcess;
let graphServer;
const graphCalls = [];

const listenOnFreePort = (server) =>
  new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server.address().port)));

function sign(body) {
  return 'sha256=' + crypto.createHmac('sha256', APP_SECRET).update(body).digest('hex');
}

async function postWebhook(payload, { signature } = {}) {
  const body = JSON.stringify(payload);
  return fetch(`http://127.0.0.1:${botPort}/webhook`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Hub-Signature-256': signature ?? sign(body),
    },
    body,
  });
}

async function waitFor(predicate, { timeout = 8000, label = 'condition' } = {}) {
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    if (await predicate()) return;
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
  throw new Error(`timed out waiting for ${label}`);
}

before(async () => {
  // Stand-in for graph.facebook.com: records every outbound send.
  graphServer = http.createServer((req, res) => {
    let body = '';
    req.on('data', (chunk) => { body += chunk; });
    req.on('end', () => {
      graphCalls.push({
        url: req.url,
        authorization: req.headers.authorization,
        body: JSON.parse(body),
      });
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ messages: [{ id: 'sent' }] }));
    });
  });
  const graphPort = await listenOnFreePort(graphServer);

  const probe = http.createServer();
  botPort = await listenOnFreePort(probe);
  await new Promise((resolve) => probe.close(resolve));

  botProcess = spawn(process.execPath, ['src/index.js'], {
    cwd: path.resolve(import.meta.dirname, '..'),
    stdio: ['ignore', 'pipe', 'pipe'],
    env: {
      ...process.env,
      PORT: String(botPort),
      DATA_DIR: fs.mkdtempSync(path.join(os.tmpdir(), 'welcome-e2e-')),
      GRAPH_API_BASE: `http://127.0.0.1:${graphPort}`,
      META_VERIFY_TOKEN: VERIFY_TOKEN,
      META_APP_SECRET: APP_SECRET,
      WHATSAPP_PHONE_NUMBER_ID: PHONE_NUMBER_ID,
      WHATSAPP_TOKEN: 'wa-token',
      FB_PAGE_TOKEN: 'page-token',
      WELCOME_DELAY_SECONDS: '1',
    },
  });

  await waitFor(
    () => fetch(`http://127.0.0.1:${botPort}/health`).then((r) => r.ok, () => false),
    { label: 'the server to come up' },
  );
});

after(async () => {
  botProcess?.kill();
  await new Promise((resolve) => graphServer.close(resolve));
});

test('Meta can verify the webhook subscription', async () => {
  const url = `http://127.0.0.1:${botPort}/webhook`
    + `?hub.mode=subscribe&hub.verify_token=${VERIFY_TOKEN}&hub.challenge=42`;
  const res = await fetch(url);

  assert.equal(res.status, 200);
  assert.equal(await res.text(), '42');

  const wrongToken = await fetch(url.replace(VERIFY_TOKEN, 'wrong'));
  assert.equal(wrongToken.status, 403);
});

test('a forged webhook is rejected and never reaches the queue', async () => {
  const res = await postWebhook(
    {
      object: 'whatsapp_business_account',
      entry: [{ changes: [{ value: { messages: [{ from: '962790000001', id: 'w1', timestamp: '1' }] } }] }],
    },
    { signature: 'sha256=deadbeef' },
  );

  assert.equal(res.status, 401);
  await new Promise((resolve) => setTimeout(resolve, 1500));
  assert.equal(graphCalls.length, 0);
});

test('a WhatsApp message is answered after the delay, once', async () => {
  const payload = {
    object: 'whatsapp_business_account',
    entry: [{
      changes: [{
        value: {
          messages: [{
            from: '962790000002',
            id: 'wamid.1',
            timestamp: String(Math.floor(Date.now() / 1000)),
          }],
        },
      }],
    }],
  };

  assert.equal((await postWebhook(payload)).status, 200);
  // Nothing goes out immediately — the whole point is the wait.
  assert.equal(graphCalls.length, 0);

  // Same customer writes again while the reply is still pending.
  await postWebhook(payload);

  await waitFor(() => graphCalls.length === 1, { label: 'the WhatsApp reply' });

  const call = graphCalls[0];
  assert.equal(call.url, `/v21.0/${PHONE_NUMBER_ID}/messages`);
  assert.equal(call.authorization, 'Bearer wa-token');
  assert.equal(call.body.messaging_product, 'whatsapp');
  assert.equal(call.body.to, '962790000002');
  assert.match(call.body.text.body, /أهلاً بك في Warmup/);
  assert.match(call.body.text.body, /تم استلام رسالتك/);
  assert.match(call.body.text.body, /https:\/\/warmupjo\.com/);

  // And once more after delivery — still just the one reply.
  await postWebhook(payload);
  await new Promise((resolve) => setTimeout(resolve, 1500));
  assert.equal(graphCalls.length, 1);
});

test('Messenger and Instagram are answered through the Send API', async () => {
  graphCalls.length = 0;

  for (const object of ['page', 'instagram']) {
    await postWebhook({
      object,
      entry: [{
        messaging: [{
          sender: { id: `${object}-user` },
          timestamp: Date.now(),
          message: { mid: `mid.${object}`, text: 'مرحبا' },
        }],
      }],
    });
  }

  await waitFor(() => graphCalls.length === 2, { label: 'the Messenger and Instagram replies' });

  for (const call of graphCalls) {
    assert.equal(call.url, '/v21.0/me/messages');
    assert.equal(call.authorization, 'Bearer page-token');
    assert.equal(call.body.messaging_type, 'RESPONSE');
    assert.match(call.body.message.text, /https:\/\/warmupjo\.com/);
  }
  assert.deepEqual(
    graphCalls.map((c) => c.body.recipient.id).sort(),
    ['instagram-user', 'page-user'],
  );
});

test('delivery receipts and our own echoes are ignored', async () => {
  graphCalls.length = 0;

  await postWebhook({
    object: 'whatsapp_business_account',
    entry: [{ changes: [{ value: { statuses: [{ id: 'wamid.1', status: 'read' }] } }] }],
  });
  await postWebhook({
    object: 'page',
    entry: [{
      messaging: [{
        sender: { id: 'PAGE_ID' },
        message: { mid: 'mid.echo', text: 'أهلاً بك في Warmup', is_echo: true },
      }],
    }],
  });

  await new Promise((resolve) => setTimeout(resolve, 1500));
  assert.equal(graphCalls.length, 0);
});
