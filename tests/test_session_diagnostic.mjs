import { test } from 'node:test';
import assert from 'node:assert/strict';
import { sessionFailureDiagnostic } from '../examples/session-failure-diagnostic.mjs';

const cid = '0xda15edcf0232816d32b4684c221896de08d60ce9238152e9a44c682c30b3d7a3';
const tx = '0xa51b2c195c09c37353d53840f89c373b0ea33e7e65802adf661073b3e7ec9f51';
function direct(message, cause) {
  const e = new Error(`${message} (channel ${cid})`, { cause });
  e.name = 'DirectSessionError'; return e;
}
const ack = () => new Error('miner acknowledgement timed out');
const failure = recovery => direct('direct session failed; on-chain recovery failed',
  new AggregateError([ack(), recovery], 'session and recovery errors'));

test('distinct recovery metadata distinguishes rejected and unknown submissions', () => {
  const rejected = Object.assign(new Error('private dispatch detail'), { code: 'TRANSACTION_FINALIZED_FAILED', txHash: tx });
  const unknown = Object.assign(new Error('Bearer PRIVATE_SENTINEL'), { code: 'TRANSACTION_UNCONFIRMED', txHash: tx });
  const a = sessionFailureDiagnostic(failure(rejected), cid);
  const b = sessionFailureDiagnostic(failure(unknown), cid);
  assert.equal(a.original_failure.kind, 'miner_ack_timeout');
  assert.equal(a.recovery.failure.reported_outcome, 'finalized_failed');
  assert.equal(b.recovery.failure.reported_outcome, 'unknown');
  assert.equal(b.recovery.failure.tx_hash, tx);
  assert.notDeepEqual(a, b);
  assert.equal(b.evidence, 'client_error_metadata_only');
});
test('an acknowledgement timeout without a recovery error does not certify a refund', () => {
  const value = sessionFailureDiagnostic(direct('miner acknowledgement timed out', ack()), cid);
  assert.equal(value.original_failure.kind, 'miner_ack_timeout');
  assert.deepEqual(value.recovery, { state: 'not_established' });
});
test('plain errors and malformed channel identifiers do not gain SDK diagnostics', () => {
  assert.equal(sessionFailureDiagnostic(new Error('ordinary'), cid), undefined);
  for (const id of [null, '', cid.slice(0, -1), cid + '0', tx.toUpperCase()]) {
    assert.equal(sessionFailureDiagnostic(failure(new Error('ordinary')), id), undefined);
  }
});
test('messages, headers, payloads, names, stacks and arbitrary codes are omitted', () => {
  const e = Object.assign(new Error('Bearer PRIVATE_SENTINEL'), {
    name: 'PRIVATE_SENTINEL', code: 'PRIVATE_SENTINEL', stack: 'PRIVATE_SENTINEL',
    request: { headers: { Authorization: 'PRIVATE_SENTINEL' } }, payload: 'PRIVATE_SENTINEL',
    txHash: 'https://credential:PRIVATE_SENTINEL@host.invalid',
    toJSON() { throw new Error('must not serialize an error'); },
  });
  const value = sessionFailureDiagnostic(failure(e), cid);
  assert.equal(value.recovery.failure.kind, 'unclassified');
  assert.ok(!JSON.stringify(value).includes('PRIVATE_SENTINEL'));
});
test('only syntactically valid public transaction hashes are included', () => {
  for (const value of ['0x1', tx + '0', {}, { toString() { throw Error('do not coerce'); } }]) {
    const e = Object.assign(new Error('redacted'), { code: 'TRANSACTION_UNCONFIRMED', txHash: value });
    assert.equal(sessionFailureDiagnostic(failure(e), cid).recovery.failure.tx_hash, undefined);
  }
});
test('nested diagnostic getters and custom stringification are not invoked', () => {
  let calls = 0;
  const e = {};
  for (const key of ['code', 'message', 'cause', 'txHash']) {
    Object.defineProperty(e, key, { get() { calls++; throw Error('private getter'); } });
  }
  e.toString = () => { calls++; throw Error('private conversion'); };
  assert.equal(sessionFailureDiagnostic(failure(e), cid).recovery.failure.kind, 'unclassified');
  assert.equal(calls, 0);
});
test('an AggregateError errors getter is not used as a trusted pair', () => {
  let calls = 0;
  const e = {};
  Object.defineProperty(e, 'errors', { get() { calls++; throw Error('do not read'); } });
  const value = sessionFailureDiagnostic(direct('direct session failed; on-chain recovery failed', e), cid);
  assert.equal(value.recovery.failure.kind, 'unclassified'); assert.equal(calls, 0);
});
test('two errors without the SDK recovery-stage marker do not establish recovery failure', () => {
  const cause = new AggregateError([ack(), Object.assign(new Error('redacted'), { code: 'TRANSACTION_UNCONFIRMED' })]);
  const value = sessionFailureDiagnostic(direct('other failure', cause), cid);
  assert.deepEqual(value.recovery, { state: 'not_established' });
});
test('cycles and long cause chains terminate with an explicit truncation flag', () => {
  const cycle = {}; cycle.cause = cycle;
  assert.equal(sessionFailureDiagnostic(failure(cycle), cid).truncated, true);
  let chain = Object.assign(new Error('hidden deep result'), { code: 'TRANSACTION_FINALIZED_FAILED' });
  for (let i = 0; i < 20; i++) chain = { cause: chain };
  const value = sessionFailureDiagnostic(failure(chain), cid);
  assert.equal(value.truncated, true); assert.equal(value.recovery.failure.kind, 'unclassified');
  assert.ok(Buffer.byteLength(JSON.stringify(value)) < 1024);
});
test('proxy descriptor failure is contained without copying proxy data', () => {
  const e = new Proxy({}, { getOwnPropertyDescriptor() { throw new Error('private trap'); } });
  assert.equal(sessionFailureDiagnostic(failure(e), cid).recovery.failure.kind, 'unclassified');
});
test('a malformed or oversized aggregate is not traversed', () => {
  const e = { errors: new Array(100000) };
  const value = sessionFailureDiagnostic(direct('direct session failed; on-chain recovery failed', e), cid);
  assert.equal(value.original_failure.kind, 'unclassified');
  assert.equal(value.recovery.failure.kind, 'unclassified');
});
test('a revoked proxy array does not break CLI rendering', () => {
  const revocable = Proxy.revocable([], {}); revocable.revoke();
  const value = sessionFailureDiagnostic(direct('direct session failed; on-chain recovery failed',
    { errors: revocable.proxy }), cid);
  assert.equal(value.recovery.failure.kind, 'unclassified');
});
test('recognized reconciliation metadata remains unknown and is bounded', () => {
  const e = Object.assign(new Error('PRIVATE_SENTINEL'.repeat(100000)), { code: 'RECONCILIATION_UNKNOWN' });
  const value = sessionFailureDiagnostic(direct('cooperative settlement outcome unknown', e), cid);
  assert.equal(value.original_failure.reported_outcome, 'unknown');
  assert.ok(Buffer.byteLength(JSON.stringify(value)) < 1024);
});

