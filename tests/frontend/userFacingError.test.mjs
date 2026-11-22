import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { describeRequestError } from '../../src/userFacingError.js';

describe('dashboard request errors', () => {
  it('replaces browser-specific network failures with actionable API guidance', () => {
    for (const message of ['Failed to fetch', 'Load failed', 'NetworkError when attempting to fetch resource.']) {
      assert.equal(
        describeRequestError(new TypeError(message), 'Unable to continue.'),
        'Could not reach the RELAY AI API. Check the API connection and try again.',
      );
    }
  });

  it('preserves useful API and validation error details', () => {
    const error = new Error('Repository target is not allow-listed (Request ID: req-123).');
    assert.equal(describeRequestError(error, 'Action failed.'), error.message);
  });

  it('uses the operation fallback for non-error values and empty messages', () => {
    assert.equal(describeRequestError(null, 'Submission failed.'), 'Submission failed.');
    assert.equal(describeRequestError(new Error(''), 'Action failed.'), 'Action failed.');
  });
});
