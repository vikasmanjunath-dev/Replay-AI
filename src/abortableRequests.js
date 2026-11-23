/** Tracks one replaceable request and aborts stale work. */
export class AbortableRequests {
  /** @type {AbortController | null} */
  current = null;

  /** @returns {AbortController} */
  start() {
    this.current?.abort();
    this.current = new AbortController();
    return this.current;
  }

  /** @param {AbortController} controller */
  isCurrent(controller) {
    return this.current === controller && !controller.signal.aborted;
  }

  /** @param {AbortController} controller */
  finish(controller) {
    if (this.current === controller) this.current = null;
  }

  cancel() {
    this.current?.abort();
    this.current = null;
  }
}
