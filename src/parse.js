/**
 * Flattens a Meta webhook payload into a list of inbound customer messages:
 *   { channel, senderId, messageId, timestamp }
 *
 * Anything that isn't a real message from a real customer is dropped here —
 * delivery/read receipts, reactions, echoes of our own replies, status updates.
 * Everything downstream can assume it is looking at a customer who just wrote in.
 */
export function extractInboundMessages(payload) {
  const messages = [];
  if (!payload || !Array.isArray(payload.entry)) return messages;

  for (const entry of payload.entry) {
    if (payload.object === 'whatsapp_business_account') {
      for (const change of entry.changes ?? []) {
        // `statuses` events are delivery/read receipts, not customer messages.
        for (const message of change.value?.messages ?? []) {
          if (!message.from) continue;
          messages.push({
            channel: 'whatsapp',
            senderId: message.from,
            messageId: message.id,
            // WhatsApp timestamps are seconds since epoch.
            timestamp: Number(message.timestamp) * 1000 || Date.now(),
          });
        }
      }
      continue;
    }

    if (payload.object === 'page' || payload.object === 'instagram') {
      const channel = payload.object === 'page' ? 'messenger' : 'instagram';
      for (const event of entry.messaging ?? []) {
        const message = event.message;
        if (!message) continue; // delivery, read, postback, reaction …
        if (message.is_echo) continue; // our own outgoing message coming back
        if (!event.sender?.id) continue;
        messages.push({
          channel,
          senderId: event.sender.id,
          messageId: message.mid,
          timestamp: Number(event.timestamp) || Date.now(),
        });
      }
    }
  }

  return messages;
}

export const contactKey = (channel, senderId) => `${channel}:${senderId}`;
