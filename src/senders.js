import { config } from './config.js';

const graph = (pathname) => `https://graph.facebook.com/${config.graphVersion}/${pathname}`;

async function post(url, token, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });

  const text = await res.text();
  if (!res.ok) {
    throw new Error(`Graph API ${res.status}: ${text}`);
  }
  return text;
}

/** WhatsApp Cloud API — send as the business phone number. */
function sendWhatsApp(to, text) {
  if (!config.whatsappPhoneNumberId || !config.whatsappToken) {
    throw new Error('WhatsApp غير مضبوط: محتاج WHATSAPP_PHONE_NUMBER_ID و WHATSAPP_TOKEN');
  }
  return post(graph(`${config.whatsappPhoneNumberId}/messages`), config.whatsappToken, {
    messaging_product: 'whatsapp',
    recipient_type: 'individual',
    to,
    type: 'text',
    text: { preview_url: true, body: text },
  });
}

/**
 * Messenger and Instagram DMs share the Send API and the Page token — an
 * Instagram professional account replies through the Page it is linked to.
 */
function sendMessenger(to, text, token) {
  if (!token) {
    throw new Error('ماسنجر/انستجرام غير مضبوط: محتاج FB_PAGE_TOKEN');
  }
  return post(graph('me/messages'), token, {
    recipient: { id: to },
    message: { text },
    messaging_type: 'RESPONSE',
  });
}

export function sendMessage(channel, to, text) {
  switch (channel) {
    case 'whatsapp':
      return sendWhatsApp(to, text);
    case 'messenger':
      return sendMessenger(to, text, config.pageToken);
    case 'instagram':
      return sendMessenger(to, text, config.instagramToken);
    default:
      throw new Error(`قناة غير معروفة: ${channel}`);
  }
}
