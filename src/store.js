import fs from 'node:fs';
import path from 'node:path';

/**
 * Tiny JSON-file store. It keeps two things across restarts:
 *   welcomed — customers who already got the message, so nobody gets it twice
 *   pending  — replies scheduled but not yet sent, so a restart mid-wait
 *              doesn't silently swallow them
 *
 * A file is enough here: one row per customer, written a few times a minute at
 * worst. Swap in a real database only if this ever runs on more than one node.
 */
export class Store {
  #file;
  #state;

  constructor(dataDir) {
    this.#file = path.join(dataDir, 'contacts.json');
    fs.mkdirSync(dataDir, { recursive: true });
    this.#state = this.#read();
  }

  #read() {
    try {
      const parsed = JSON.parse(fs.readFileSync(this.#file, 'utf8'));
      return {
        welcomed: parsed.welcomed ?? {},
        pending: parsed.pending ?? {},
      };
    } catch (err) {
      if (err.code !== 'ENOENT') {
        console.error(`[store] ${this.#file} unreadable, starting empty:`, err.message);
      }
      return { welcomed: {}, pending: {} };
    }
  }

  // Written through a temp file and renamed, so a crash mid-write can never
  // leave a half-written contacts.json behind. Synchronous on purpose: the file
  // must be on disk before the caller continues, and it is a few KB at most.
  #save() {
    const tmp = `${this.#file}.tmp`;
    fs.writeFileSync(tmp, JSON.stringify(this.#state, null, 2));
    fs.renameSync(tmp, this.#file);
  }

  /** True when this customer is due a welcome message. */
  shouldWelcome(key, { reWelcomeAfterDays = 0, now = Date.now() } = {}) {
    if (this.#state.pending[key]) return false;

    const welcomedAt = this.#state.welcomed[key];
    if (!welcomedAt) return true;
    if (reWelcomeAfterDays <= 0) return false;

    return now - welcomedAt >= reWelcomeAfterDays * 24 * 60 * 60 * 1000;
  }

  addPending(key, entry) {
    this.#state.pending[key] = entry;
    this.#save();
  }

  clearPending(key) {
    delete this.#state.pending[key];
    this.#save();
  }

  markWelcomed(key, now = Date.now()) {
    delete this.#state.pending[key];
    this.#state.welcomed[key] = now;
    this.#save();
  }

  allPending() {
    return Object.entries(this.#state.pending);
  }

  stats() {
    return {
      welcomed: Object.keys(this.#state.welcomed).length,
      pending: Object.keys(this.#state.pending).length,
    };
  }
}
