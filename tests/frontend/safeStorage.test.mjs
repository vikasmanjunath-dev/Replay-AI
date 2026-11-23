import assert from 'node:assert/strict';
import { afterEach, describe, it } from 'node:test';
import { readStorage, removeStorage, writeStorage } from '../../src/safeStorage.js';

const originalWindow = globalThis.window;

function memoryStorage(initial = {}) {
  const values = new Map(Object.entries(initial));
  return {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, String(value)),
    removeItem: (key) => values.delete(key),
  };
}

function setWindow(properties) {
  const mockWindow = {};
  Object.defineProperties(mockWindow, Object.getOwnPropertyDescriptors(properties));
  Object.defineProperty(globalThis, 'window', {
    configurable: true,
    value: mockWindow,
  });
}

afterEach(() => {
  if (originalWindow === undefined) delete globalThis.window;
  else Object.defineProperty(globalThis, 'window', { configurable: true, value: originalWindow });
});

describe('safe browser storage', () => {
  it('reads and writes supported browser storage', () => {
    setWindow({ localStorage: memoryStorage(), sessionStorage: memoryStorage() });

    assert.equal(writeStorage('local', 'relay-theme', 'dark'), true);
    assert.equal(writeStorage('session', 'relay-api-token', 'secret-token'), true);

    assert.equal(readStorage('local', 'relay-theme'), 'dark');
    assert.equal(readStorage('session', 'relay-api-token'), 'secret-token');
  });

  it('returns no preference when local storage access is denied', () => {
    setWindow({
      get localStorage() { throw new Error('storage denied'); },
      sessionStorage: memoryStorage(),
    });

    assert.equal(writeStorage('local', 'relay-theme', 'dark'), false);
    assert.doesNotThrow(() => removeStorage('local', 'relay-theme'));
    assert.equal(readStorage('local', 'relay-theme'), null);
  });

  it('keeps session values in memory when session storage access is denied', () => {
    setWindow({
      localStorage: memoryStorage(),
      get sessionStorage() { throw new Error('storage denied'); },
    });

    assert.equal(writeStorage('session', 'relay-api-token', 'secret-token'), false);
    assert.equal(readStorage('session', 'relay-api-token'), 'secret-token');
    removeStorage('session', 'relay-api-token');
    assert.equal(readStorage('session', 'relay-api-token'), null);
  });

  it('hides stale session values if removal itself fails', () => {
    const staleStorage = {
      getItem: () => 'old-key',
      setItem: () => { throw new Error('quota exceeded'); },
      removeItem: () => { throw new Error('storage denied'); },
    };
    setWindow({ localStorage: memoryStorage(), sessionStorage: staleStorage });

    assert.equal(writeStorage('session', 'relay-action-key', 'new-key'), false);
    assert.equal(readStorage('session', 'relay-action-key'), 'new-key');
    removeStorage('session', 'relay-action-key');
    assert.equal(readStorage('session', 'relay-action-key'), null);
  });
});
