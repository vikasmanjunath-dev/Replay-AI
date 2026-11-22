import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { getSessionBadgeLabel } from '../../src/dashboardLabels.js';

describe('session badge labels', () => {
  it('shows an authenticated actor and role', () => {
    assert.equal(getSessionBadgeLabel({ actor: 'operator-1', role: 'operator' }, 'ready'), 'operator-1 · operator');
  });

  it('describes unauthenticated service states without claiming to be connecting', () => {
    assert.equal(getSessionBadgeLabel({ actor: '', role: 'viewer' }, 'offline'), 'API offline');
    assert.equal(getSessionBadgeLabel({ actor: '', role: 'viewer' }, 'auth'), 'Authentication required');
    assert.equal(getSessionBadgeLabel({ actor: '', role: 'viewer' }, 'degraded'), 'Session unavailable');
    assert.equal(getSessionBadgeLabel({ actor: '', role: 'viewer' }, 'checking'), 'Connecting');
  });
});
