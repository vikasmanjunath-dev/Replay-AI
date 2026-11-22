import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { describe, it } from 'node:test';

const css = await readFile(new URL('../../src/theme.css', import.meta.url), 'utf8');
const lightRoot = css.match(/:root\s*\{([^}]+)\}/)?.[1];
const darkRoot = css.match(/:root\[data-theme="dark"\]\s*\{([^}]+)\}/)?.[1];
assert.ok(lightRoot, 'light theme token block exists');
assert.ok(darkRoot, 'dark theme token block exists');

function token(name, root = darkRoot, theme = 'dark') {
  const value = root.match(new RegExp(`${name}:\\s*(#[0-9a-f]{6})`, 'i'))?.[1];
  assert.ok(value, `${theme} theme token ${name} is a hex color`);
  return hex(value);
}

function hex(value) {
  return [1, 3, 5].map((offset) => Number.parseInt(value.slice(offset, offset + 2), 16));
}

function luminance(rgb) {
  const linear = rgb.map((value) => {
    const channel = value / 255;
    return channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
  });
  return linear[0] * 0.2126 + linear[1] * 0.7152 + linear[2] * 0.0722;
}

function contrast(foreground, background) {
  const [light, dark] = [luminance(foreground), luminance(background)].sort((a, b) => b - a);
  return (light + 0.05) / (dark + 0.05);
}

function minimumContrast(label, foreground, background) {
  const ratio = contrast(foreground, background);
  assert.ok(ratio >= 4.5, `${label} contrast is ${ratio.toFixed(2)}:1 (needs 4.5:1)`);
  return ratio;
}

function offlineNoticeColors(selector, backgroundSelector = selector, theme = 'dark') {
  const prefix = theme === 'dark' ? ':root\\[data-theme="dark"\\] ' : '';
  const rule = css.match(new RegExp(`${prefix}${selector}\\s*\\{([^}]+)\\}`))?.[1];
  const backgroundRule = css.match(new RegExp(`${prefix}${backgroundSelector}\\s*\\{([^}]+)\\}`))?.[1];
  assert.ok(rule, `${selector} dark theme rule exists`);
  const fg = rule.match(/color:\s*(#[0-9a-f]{6})/i)?.[1];
  const bg = backgroundRule?.match(/background:\s*rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)/)?.slice(1).map(Number);
  assert.ok(fg && bg, `${selector} declares foreground and translucent background colors`);
  const base = token('--canvas', theme === 'dark' ? darkRoot : lightRoot, theme);
  const composite = bg.slice(0, 3).map((channel, index) => channel * bg[3] + base[index] * (1 - bg[3]));
  return { foreground: hex(fg), background: composite };
}

describe('sampled dark theme text contrast', () => {
  it('keeps muted and secondary text above WCAG AA normal-text contrast', () => {
    const canvas = token('--canvas');
    minimumContrast('muted', token('--muted'), canvas);
    minimumContrast('secondary', token('--secondary'), canvas);
  });

  it('keeps offline readiness text and details above WCAG AA normal-text contrast', () => {
    const heading = offlineNoticeColors('.readiness-notice.offline');
    const detail = offlineNoticeColors('.readiness-notice.offline small', '.readiness-notice.offline');
    minimumContrast('offline heading', heading.foreground, heading.background);
    minimumContrast('offline detail', detail.foreground, detail.background);
  });
});

describe('sampled light theme text contrast', () => {
  it('keeps muted and secondary text above WCAG AA normal-text contrast', () => {
    const canvas = token('--canvas', lightRoot, 'light');
    minimumContrast('muted', token('--muted', lightRoot, 'light'), canvas);
    minimumContrast('secondary', token('--secondary', lightRoot, 'light'), canvas);
  });

  it('keeps offline readiness text and details above WCAG AA normal-text contrast', () => {
    const heading = offlineNoticeColors('.readiness-notice.offline', '.readiness-notice.offline', 'light');
    const detail = offlineNoticeColors('.readiness-notice.offline small', '.readiness-notice.offline', 'light');
    minimumContrast('offline heading', heading.foreground, heading.background);
    minimumContrast('offline detail', detail.foreground, detail.background);
  });
});
