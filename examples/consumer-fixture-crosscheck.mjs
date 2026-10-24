// Offline cross-implementation check of one pinned inert fixture, not a consumer policy.
// No network, signing key, embedded URL, store, wallet or model is used.
import assert from 'node:assert/strict';
import { createHash, createPublicKey, verify as ed25519Verify } from 'node:crypto';
import { readFileSync, statSync } from 'node:fs';

const [path, expectedHash] = process.argv.slice(2);
assert(path && /^[0-9a-f]{64}$/.test(expectedHash), 'pass fixture path and expected SHA-256');
assert(statSync(path).size <= 256 * 1024, 'fixture exceeds byte bound');
const raw = readFileSync(path);
assert(raw.length <= 256 * 1024, 'fixture exceeds byte bound');
assert.equal(createHash('sha256').update(raw).digest('hex'), expectedHash);

// Require source-token support; silently falling back to rounded Number is unsafe.
assert.equal(JSON.parse('1000000000000000001', (_k, _v, c) => c?.source),
  '1000000000000000001', 'this Node runtime lacks lossless JSON source-token support');
const corpus = JSON.parse(raw.toString('utf8'), (key, value, context) => {
  if (key !== 'nonce') return value;
  assert.equal(typeof value, 'number', 'this pinned corpus models numeric export nonces');
  assert(/^[0-9]{1,19}$/.test(context.source), 'nonce is not an exact decimal token');
  return context.source;
});

function publicKey(did) {
  const alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
  assert(/^did:key:z[1-9A-HJ-NP-Za-km-z]{47}$/.test(did));
  let value = 0n;
  for (const char of did.slice(9)) value = value * 58n + BigInt(alphabet.indexOf(char));
  const decoded = Buffer.from(value.toString(16).padStart(68, '0'), 'hex');
  assert.equal(decoded.length, 34);
  assert.equal(decoded.subarray(0, 2).toString('hex'), 'ed01');
  return createPublicKey({key: Buffer.concat([
    Buffer.from('302a300506032b6570032100', 'hex'), decoded.subarray(2)
  ]), format: 'der', type: 'spki'});
}

function verifyDigits(room, record, digits) {
  const signature = Buffer.from(record.sig, 'base64url');
  assert.equal(signature.length, 64);
  assert.equal(signature.toString('base64url'), record.sig, 'noncanonical signature');
  return ed25519Verify(null, Buffer.from(`${room}|${digits}|${record.text}`),
    publicKey(record.from), signature);
}

function status(room, record) {
  if (record.sig === undefined) return 'unverifiable';
  if (typeof record.nonce === 'number' && !Number.isSafeInteger(record.nonce)) return 'invalid';
  if (!/^[0-9]{1,19}$/.test(String(record.nonce))) return 'invalid';
  return verifyDigits(room, record, String(record.nonce)) ? 'verified' : 'invalid';
}

const translation = {valid: 'verified', invalid: 'invalid', absent: 'unverifiable',
  not_reverifiable: 'unverifiable'};
const counts = {verified: 0, invalid: 0, unverifiable: 0};
let controls = 0;
assert.equal(corpus.cases.length, 11);
for (const item of corpus.cases) {
  const {room, record} = item;
  const result = status(room, record);
  assert.equal(result, translation[item.expected.signature], item.id);
  assert.equal(item.expected.authority, 'none');
  assert.equal(item.expected.automatic_action, false);
  counts[result]++;
  if (result !== 'verified') continue;
  assert.equal(status(room, {...record, text: record.text + ' altered'}), 'invalid');
  assert.equal(status(room + '-different', record), 'invalid');
  assert.equal(status(room, {...record, nonce: String(BigInt(record.nonce) + 1n)}), 'invalid');
  assert.equal(status(room, {...record, seq: record.seq + 10000, ts: 'changed unsigned ts'}), 'verified');
  const relabelled = {...item, generation: item.generation + 1};
  assert.equal(status(relabelled.room, relabelled.record), 'verified');
  controls += 5;
}

const exact = corpus.cases.find(item => item.id === 'large-numeric-nonce');
const rounded = JSON.parse(raw.toString('utf8')).cases.find(item => item.id === exact.id);
assert.equal(exact.record.nonce, '1000000000000000001');
assert.equal(typeof rounded.record.nonce, 'number');
assert.equal(Number.isSafeInteger(rounded.record.nonce), false);
assert.equal(String(rounded.record.nonce), '1000000000000000000');
assert.equal(verifyDigits(exact.room, exact.record, exact.record.nonce), true);
assert.equal(verifyDigits(rounded.room, rounded.record, String(rounded.record.nonce)), false);
assert.equal(status(rounded.room, rounded.record), 'invalid');
assert.deepEqual(counts, {verified: 6, invalid: 2, unverifiable: 3});
assert.equal(controls, 30);
console.log(JSON.stringify({fixture_sha256: expectedHash, node: process.version,
  cases_matched: 11, counts, controls_passed: controls,
  rounded_number_rejected: true,
  scope: 'Signature evidence only, not authority, trusted freshness, replay policy or settlement'}));
