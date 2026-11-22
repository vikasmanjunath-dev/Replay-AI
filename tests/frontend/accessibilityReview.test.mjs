import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const [app, styles] = await Promise.all([
  readFile(new URL('../../src/App.tsx', import.meta.url), 'utf8'),
  readFile(new URL('../../src/theme.css', import.meta.url), 'utf8'),
]);

test('dashboard exposes keyboard skip navigation and a focus-visible indicator', () => {
  assert.match(app, /className="skip-link sr-only" href="#main-content"/);
  assert.match(app, /id="main-content"[^>]*tabIndex=\{-1\}/);
  assert.match(styles, /button:focus-visible[\s\S]*?outline:\s*3px solid/);
  assert.match(styles, /\.skip-link:focus\s*\{/);
});

test('dashboard keeps service and request failures announced and recoverable', () => {
  assert.match(app, /readiness.status === 'offline' \? 'alert' : 'status'/);
  assert.match(app, /aria-label="Check pipeline service readiness again"/);
  assert.match(app, /role=\{error \? 'alert' : 'status'\}/);
  assert.match(app, /aria-label="Dismiss notification"/);
});

test('mobile layout and reduced-motion preferences have explicit rules', () => {
  assert.match(styles, /@media\s*\(max-width:\s*400px\)/);
  assert.match(styles, /@media\s*\(max-width:\s*620px\)/);
  assert.match(styles, /@media\s*\(prefers-reduced-motion:\s*reduce\)/);
});

test('empty task and result states provide visible text', () => {
  assert.match(app, /Submitted tasks will appear here\./);
  assert.match(app, /Your pipeline results/);
  assert.match(app, /Submit a report to see triage/);
});
