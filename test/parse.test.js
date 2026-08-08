import assert from 'node:assert/strict';
import { test } from 'node:test';

import { extractInboundMessages } from '../src/parse.js';

test('picks up a WhatsApp text message', () => {
  const messages = extractInboundMessages({
    object: 'whatsapp_business_account',
    entry: [{
      changes: [{
        value: {
          messages: [{ from: '201000000000', id: 'wamid.1', timestamp: '1700000000' }],
        },
      }],
    }],
  });

  assert.deepEqual(messages, [{
    channel: 'whatsapp',
    senderId: '201000000000',
    messageId: 'wamid.1',
    timestamp: 1700000000000,
  }]);
});

test('ignores WhatsApp delivery/read receipts', () => {
  const messages = extractInboundMessages({
    object: 'whatsapp_business_account',
    entry: [{ changes: [{ value: { statuses: [{ status: 'delivered' }] } }] }],
  });

  assert.deepEqual(messages, []);
});

test('picks up Messenger and Instagram messages with the right channel', () => {
  const event = (object) => ({
    object,
    entry: [{
      messaging: [{
        sender: { id: '123' },
        timestamp: 1700000000000,
        message: { mid: 'm.1', text: 'hi' },
      }],
    }],
  });

  assert.equal(extractInboundMessages(event('page'))[0].channel, 'messenger');
  assert.equal(extractInboundMessages(event('instagram'))[0].channel, 'instagram');
});

test('ignores echoes of our own outgoing replies', () => {
  const messages = extractInboundMessages({
    object: 'page',
    entry: [{
      messaging: [{
        sender: { id: 'PAGE_ID' },
        message: { mid: 'm.2', text: 'welcome', is_echo: true },
      }],
    }],
  });

  assert.deepEqual(messages, []);
});

test('ignores postbacks, reactions and unknown payloads', () => {
  assert.deepEqual(
    extractInboundMessages({
      object: 'page',
      entry: [{ messaging: [{ sender: { id: '1' }, postback: { payload: 'X' } }] }],
    }),
    [],
  );
  assert.deepEqual(extractInboundMessages({}), []);
  assert.deepEqual(extractInboundMessages(null), []);
});
