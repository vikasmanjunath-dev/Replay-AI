import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { AbortableRequests } from '../../src/abortableRequests.js';

describe('abortable dashboard requests', () => {
  it('aborts the previous request when a replacement starts', () => {
    const requests = new AbortableRequests();
    const first = requests.start();
    const second = requests.start();

    assert.equal(first.signal.aborted, true);
    assert.equal(requests.isCurrent(first), false);
    assert.equal(requests.isCurrent(second), true);
  });

  it('does not let an older request finish and clear its replacement', () => {
    const requests = new AbortableRequests();
    const first = requests.start();
    const second = requests.start();

    requests.finish(first);

    assert.equal(requests.isCurrent(second), true);
  });

  it('aborts and clears outstanding work on cancellation', () => {
    const requests = new AbortableRequests();
    const controller = requests.start();

    requests.cancel();

    assert.equal(controller.signal.aborted, true);
    assert.equal(requests.isCurrent(controller), false);
  });
});
