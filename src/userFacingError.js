const NETWORK_FAILURES = new Set(['failed to fetch', 'load failed', 'networkerror when attempting to fetch resource.']);

/** Turn browser-specific fetch failures into a stable, actionable dashboard message. */
export function describeRequestError(reason, fallback) {
  if (!(reason instanceof Error)) return fallback;
  if (reason instanceof TypeError && NETWORK_FAILURES.has(reason.message.trim().toLowerCase())) {
    return 'Could not reach the RELAY AI API. Check the API connection and try again.';
  }
  return reason.message || fallback;
}
