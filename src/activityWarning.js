/** @typedef {'right-click' | 'ctrl-f12'} ActivityWarningTrigger */

/**
 * Listen for browser context-menu requests and the exact Ctrl+F12 shortcut.
 * The browser's default context menu and keyboard handling are not cancelled.
 *
 * @param {Document} target
 * @param {(trigger: ActivityWarningTrigger) => void} onTrigger
 * @returns {() => void} Removes both listeners.
 */
export function watchBrowserActivity(target, onTrigger) {
  const onContextMenu = () => onTrigger('right-click');
  const onKeyDown = (event) => {
    if (event.key === 'F12' && event.ctrlKey && !event.altKey && !event.metaKey && !event.shiftKey) {
      onTrigger('ctrl-f12');
    }
  };

  target.addEventListener('contextmenu', onContextMenu);
  target.addEventListener('keydown', onKeyDown);

  return () => {
    target.removeEventListener('contextmenu', onContextMenu);
    target.removeEventListener('keydown', onKeyDown);
  };
}

/** @param {ActivityWarningTrigger} trigger */
export function getActivityWarningMessage(trigger) {
  if (trigger === 'right-click') {
    return 'Warning: Browser context-menu activity detected. Use inspection tools only when authorized.';
  }
  return 'Warning: Ctrl+F12 detected. Use developer tools only when authorized.';
}
