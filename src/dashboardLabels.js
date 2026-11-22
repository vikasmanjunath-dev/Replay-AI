/** Describe the session state without implying that an unavailable API is still connecting. */
export function getSessionBadgeLabel(session, readinessStatus) {
  if (session.actor) return `${session.actor} · ${session.role}`;
  if (readinessStatus === 'offline') return 'API offline';
  if (readinessStatus === 'auth') return 'Authentication required';
  if (readinessStatus === 'degraded') return 'Session unavailable';
  return 'Connecting';
}
