import { config } from './config.js';
import { sendMessage } from './senders.js';

/**
 * Holds each reply for `config.delayMs` before sending it.
 *
 * Timers live in memory but every pending reply is also written to the store,
 * so `restorePending()` can re-arm them after a restart.
 */
export class Scheduler {
  #store;
  #text;
  #timers = new Map();
  #send;
  #delayMs;
  #maxLateMs;
  #reWelcomeAfterDays;

  constructor(store, text, options = {}) {
    this.#store = store;
    this.#text = text;
    this.#send = options.send ?? sendMessage;
    this.#delayMs = options.delayMs ?? config.delayMs;
    this.#maxLateMs = options.maxLateMs ?? config.maxLateMs;
    this.#reWelcomeAfterDays = options.reWelcomeAfterDays ?? config.reWelcomeAfterDays;
  }

  /** Queues a welcome for a customer who has not been welcomed before. */
  schedule({ channel, senderId, timestamp = Date.now() }) {
    const key = `${channel}:${senderId}`;
    if (!this.#store.shouldWelcome(key, { reWelcomeAfterDays: this.#reWelcomeAfterDays })) {
      return false;
    }

    const dueAt = timestamp + this.#delayMs;
    this.#store.addPending(key, { channel, senderId, dueAt });
    this.#arm(key, { channel, senderId, dueAt });
    return true;
  }

  #arm(key, entry) {
    clearTimeout(this.#timers.get(key));
    const delay = Math.max(0, entry.dueAt - Date.now());
    const timer = setTimeout(() => {
      this.#timers.delete(key);
      this.#fire(key, entry);
    }, delay);
    timer.unref?.();
    this.#timers.set(key, timer);
  }

  async #fire(key, { channel, senderId, dueAt }) {
    const lateBy = Date.now() - dueAt;
    if (lateBy > this.#maxLateMs) {
      console.warn(`[scheduler] تم إلغاء رسالة متأخرة ${Math.round(lateBy / 1000)}ث لـ ${key}`);
      this.#store.clearPending(key);
      return;
    }

    try {
      await this.#send(channel, senderId, this.#text);
      // Marked only on success, so a failed send can be retried on the
      // customer's next message rather than being recorded as delivered.
      this.#store.markWelcomed(key);
      console.log(`[scheduler] تم إرسال رسالة الترحيب إلى ${key}`);
    } catch (err) {
      this.#store.clearPending(key);
      console.error(`[scheduler] فشل الإرسال إلى ${key}:`, err.message);
    }
  }

  /** Re-arms replies that were still waiting when the process last stopped. */
  restorePending() {
    for (const [key, entry] of this.#store.allPending()) {
      this.#arm(key, entry);
    }
    return this.#store.stats().pending;
  }

  stop() {
    for (const timer of this.#timers.values()) clearTimeout(timer);
    this.#timers.clear();
  }
}
