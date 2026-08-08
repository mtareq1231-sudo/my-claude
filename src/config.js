import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

function loadJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(rootDir, relativePath), 'utf8'));
}

function num(value, fallback) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

export const business = loadJson('config/business.json');

export const config = {
  port: num(process.env.PORT, 3000),
  dataDir: process.env.DATA_DIR || path.join(rootDir, 'data'),

  // Meta credentials. All three channels sit behind the same webhook.
  verifyToken: process.env.META_VERIFY_TOKEN || '',
  appSecret: process.env.META_APP_SECRET || '',
  graphVersion: process.env.META_GRAPH_VERSION || 'v21.0',
  // Overridden by the end-to-end test to point at a local stand-in for Graph.
  graphApiBase: process.env.GRAPH_API_BASE || 'https://graph.facebook.com',
  whatsappPhoneNumberId: process.env.WHATSAPP_PHONE_NUMBER_ID || '',
  whatsappToken: process.env.WHATSAPP_TOKEN || '',
  pageToken: process.env.FB_PAGE_TOKEN || '',
  instagramToken: process.env.IG_TOKEN || process.env.FB_PAGE_TOKEN || '',

  // How long to wait after the customer's message before replying.
  delayMs: num(process.env.WELCOME_DELAY_SECONDS, 60) * 1000,

  // A reply that is already this late is dropped instead of sent — it would
  // reach the customer long after the conversation moved on (and, on WhatsApp,
  // risks falling outside the 24-hour customer service window).
  maxLateMs: num(process.env.MAX_LATE_SECONDS, 600) * 1000,

  // 0 means "welcome each customer once, ever". Set to e.g. 30 to welcome the
  // same customer again after 30 days of silence.
  reWelcomeAfterDays: num(process.env.RE_WELCOME_AFTER_DAYS, 0),
};

export function missingCredentials() {
  const missing = [];
  if (!config.verifyToken) missing.push('META_VERIFY_TOKEN');
  if (!config.appSecret) missing.push('META_APP_SECRET');
  if (!config.whatsappPhoneNumberId || !config.whatsappToken) {
    missing.push('WHATSAPP_PHONE_NUMBER_ID + WHATSAPP_TOKEN (واتساب)');
  }
  if (!config.pageToken) missing.push('FB_PAGE_TOKEN (ماسنجر + انستجرام)');
  return missing;
}
