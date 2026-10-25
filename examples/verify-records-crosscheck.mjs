// Companion to compatibility_pack.py. Inputs are bounded, Python-strict-parsed
// case packets, not a general JSON parser or consumer authorization policy.
import assert from 'node:assert/strict';
import {createHash, createPublicKey, verify} from 'node:crypto';
import {readFileSync} from 'node:fs';

const raw = readFileSync(0);
assert(raw.length <= 2 * 1024 * 1024, 'input too large');
assert.equal(JSON.parse('1000000000000000001', (_k, _v, c) => c?.source),
  '1000000000000000001', 'Node needs JSON source-token support');
const packet = JSON.parse(raw.toString('utf8'), (key, value, context) => {
  if (key !== 'nonce' || typeof value !== 'number') return value;
  assert(/^[0-9]{1,19}$/.test(context.source), 'invalid numeric nonce token');
  return context.source;
});
assert(packet.schema === 'flop-cross-client-cases-v1');
assert(Array.isArray(packet.cases) && packet.cases.length <= 200);
const alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';

function key(did) {
  assert(typeof did === 'string' && /^did:key:z[1-9A-HJ-NP-Za-km-z]{47}$/.test(did));
  let n = 0n;
  for (const c of did.slice(9)) n = 58n * n + BigInt(alphabet.indexOf(c));
  const bytes = Buffer.from(n.toString(16).padStart(68, '0'), 'hex');
  assert(bytes.length === 34 && bytes.subarray(0, 2).toString('hex') === 'ed01');
  return createPublicKey({key: Buffer.concat([
    Buffer.from('302a300506032b6570032100', 'hex'), bytes.subarray(2)
  ]), type: 'spki', format: 'der'});
}

function status(room, r) {
  if (!r || typeof r !== 'object') return 'invalid';
  if (r.sig === undefined || r.sig === null) return 'unverifiable';
  if ((typeof r.nonce !== 'string' && typeof r.nonce !== 'number') ||
      (typeof r.nonce === 'number' && !Number.isSafeInteger(r.nonce)) ||
      !/^[0-9]{1,19}$/.test(String(r.nonce)) || typeof r.text !== 'string' ||
      typeof r.sig !== 'string' || !/^[A-Za-z0-9_-]{86}$/.test(r.sig)) return 'invalid';
  try {
    const sig = Buffer.from(r.sig, 'base64url');
    if (sig.length !== 64 || sig.toString('base64url') !== r.sig) return 'invalid';
    return verify(null, Buffer.from(`${room}|${r.nonce}|${r.text}`), key(r.from), sig)
      ? 'verified' : 'invalid';
  } catch { return 'invalid'; }
}

const rounded = JSON.parse(raw.toString('utf8'));
const results = packet.cases.map((c, i) => {
  assert(typeof c.id === 'string' && typeof c.room === 'string');
  const ordinary = rounded.cases[i].record;
  const unsafe = typeof ordinary.nonce === 'number' && !Number.isSafeInteger(ordinary.nonce);
  return {id: c.id, status: status(c.room, c.record),
    ordinary_parse_unsafe_nonce: unsafe,
    ordinary_parse_status: unsafe ? status(c.room, ordinary) : null};
});
console.log(JSON.stringify({node: process.version,
  input_sha256: createHash('sha256').update(raw).digest('hex'), results,
  scope: 'Signature parity only; metadata, delivery, authorization and settlement are not verified'}));
