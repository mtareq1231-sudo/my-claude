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

test('the message leads with the website and the phone number', () => {
  const text = buildWelcomeMessage({
    storeName: 'Warmup',
    website: 'warmupjo.com',
    phone: '+962 79 222 5298',
    closingLine: 'كيف يمكننا مساعدتك اليوم؟',
  });

  assert.match(text, /أهلاً بك في Warmup/);
  assert.match(text, /تصفّح موقعنا واكتشاف جميع منتجاتنا: warmupjo\.com/);
  assert.match(text, /\+962 79 222 5298/);
  assert.match(text, /كيف يمكننا مساعدتك اليوم؟$/);
});

test('the short message stays short — no policy lines unless asked for', () => {
  const text = buildWelcomeMessage({
    storeName: 'Warmup',
    website: 'warmupjo.com',
    phone: '+962 79 222 5298',
    shipping: '',
    warranty: '',
    returns: '',
  });

  for (const label of ['مدة التوصيل', 'الكفالة', 'الاسترجاع', 'أوقات العمل']) {
    assert.doesNotMatch(text, new RegExp(label), `${label} should be absent`);
  }
  assert.doesNotMatch(text, /undefined/);
});

test('filling in an optional field brings its line back', () => {
  const text = buildWelcomeMessage({
    website: 'warmupjo.com',
    warranty: 'كفالة سنة كاملة على جميع المنتجات',
  });

  assert.match(text, /🛡️ الكفالة: كفالة سنة كاملة على جميع المنتجات/);
});

test('an optional array field renders as a bulleted list under its label', () => {
  const text = buildWelcomeMessage({
    shipping: ['عمّان: 1-2 يوم عمل', 'باقي المحافظات: 2-4 أيام عمل'],
  });

  assert.match(text, /🚚 مدة التوصيل:\n {3}• عمّان: 1-2 يوم عمل\n {3}• باقي المحافظات: 2-4 أيام عمل/);
});

test('the phone line stands alone when there is no website', () => {
  const text = buildWelcomeMessage({ phone: '+962 79 222 5298' });
  assert.match(text, /📞 للتواصل معنا: \+962 79 222 5298/);
  assert.doesNotMatch(text, /أو التواصل/);
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
