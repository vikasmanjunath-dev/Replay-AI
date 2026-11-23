/** @typedef {'local' | 'session'} StorageArea */

// Session values remain usable for this page lifetime when browser storage is denied.
const sessionOverrides = new Map();

/**
 * @param {StorageArea} area
 * @param {string} key
 * @returns {string | null}
 */
export function readStorage(area, key) {
  if (area === 'session' && sessionOverrides.has(key)) return sessionOverrides.get(key) ?? null;
  try {
    const storage = area === 'session' ? window.sessionStorage : window.localStorage;
    return storage.getItem(key);
  } catch {
    return null;
  }
}

/** @param {StorageArea} area @param {string} key @param {string} value @returns {boolean} */
export function writeStorage(area, key, value) {
  try {
    const storage = area === 'session' ? window.sessionStorage : window.localStorage;
    storage.setItem(key, value);
    if (area === 'session') sessionOverrides.delete(key);
    return true;
  } catch {
    if (area === 'session') sessionOverrides.set(key, value);
    return false;
  }
}

/** @param {StorageArea} area @param {string} key */
export function removeStorage(area, key) {
  try {
    const storage = area === 'session' ? window.sessionStorage : window.localStorage;
    storage.removeItem(key);
    if (area === 'session') sessionOverrides.delete(key);
  } catch {
    if (area === 'session') sessionOverrides.set(key, null);
  }
}
