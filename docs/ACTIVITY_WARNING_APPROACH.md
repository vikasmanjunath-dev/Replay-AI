# Browser Activity Warning Approach

## Acceptance criteria

- Right-click and the exact `Ctrl+F12` chord show different, clear warning text.
- The warning is dismissible and announced through a polite live region.
- The browser context menu and normal keyboard events are not blocked.
- Other function-key combinations do not trigger the warning.
- Event listeners are removed when the dashboard component unmounts.
- Automated tests cover trigger matching, non-interference, user-facing text, and cleanup.

## Design decisions

- Treat these events as an informational notice only. They do not establish user intent and must not be logged as a security incident.
- Keep detection in a small DOM-event helper and render the notice in the existing dashboard so event logic remains independently testable.
- Do not disable context menus, trap focus, or intercept reserved browser shortcuts. Browser behavior varies, and a page cannot reliably detect every developer-tools opening path.
- Keep the warning visible until dismissed; repeated triggers can bring it back after dismissal.

## Verification

Run `npm test`, `npm run lint`, and `npm run build` from the repository root. Manually confirm the notice appears for right-click and `Ctrl+F12` in a browser that delivers the shortcut to page scripts; confirm the browser's context menu still opens and the dismiss control works with keyboard and pointer input.
