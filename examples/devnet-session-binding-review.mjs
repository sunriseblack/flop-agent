/** Offline regression review for wyc4t's FLOP-EXP-001 public fixture checker.
 * Paths are supplied by the caller. Original source, capture, lock and metadata
 * hashes are checked before loading either checker. No live capture is called.
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const packetDir = process.env.DEVNET_PACKET_DIR;
const metadataFile = process.env.DEVNET_METADATA_FILE;
const patchedFile = process.env.DEVNET_PATCHED_CHECKER;
if (!packetDir || !metadataFile || !patchedFile) {
  throw new Error('Set DEVNET_PACKET_DIR, DEVNET_METADATA_FILE and DEVNET_PATCHED_CHECKER');
}
const hashes = {
  original: 'a5a114c211bb11ea455df15420547a7d21aafde14048e5765e2814e718f9f547',
  patched: '0836ee9185157b83cae8630ad1ea8aab77161a097d8b3407cba5f04629a4e1dc',
  capture: '47a4061fc50d962cf3c1376339cb1b676d9b2f538dbf40886fd28cc2c0db0fd2',
  lock: '2d2ab9e3ddfbc8363f2dff7f549ef44fcdbf6cf164cfc791a06b719eadcb8491',
  metadata: '4a144b9e881f9c086b26f3225ace9958593acf393c8194a9f367059f6948d8dd',
};
function readBounded(file) {
  const descriptor = fs.openSync(file, 'r');
  try {
    const stat = fs.fstatSync(descriptor);
    assert.ok(stat.isFile() && stat.size <= 2 * 1024 * 1024, 'bounded regular input required');
    const buffer = Buffer.alloc(stat.size + 1);
    let total = 0;
    while (total < buffer.length) {
      const count = fs.readSync(descriptor, buffer, total, buffer.length - total, null);
      if (!count) break;
      total += count;
    }
    assert.ok(total <= stat.size, 'input grew during read');
    return buffer.subarray(0, total);
  } finally {
    fs.closeSync(descriptor);
  }
}
function checked(file, expected) {
  const raw = readBounded(file);
  assert.equal(createHash('sha256').update(raw).digest('hex'), expected, 'input hash mismatch');
  return raw;
}
const root = path.resolve(packetDir);
const source = checked(path.join(root, 'verify-session.mjs'), hashes.original).toString('utf8');
const candidate = checked(patchedFile, hashes.patched).toString('utf8');
const capture = checked(path.join(root, 'capture.json'), hashes.capture);
checked(path.join(root, 'package-lock.json'), hashes.lock);
const metadataHex = readBounded(metadataFile).toString('utf8').trim();
assert.match(metadataHex, /^0x(?:[0-9a-fA-F]{2})+$/);
assert.equal(createHash('sha256').update(Buffer.from(metadataHex.slice(2), 'hex')).digest('hex'), hashes.metadata);

// The published modules do not export verify(). Load their unchanged definition
// before the CLI entry point, inside a private temporary module. Capture never runs.
const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'flop-binding-review-'));
const previousEntry = process.env.FLOP_CLI_ENTRY;
let originalModule;
let patchedModule;
try {
  process.env.FLOP_CLI_ENTRY = path.join(root, 'package.json');
  for (const [name, code] of [['original', source], ['patched', candidate]]) {
    const marker = 'const deadline = setTimeout(';
    assert.equal(code.split(marker).length, 2, 'CLI boundary changed');
    fs.writeFileSync(path.join(directory, name + '.mjs'),
      code.slice(0, code.indexOf(marker)) + 'export { verify, version };\n',
      { mode: 0o600, flag: 'wx' });
  }
  originalModule = await import(pathToFileURL(path.join(directory, 'original.mjs')));
  patchedModule = await import(pathToFileURL(path.join(directory, 'patched.mjs')));
} finally {
  if (previousEntry === undefined) delete process.env.FLOP_CLI_ENTRY;
  else process.env.FLOP_CLI_ENTRY = previousEntry;
  fs.rmSync(directory, { recursive: true, force: true });
}
const original = originalModule.verify;
const patched = patchedModule.verify;
for (const [name, version] of Object.entries({
  '@polkadot/api': '17.0.2', '@polkadot/types': '17.0.2',
  '@polkadot/util': '14.0.3', '@polkadot/util-crypto': '14.0.3',
})) {
  assert.equal(originalModule.version(name), version, 'dependency version mismatch');
}
const req = createRequire(path.join(root, 'package.json'));
const { cryptoWaitReady, blake2AsHex } = req('@polkadot/util-crypto');
await cryptoWaitReady();
const fixture = JSON.parse(capture.toString('utf8'));
fixture.rpc.metadataHex = metadataHex;
const fresh = () => structuredClone(fixture);
function changeHex(value) {
  return '0x' + (value[2] === '0' ? '1' : '0') + value.slice(3);
}
function updateHashes(value) {
  value.rpc.extrinsicHash = blake2AsHex(value.rpc.extrinsicHex, 256);
  value.explorer.settlement.extrinsicHash = value.rpc.extrinsicHash;
}
function changeRaw(value, before, after) {
  assert.equal(value.rpc.extrinsicHex.split(before.slice(2)).length, 2);
  value.rpc.extrinsicHex = value.rpc.extrinsicHex.replace(before.slice(2), after.slice(2));
  updateHashes(value);
}
function rejected(value) {
  try {
    assert.equal(patched(value).allChecksPassed, false);
  } catch (error) {
    // Malformed SCALE or signature encodings also refuse the fixture in the real CLI.
    if (error.code === 'ERR_ASSERTION') throw error;
  }
}

test('original fixture still passes its 14 checks', () => {
  assert.equal(original(fresh()).allChecksPassed, true);
});
test('metadata-enriched original passes all 18 checks', () => {
  const result = patched(fresh());
  assert.equal(result.allChecksPassed, true);
  assert.equal(Object.keys(result.checks).length, 18);
});
test('object key order remains immaterial', () => {
  const value = fresh();
  value.rpc.call = { args: value.rpc.call.args, callIndex: value.rpc.call.callIndex };
  assert.equal(patched(value).allChecksPassed, true);
});
test('capture timestamp remains observation metadata', () => {
  const value = fresh();
  value.capturedAt = '2026-11-05T00:00:00Z';
  assert.equal(patched(value).allChecksPassed, true);
});
test('missing historical runtime metadata is refused', () => {
  const value = fresh();
  delete value.rpc.metadataHex;
  assert.throws(() => patched(value), /metadata is required/);
});
test('malformed runtime metadata is refused', () => {
  const value = fresh();
  value.rpc.metadataHex = '0x00';
  assert.throws(() => patched(value));
});
test('raw output mutation with refreshed hashes exposes the original gap', () => {
  const value = fresh();
  const turn = value.rpc.call.args.verified_turns[0];
  changeRaw(value, turn.hOut, changeHex(turn.hOut));
  assert.equal(original(value).allChecksPassed, true);
  const result = patched(value);
  assert.equal(result.checks.decodedCallMatchesRaw, false);
  assert.equal(result.checks.minerSessionSignatureValid, false);
  assert.equal(result.allChecksPassed, false);
});
test('changing decoded output alone is rejected against raw bytes', () => {
  const value = fresh();
  const turn = value.rpc.call.args.verified_turns[0];
  turn.hOut = changeHex(turn.hOut);
  rejected(value);
});
test('matching raw and decoded mutations cannot preserve the original signatures', () => {
  const value = fresh();
  const turn = value.rpc.call.args.verified_turns[0];
  const changed = changeHex(turn.hOut);
  changeRaw(value, turn.hOut, changed);
  turn.hOut = changed;
  const result = patched(value);
  assert.equal(result.checks.decodedCallMatchesRaw, true);
  assert.equal(result.checks.minerSessionSignatureValid, false);
  assert.equal(result.allChecksPassed, false);
});
for (const field of ['agent receipt', 'miner witness']) {
  test(`changed raw ${field} signature is rejected`, () => {
    const value = fresh();
    const object = field === 'agent receipt'
      ? value.rpc.call.args : value.rpc.call.args.verified_turns[0];
    const key = field === 'agent receipt' ? 'agent_receipt_sig' : 'enclaveSig';
    const changed = changeHex(object[key]);
    changeRaw(value, object[key], changed);
    object[key] = changed;
    rejected(value);
  });
}
test('raw trailing bytes cannot be hidden behind an updated hash', () => {
  const value = fresh();
  value.rpc.extrinsicHex += '00';
  updateHashes(value);
  assert.equal(original(value).allChecksPassed, true);
  assert.equal(patched(value).checks.rawExtrinsicRoundTrips, false);
  rejected(value);
});
test('truncated raw extrinsic is refused', () => {
  const value = fresh();
  value.rpc.extrinsicHex = value.rpc.extrinsicHex.slice(0, -2);
  updateHashes(value);
  rejected(value);
});
test('unrelated raw bytes with consistent displayed hashes are refused', () => {
  const value = fresh();
  value.rpc.extrinsicHex = '0x00';
  updateHashes(value);
  assert.equal(original(value).allChecksPassed, true);
  assert.throws(() => patched(value));
});
test('supplied signer must match the raw signer', () => {
  const value = fresh();
  value.rpc.signer = value.rpc.channel.agent;
  rejected(value);
});
for (const [field, changed] of [['callSection', 'balances'], ['callMethod', 'transfer']]) {
  test(`supplied ${field} must match the raw call`, () => {
    const value = fresh();
    value.rpc[field] = changed;
    rejected(value);
  });
}
test('altered header number is rejected', () => {
  const value = fresh();
  value.rpc.header.number++;
  assert.equal(original(value).allChecksPassed, true);
  rejected(value);
});
test('altering both block numbers still fails the header hash', () => {
  const value = fresh();
  value.rpc.header.number++;
  value.rpc.blockNumber = String(value.rpc.header.number);
  rejected(value);
});
test('altered parent hash is rejected', () => {
  const value = fresh();
  value.rpc.header.parentHash = changeHex(value.rpc.header.parentHash);
  rejected(value);
});
test('matching changed block hashes still fail header binding', () => {
  const value = fresh();
  value.rpc.blockHashAtHeight = changeHex(value.rpc.blockHashAtHeight);
  value.explorer.settlement.blockHash = value.rpc.blockHashAtHeight;
  assert.equal(original(value).allChecksPassed, true);
  rejected(value);
});
test('changed supplied extrinsic index is refused', () => {
  const value = fresh();
  value.rpc.extrinsicIndex = 3;
  assert.throws(() => patched(value), /Unexpected fixture/);
});
test('changed genesis keeps the existing channel-ID rejection', () => {
  const value = fresh();
  value.rpc.genesisHash = changeHex(value.rpc.genesisHash);
  rejected(value);
});
test('changed escrow keeps the existing receipt rejection', () => {
  const value = fresh();
  value.rpc.channel.escrow = String(BigInt(value.rpc.channel.escrow) + 1n);
  rejected(value);
});
