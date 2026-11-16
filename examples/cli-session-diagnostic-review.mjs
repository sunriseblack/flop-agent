/** Bounded offline replay of almondous's CLI-0.5.0 diagnostic finding.
 * Extracts only the unchanged SDK error class and CLI catch-handler text.
 * No CLI startup, package imports, key generation, wallet, RPC or transaction.
 */
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { test } from 'node:test';

function checked(variable, expected) {
  const file = process.env[variable]; assert.ok(file, `Set ${variable}`);
  assert.ok(!fs.lstatSync(file).isSymbolicLink(), 'regular source required');
  const fd = fs.openSync(file, 'r'); let raw;
  try {
    const stat = fs.fstatSync(fd); assert.ok(stat.isFile() && stat.size <= 2 * 1024 * 1024);
    const b = Buffer.alloc(stat.size + 1); let used = 0;
    while (used < b.length) { const n = fs.readSync(fd, b, used, b.length - used, null); if (!n) break; used += n; }
    assert.ok(used <= stat.size, 'source grew while reading'); raw = b.subarray(0, used);
  } finally { fs.closeSync(fd); }
  assert.equal(createHash('sha256').update(raw).digest('hex'), expected, 'source pin mismatch');
  return raw.toString('utf8');
}
const original = checked('CLI_ORIGINAL', 'c94d7d6bdfee094c401aa5accd04faf19e6d48fd925ffd934f962c2ceca1de40');
const candidate = checked('CLI_CANDIDATE', '3b2f453e2c833974a262559b5af121d1b4d29571e4dac1afa1edeb887c0cb3b9');
const sdk = checked('SDK_DIRECT_SESSION', '1a6af4ec4be8ed7e46a52eed24bc9abc7d7a9685d37a4d1d1570e4c83fa52f74');
const cid = '0xda15edcf0232816d32b4684c221896de08d60ce9238152e9a44c682c30b3d7a3';
const id = Uint8Array.from(Buffer.from(cid.slice(2), 'hex'));
const tx = '0xa51b2c195c09c37353d53840f89c373b0ea33e7e65802adf661073b3e7ec9f51';
const classText = sdk.slice(sdk.indexOf('export class DirectSessionError'), sdk.indexOf('export function sameSessionAccount'));
assert.ok(classText.startsWith('export class DirectSessionError'));
const SDKError = vm.runInNewContext(classText.replace('export class', 'class') + '\nDirectSessionError;', {
  Error, Uint8Array, u8aToHex: value => '0x' + Buffer.from(value).toString('hex'),
});
function render(source, error, funding, walletPath) {
  const command = source.indexOf('function sessionRunCmd() {'); assert.ok(command > 0);
  const startMarker = '    } catch (error) {\n';
  const start = source.indexOf(startMarker, command); const end = source.indexOf('    } finally {', start);
  assert.ok(start > command && end > start);
  const helperStart = source.indexOf('function sessionFailureDiagnostic(error, channelId) {');
  const helper = helperStart < 0 ? '' : source.slice(helperStart, command);
  const processStub = { exitCode: 0 }; let result; let format;
  const fn = vm.runInNewContext(helper + '\n(function(error, funding, walletPath) {\n'
    + source.slice(start + startMarker.length, end) + '\n})', {
    Error, Uint8Array, Buffer, process: processStub,
    printError(value, mode) { result = value; format = mode; },
  });
  fn(error, funding, walletPath);
  return { value: JSON.parse(JSON.stringify(result)), exit: processStub.exitCode, format };
}
const ack = () => new Error('miner acknowledgement timed out');
const failure = recovery => new SDKError('direct session failed; on-chain recovery failed', id,
  { cause: new AggregateError([ack(), recovery], 'session and recovery errors') });
const definitive = () => Object.assign(new Error('PRIVATE_REJECTION_DETAIL'), { code: 'TRANSACTION_FINALIZED_FAILED', txHash: tx });
const uncertain = () => Object.assign(new Error('Bearer PRIVATE_CREDENTIAL'), { code: 'TRANSACTION_UNCONFIRMED', txHash: tx });
function oldFields(value) { const { diagnostic, ...rest } = value; return rest; }

test('unchanged release collapses distinct nested transaction outcomes into identical JSON', () => {
  assert.deepEqual(render(original, failure(definitive())), render(original, failure(uncertain())));
});
test('candidate distinguishes reported failure from an unknown outcome without messages', () => {
  const a = render(candidate, failure(definitive())).value;
  const b = render(candidate, failure(uncertain())).value;
  assert.equal(a.diagnostic.recovery.failure.reported_outcome, 'finalized_failed');
  assert.equal(b.diagnostic.recovery.failure.reported_outcome, 'unknown');
  assert.equal(b.diagnostic.recovery.failure.tx_hash, tx);
  assert.notDeepEqual(a, b);
  assert.ok(!JSON.stringify([a, b]).includes('PRIVATE_'));
});
test('existing code, message, channel, guidance, JSON mode and exit status stay identical', () => {
  for (const e of [failure(definitive()), failure(uncertain()), new SDKError('miner acknowledgement timed out', id, { cause: ack() })]) {
    const before = render(original, e); const after = render(candidate, e);
    assert.deepEqual(oldFields(after.value), before.value);
    assert.equal(after.exit, 1); assert.equal(after.format, 'json');
    assert.equal(after.value.code, 'SESSION_FAILED'); assert.equal(after.value.channel, cid);
    assert.equal(after.value.recovery, 'inspect finalized channel and terminal events before retrying');
  }
});
test('a successfully recovered timeout is not turned into a certified refund', () => {
  const result = render(candidate, new SDKError('miner acknowledgement timed out', id, { cause: ack() })).value;
  assert.equal(result.diagnostic.original_failure.kind, 'miner_ack_timeout');
  assert.deepEqual(result.diagnostic.recovery, { state: 'not_established' });
});
test('plain and non-Error failures retain their exact old output', () => {
  for (const error of [new Error('ordinary safe message'), 'ordinary safe text', null]) {
    assert.deepEqual(render(candidate, error), render(original, error));
  }
});
test('funding uncertainty and saved-wallet fields retain their exact old output', () => {
  const funding = { outcome: 'unknown', success: false, txHash: tx, status: 202, amount: 25 };
  assert.deepEqual(render(candidate, new Error('safe top-level message'), funding, '/private/synthetic/wallet.json'),
    render(original, new Error('safe top-level message'), funding, '/private/synthetic/wallet.json'));
});
test('nested opaque objects and getters do not leak or break candidate rendering', () => {
  let calls = 0; const secret = { request: { headers: { Authorization: 'PRIVATE_CREDENTIAL' } } };
  for (const key of ['code', 'message', 'cause', 'txHash']) {
    Object.defineProperty(secret, key, { get() { calls++; throw Error('do not inspect'); } });
  }
  const output = render(candidate, failure(secret));
  assert.equal(calls, 0); assert.ok(!JSON.stringify(output).includes('PRIVATE_'));
  assert.equal(output.value.diagnostic.recovery.failure.kind, 'unclassified');
});
test('cyclic and huge nested details produce bounded additive diagnostics', () => {
  const recovery = { message: 'PRIVATE_'.repeat(100000) }; recovery.cause = recovery;
  const output = render(candidate, failure(recovery));
  assert.equal(output.value.diagnostic.truncated, true);
  assert.ok(Buffer.byteLength(JSON.stringify(output.value.diagnostic)) < 1024);
});
