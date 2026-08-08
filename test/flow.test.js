import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { test } from 'node:test';

import { buildWelcomeMessage } from '../src/message.js';
import { Scheduler } from '../src/scheduler.js';
import { Store } from '../src/store.js';

const tempStore = () => new Store(fs.mkdtempSync(path.join(os.tmpdir(), 'welcome-')));

// The real delay is 60s; these tests override it so they finish instantly.
const scheduler = (store, options) => new Scheduler(store, 'hello', { delayMs: 0, ...options });

test('the message carries website, phone, shipping and warranty', () => {
  const text = buildWelcomeMessage({
    storeName: 'متجر تجريبي',
    website: 'https://shop.example',
    phone: '+201000000000',
    shipping: '2 إلى 5 أيام',
    warranty: 'ضمان سنة',
  });

  assert.match(text, /متجر تجريبي/);
  assert.match(text, /https:\/\/shop\.example/);
  assert.match(text, /\+201000000000/);
  assert.match(text, /2 إلى 5 أيام/);
  assert.match(text, /ضمان سنة/);
});

test('omitted fields drop their line instead of printing blanks', () => {
  const text = buildWelcomeMessage({ website: 'https://shop.example' });
  assert.match(text, /الموقع/);
  assert.doesNotMatch(text, /رقم التواصل/);
  assert.doesNotMatch(text, /undefined/);
});

test('each customer is welcomed exactly once', async () => {
  const sent = [];
  const bot = scheduler(tempStore(), {
    send: (channel, to) => { sent.push(`${channel}:${to}`); return Promise.resolve(); },
  });

  const message = { channel: 'whatsapp', senderId: '2010', timestamp: Date.now() };
  assert.equal(bot.schedule(message), true);
  // Same customer messaging again while the first reply is still pending.
  assert.equal(bot.schedule(message), false);

  await new Promise((resolve) => setTimeout(resolve, 20));
  assert.deepEqual(sent, ['whatsapp:2010']);

  // And again after it was delivered.
  assert.equal(bot.schedule(message), false);
  bot.stop();
});

test('the same id on different channels is treated as two customers', async () => {
  const sent = [];
  const bot = scheduler(tempStore(), {
    send: (channel, to) => { sent.push(`${channel}:${to}`); return Promise.resolve(); },
  });

  bot.schedule({ channel: 'messenger', senderId: '999' });
  bot.schedule({ channel: 'instagram', senderId: '999' });

  await new Promise((resolve) => setTimeout(resolve, 20));
  assert.deepEqual(sent.sort(), ['instagram:999', 'messenger:999']);
  bot.stop();
});

test('a failed send is not recorded, so the next message retries', async () => {
  let attempts = 0;
  const bot = scheduler(tempStore(), {
    send: () => {
      attempts += 1;
      return attempts === 1 ? Promise.reject(new Error('boom')) : Promise.resolve();
    },
  });

  const message = { channel: 'whatsapp', senderId: '2011' };
  bot.schedule(message);
  await new Promise((resolve) => setTimeout(resolve, 20));

  assert.equal(bot.schedule(message), true);
  await new Promise((resolve) => setTimeout(resolve, 20));
  assert.equal(attempts, 2);
  bot.stop();
});

test('pending replies survive a restart', async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'welcome-'));
  const sent = [];

  // Queue a reply, then "crash" before its timer ever gets to run. The message
  // is backdated by the full delay so it comes due the moment it is restored.
  const first = scheduler(new Store(dir), {
    delayMs: 60_000,
    send: () => assert.fail('the first process should have stopped before sending'),
  });
  first.schedule({ channel: 'whatsapp', senderId: '2012', timestamp: Date.now() - 60_000 });
  first.stop();

  const second = scheduler(new Store(dir), {
    send: (channel, to) => { sent.push(`${channel}:${to}`); return Promise.resolve(); },
  });
  assert.equal(second.restorePending(), 1);

  await new Promise((resolve) => setTimeout(resolve, 20));
  assert.deepEqual(sent, ['whatsapp:2012']);
  second.stop();
});
