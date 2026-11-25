# Browser Activity Warning Architecture

## Event flow

1. `watchBrowserActivity()` in `src/activityWarning.js` attaches `contextmenu` and `keydown` listeners to the document.
2. A context-menu event reports `right-click`. An unmodified `Ctrl+F12` event reports `ctrl-f12`.
3. `App` maps the trigger to user-facing text and stores it in React state.
4. The dashboard renders a polite live-region notice with a dismiss button.
5. React removes the listeners when `App` unmounts.

```text
Document event → activityWarning.js → React state → accessible warning notice
```

The listeners do not call `preventDefault()` or stop propagation. Existing browser behavior remains in control. The helper is independent of the UI so its event matching and cleanup can be tested with the platform `EventTarget` API.
