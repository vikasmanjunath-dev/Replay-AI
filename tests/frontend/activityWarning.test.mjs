import test from 'node:test';
import assert from 'node:assert/strict';
import { getActivityWarningMessage, watchBrowserActivity } from '../../src/activityWarning.js';

function keyEvent(key, { ctrlKey = false, altKey = false, metaKey = false, shiftKey = false } = {}) {
  const event = new Event('keydown', { cancelable: true });
  Object.defineProperties(event, {
    key: { value: key },
    ctrlKey: { value: ctrlKey },
    altKey: { value: altKey },
    metaKey: { value: metaKey },
    shiftKey: { value: shiftKey },
  });
  return event;
}

test('right-click reports activity without blocking the browser context menu', () => {
  const target = new EventTarget();
  const triggers = [];
  watchBrowserActivity(target, (trigger) => triggers.push(trigger));
  const event = new Event('contextmenu', { cancelable: true });

  target.dispatchEvent(event);

  assert.deepEqual(triggers, ['right-click']);
  assert.equal(event.defaultPrevented, false);
});

test('only the exact Ctrl+F12 shortcut reports keyboard activity', () => {
  const target = new EventTarget();
  const triggers = [];
  watchBrowserActivity(target, (trigger) => triggers.push(trigger));

  target.dispatchEvent(keyEvent('F12'));
  target.dispatchEvent(keyEvent('F11', { ctrlKey: true }));
  target.dispatchEvent(keyEvent('F12', { ctrlKey: true, shiftKey: true }));
  target.dispatchEvent(keyEvent('F12', { ctrlKey: true, altKey: true }));
  target.dispatchEvent(keyEvent('F12', { ctrlKey: true }));

  assert.deepEqual(triggers, ['ctrl-f12']);
});

test('listener cleanup stops future warnings and message text identifies the trigger', () => {
  const target = new EventTarget();
  const triggers = [];
  const removeListeners = watchBrowserActivity(target, (trigger) => triggers.push(trigger));
  removeListeners();
  target.dispatchEvent(new Event('contextmenu'));

  assert.deepEqual(triggers, []);
  assert.match(getActivityWarningMessage('right-click'), /context-menu activity detected/i);
  assert.match(getActivityWarningMessage('ctrl-f12'), /Ctrl\+F12 detected/i);
});