// Adjacent regressions for almondous's independent 228f2b2 review (#291).
test('recognized uncertainty survives an unreadable hash without invoking its getter', () => {
  let calls = 0;
  const e = Object.assign(new Error('PRIVATE_SENTINEL'), { code: 'TRANSACTION_UNCONFIRMED' });
  Object.defineProperty(e, 'txHash', { get() { calls++; throw Error('PRIVATE_SENTINEL'); } });
  const value = sessionFailureDiagnostic(failure(e), cid);
  assert.equal(value.recovery.failure.reported_outcome, 'unknown');
  assert.equal(value.recovery.failure.tx_hash, undefined);
  assert.equal(calls, 0); assert.ok(!JSON.stringify(value).includes('PRIVATE_SENTINEL'));
  const readable = Object.assign(new Error('redacted'), { code: 'TRANSACTION_UNCONFIRMED', txHash: tx });
  assert.equal(sessionFailureDiagnostic(failure(readable), cid).recovery.failure.tx_hash, tx);
});
test('inherited transaction labels stay unclassified while own metadata is recognized', () => {
  const inherited = Object.create({ code: 'TRANSACTION_UNCONFIRMED', txHash: tx });
  const value = sessionFailureDiagnostic(failure(inherited), cid);
  assert.equal(value.recovery.failure.kind, 'unclassified');
  assert.equal(value.recovery.failure.tx_hash, undefined);
  const owned = { code: 'TRANSACTION_UNCONFIRMED', txHash: tx };
  assert.equal(sessionFailureDiagnostic(failure(owned), cid).recovery.failure.reported_outcome, 'unknown');
});
test('conflicting aggregate children do not invent a recovery transaction outcome', () => {
  const rejected = { code: 'TRANSACTION_FINALIZED_FAILED', txHash: tx };
  const unknown = { code: 'TRANSACTION_UNCONFIRMED', txHash: tx };
  const value = sessionFailureDiagnostic(failure(new AggregateError([rejected, unknown])), cid);
  assert.equal(value.recovery.failure.kind, 'unclassified');
  assert.equal(value.recovery.failure.reported_outcome, undefined);
  assert.equal(sessionFailureDiagnostic(failure(rejected), cid).recovery.failure.reported_outcome, 'finalized_failed');
  assert.equal(sessionFailureDiagnostic(failure(unknown), cid).recovery.failure.reported_outcome, 'unknown');
});
