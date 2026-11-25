# Browser Activity Warning

## What it does

The dashboard displays a dismissible warning when it receives a browser `contextmenu` event or the exact `Ctrl+F12` keyboard shortcut. The message identifies the detected action and reminds the user to use inspection tools only when authorized.

## How to use it

- Right-click anywhere in the dashboard to display the context-menu warning.
- Press `Ctrl+F12` to display the developer-tools shortcut warning when the browser sends that key event to the page.
- Activate **Dismiss browser activity warning** to close the notice.
- Repeat either action to display the notice again.

The feature does not block the context menu, cancel keyboard input, inspect browser tools, or prevent page inspection. Browsers may handle reserved shortcuts before a page receives them, so the shortcut warning is best-effort. This is a user notice, not an access-control or anti-tampering mechanism.
