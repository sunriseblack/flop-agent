/** Additive client-error diagnostics, never chain-outcome or retry authority.
 * Do not copy messages, stacks, URLs, requests or arbitrary nested objects.
 * Existing top-level CLI fields are outside this helper's redaction scope.
 */
export function sessionFailureDiagnostic(error, channelId) {
  const data = (value, key) => {
    if (!value || typeof value !== 'object') return undefined;
    try {
      const descriptor = Object.getOwnPropertyDescriptor(value, key);
      return descriptor && Object.hasOwn(descriptor, 'value') ? descriptor.value : undefined;
    } catch {
      return undefined;
    }
  };
  if (typeof channelId !== 'string' || !/^0x[0-9a-f]{64}$/.test(channelId)
      || data(error, 'name') !== 'DirectSessionError') return undefined;

  let truncated = false;
  const classify = initial => {
    const seen = new Set();
    let current = initial;
    for (let depth = 0; current && typeof current === 'object'; depth++) {
      if (depth === 4 || seen.has(current)) { truncated = true; break; }
      seen.add(current);
      let kind;
      let reportedOutcome;
      switch (data(current, 'code')) {
        case 'TRANSACTION_UNCONFIRMED':
          kind = 'transaction_unconfirmed'; reportedOutcome = 'unknown'; break;
        case 'TRANSACTION_FINALIZED_FAILED':
          kind = 'transaction_finalized_failed'; reportedOutcome = 'finalized_failed'; break;
        case 'RECONCILIATION_UNKNOWN':
          kind = 'settlement_reconciliation_unknown'; reportedOutcome = 'unknown'; break;
        case 'TERMINAL_OUTCOME':
          kind = 'terminal_outcome_reported'; break;
      }
      if (kind) {
        const tx = data(current, 'txHash');
        return { kind, ...(reportedOutcome ? { reported_outcome: reportedOutcome } : {}),
          ...(typeof tx === 'string' && /^0x[0-9a-fA-F]{64}$/.test(tx) ? { tx_hash: tx.toLowerCase() } : {}) };
      }
      if (data(current, 'message') === 'miner acknowledgement timed out') {
        return { kind: 'miner_ack_timeout' };
      }
      current = data(current, 'cause');
    }
    return { kind: 'unclassified' };
  };

  const cause = data(error, 'cause');
  const recoveryFailed = data(error, 'message')
    === `direct session failed; on-chain recovery failed (channel ${channelId})`;
  const errors = data(cause, 'errors');
  let pair = false;
  if (recoveryFailed) {
    try { pair = Array.isArray(errors) && data(errors, 'length') === 2; } catch { /* unavailable metadata */ }
  }
  const original = classify(pair ? data(errors, '0') : cause);
  const recovery = recoveryFailed
    ? { state: 'failure_reported', failure: classify(pair ? data(errors, '1') : undefined) }
    : { state: 'not_established' };
  return { schema: 'flop-session-diagnostic-v1', evidence: 'client_error_metadata_only',
    original_failure: original, recovery, truncated };
}
