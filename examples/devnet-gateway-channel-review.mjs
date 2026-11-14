/** Read-only cross-check of infinity-nashi's existing issue-172 channels.
 * Extends wyc4t's FLOP-EXP-001 raw-call binding method to a five-turn receipt
 * and a refund. No SDK, wallet, signer, enrollment or paid request is loaded.
 * RPC-supplied metadata, state, events and canonical/finalized claims are trusted.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';

const root = process.env.POLKADOT_PACKAGE_ROOT;
if (!root) throw Error('Set POLKADOT_PACKAGE_ROOT to a package.json with the pinned dependencies');
const req = createRequire(path.resolve(root));
const { TypeRegistry, Metadata } = req('@polkadot/types');
const { cryptoWaitReady, blake2AsU8a, sr25519Verify, decodeAddress } = req('@polkadot/util-crypto');
const { hexToU8a, u8aToHex, u8aConcat } = req('@polkadot/util');
for (const [name, version] of Object.entries({ '@polkadot/api': '17.0.2',
  '@polkadot/types': '17.0.2', '@polkadot/util': '14.0.3', '@polkadot/util-crypto': '14.0.3' })) {
  let directory = path.dirname(req.resolve(name));
  while (!fs.existsSync(path.join(directory, 'package.json'))
    || JSON.parse(fs.readFileSync(path.join(directory, 'package.json'), 'utf8')).name !== name) {
    const parent = path.dirname(directory);
    assert.notEqual(parent, directory, 'dependency package not found');
    directory = parent;
  }
  assert.equal(JSON.parse(fs.readFileSync(path.join(directory, 'package.json'), 'utf8')).version, version);
}
await cryptoWaitReady();
const GENESIS = '0x99c172c095340ace980631f9123544c6bebd4839f3437e463533422d8be2d631';
const GATEWAY = '5GsXb3TmNGixuEsbtixqHnqWr9UQJ2M8bkqBQWteNekgF98S';
const CASES = [
  ['0x5268b7bf61022185e0d52157479a27ba257cbd4bef7941ba14a16c1cf3167d00', 3576952,
    '0x531f55e4b8a60e9625d1ede12b089ece95cffc6324815cffafc558353a95d3e7', 'settle'],
  ['0xcd1bbf7d9e0dfadd197905f2d1933a7b7c2b294ecc8d1bfbe170f9e260ec7d04', 3567762,
    '0x9c96b3caa338eb433e609dfb5cc88177665a76a8159732299ee54ef3c4f50767', 'timeout'],
  ['0xbae57d3042014d701a57e0061997e74060d2e429fa27a1579eca6555f15f1700', null, null, null],
];
const bytes = hexToU8a;
const hex = u8aToHex;
const text = value => new TextEncoder().encode(value);
const hash = value => blake2AsU8a(value, 256);
const concat = u8aConcat;
const sha256 = value => createHash('sha256').update(value).digest('hex');
const integer = value => {
  assert.ok(typeof value === 'bigint' || typeof value === 'string'
    || (typeof value === 'number' && Number.isSafeInteger(value)));
  return BigInt(value);
};
function le(value, size) {
  let n = integer(value); assert.ok(n >= 0n && n < (1n << BigInt(size * 8)));
  const result = new Uint8Array(size);
  for (let i = 0; i < size; i++) { result[i] = Number(n & 255n); n >>= 8n; }
  return result;
}
// Explicit V3 layout from the released SDK transcript.js; no weaker fallback.
function leaf(cid, t) {
  assert.equal(t.leafVersion, 'V3');
  return hash(concat(bytes(cid), le(t.turnIndex, 4), bytes(t.hIn), bytes(t.hOut), le(t.gN, 16),
    bytes(t.decodePolicyHash), bytes(t.hIds), bytes(t.toplocCommitmentHash),
    le(t.minerRecvMs, 8), le(t.minerDoneMs, 8), le(t.latencyMs, 8)));
}
function receipt(cid, a, payable) {
  return concat(text('FLOP/COMPUTE_CHANNEL/RECEIPT'), new Uint8Array([1]), bytes(cid),
    bytes(a.final_root), le(a.aggregate_gn, 16), le(payable, 16));
}
function readBounded(file) {
  assert.ok(!fs.lstatSync(file).isSymbolicLink(), 'regular file required');
  const fd = fs.openSync(file, 'r');
  try {
    const stat = fs.fstatSync(fd); assert.ok(stat.isFile() && stat.size <= 6 * 1024 * 1024);
    const buffer = Buffer.alloc(stat.size + 1); let total = 0;
    while (total < buffer.length) {
      const n = fs.readSync(fd, buffer, total, buffer.length - total, null);
      if (!n) break;
      total += n;
    }
    assert.ok(total <= stat.size, 'input grew during read'); return buffer.subarray(0, total);
  } finally { fs.closeSync(fd); }
}

function review(f) {
  assert.equal(f.genesis, GENESIS);
  assert.match(f.anchor, /^0x[0-9a-f]{64}$/);
  assert.ok(Number.isSafeInteger(f.blockNumber) && f.blockNumber >= CASES[0][1]);
  assert.equal(f.channels.length, CASES.length);
  const rows = [];
  for (const [cid, height, blockHash, method] of CASES) {
    const matches = f.channels.filter(row => row.channelId === cid);
    assert.equal(matches.length, 1); const row = matches[0]; const c = row.channel;
    assert.equal(row.present, true); assert.ok(c);
    const derived = hash(concat(text('FLOP/COMPUTE_CHANNEL/ID'), new Uint8Array([1]),
      bytes(GENESIS), decodeAddress(c.agent), decodeAddress(c.miner), le(c.nonce, 8)));
    assert.equal(hex(derived), cid);
    assert.deepEqual(c.state, { closed: null });
    const result = { channelId: cid, agent: c.agent, state: 'closed',
      lockedComputeConsumed: c.lockedComputeConsumed, transcriptRef: c.transcriptRef,
      terminalObservation: 'not_captured', credit: 'not_determined' };
    if (method) {
      assert.equal(c.agent, GATEWAY);
      const t = row.transition; assert.equal(t.blockHash, blockHash); assert.equal(t.blockNumber, height);
      assert.equal(t.extrinsicIndex, 3);
      assert.equal(sha256(Buffer.from(t.metadataHex.slice(2), 'hex')), t.metadataSha256);
      const registry = new TypeRegistry(); registry.setMetadata(new Metadata(registry, t.metadataHex));
      const ext = registry.createType('Extrinsic', t.extrinsicHex);
      const header = registry.createType('Header', t.header);
      assert.equal(hex(ext.toU8a()), t.extrinsicHex);
      assert.equal(ext.hash.toHex(), t.extrinsicHash);
      assert.equal(header.hash.toHex(), blockHash); assert.equal(header.number.toNumber(), height);
      assert.deepEqual(ext.method.toJSON(), t.call);
      assert.equal(ext.signer.toString(), t.signer);
      assert.equal(ext.method.section, 'computeChannel'); assert.equal(ext.method.method, method);
      const a = ext.method.toJSON().args; assert.equal(a.channel_id, cid);
      // Event rows remain RPC-trusted observations, not authenticated by the call signature.
      const events = t.events.filter(e => e.phase?.applyExtrinsic === t.extrinsicIndex);
      assert.ok(events.some(e => e.section === 'system' && e.method === 'ExtrinsicSuccess'));
      const name = method === 'settle' ? 'Settled' : 'TimedOutRefunded';
      const terminals = events.filter(e => e.section === 'computeChannel' && e.method === name);
      assert.equal(terminals.length, 1); const event = terminals[0]; assert.equal(event.data[0], cid);
      result.blockNumber = height; result.extrinsicIndex = t.extrinsicIndex;
      result.blockEventIndex = event.index;
      result.extrinsicEventOrdinal = events.findIndex(e => e === event);
      result.terminalObservation = name;
      if (method === 'settle') {
        assert.equal(t.signer, c.miner);
        assert.equal(a.verified_turns.length, 5); assert.equal(a.aggregate_gn, 4163);
        assert.equal(a.verified_turns.reduce((sum, turn) => sum + integer(turn.gN), 0n), integer(a.aggregate_gn));
        for (const [index, turn] of a.verified_turns.entries()) {
          assert.equal(turn.turnIndex, index); const h = leaf(cid, turn);
          assert.ok(sr25519Verify(h, bytes(turn.enclaveSig), bytes(c.enclaveKey)));
          let merkle = h;
          for (const [sibling, left] of turn.merklePath) {
            assert.equal(typeof left, 'boolean'); assert.equal(bytes(sibling).length, 32);
            merkle = hash(left ? concat(bytes(sibling), merkle) : concat(merkle, bytes(sibling)));
          }
          assert.equal(hex(merkle), a.final_root);
        }
        assert.ok(sr25519Verify(receipt(cid, a, c.escrow), bytes(a.agent_receipt_sig), bytes(c.agentKey)));
        assert.equal(integer(event.data[3]), integer(a.aggregate_gn)); assert.equal(event.data[4], true);
        const audit = events.find(e => e.section === 'computeChannel' && e.method === 'AuditFeeEarmarked' && e.data[0] === cid);
        assert.ok(audit); assert.equal(integer(c.escrow), integer(event.data[1]) + integer(audit.data[1]));
        result.minerPaidRaw = String(integer(event.data[1]));
        result.auditEarmarkRaw = String(integer(audit.data[1]));
        result.aggregateGn = String(integer(a.aggregate_gn));
        result.signedTurns = a.verified_turns.length;
      } else {
        assert.equal(t.signer, c.agent); assert.equal(integer(event.data[1]), integer(c.escrow));
        result.refundedRaw = String(integer(event.data[1]));
      }
    }
    rows.push(result);
  }
  return { scope: 'RPC-trusted observations; receipt/session signatures checked, outer transaction signature and independent finality not checked',
    anchor: f.anchor, blockNumber: f.blockNumber, channels: rows,
    perRequestReconciliation: 'not_performed', airdropAllocation: 'not_determined' };
}

async function capture(file) {
  const { ApiPromise, HttpProvider } = req('@polkadot/api'); let api;
  try {
    api = await ApiPromise.create({ provider: new HttpProvider('https://rpc.devnet.flop.network', {}, 8000), noInitWarn: true });
    assert.equal(api.genesisHash.toHex(), GENESIS);
    const anchor = (await api.rpc.chain.getFinalizedHead()).toHex();
    const at = await api.at(anchor); const header = await api.rpc.chain.getHeader(anchor);
    const f = { capturedAt: new Date().toISOString(), genesis: GENESIS, anchor,
      blockNumber: header.number.toNumber(), channels: [] };
    for (const [cid, height, blockHash] of CASES) {
      const state = await at.query.computeChannel.channels(cid);
      const row = { channelId: cid, present: state.isSome, channel: state.toJSON() };
      if (height) {
        assert.equal((await api.rpc.chain.getBlockHash(height)).toHex(), blockHash);
        const block = await api.rpc.chain.getBlock(blockHash); const hist = await api.at(blockHash);
        const ext = block.block.extrinsics[3]; const metadataHex = (await api.rpc.state.getMetadata(blockHash)).toHex();
        row.transition = { blockNumber: height, blockHash, header: block.block.header.toJSON(),
          extrinsicIndex: 3, extrinsicHex: ext.toHex(), extrinsicHash: ext.hash.toHex(),
          signer: ext.signer.toString(), call: ext.method.toJSON(), metadataHex,
          metadataSha256: sha256(Buffer.from(metadataHex.slice(2), 'hex')),
          events: (await hist.query.system.events()).map((e, index) => ({ index, phase: e.phase.toJSON(),
            section: e.event.section, method: e.event.method, data: e.event.data.toJSON() }))
            .filter(e => e.phase?.applyExtrinsic === 3) };
      }
      f.channels.push(row);
    }
    review(f); // No invalid positive is saved as a successful capture.
    const raw = JSON.stringify(f, null, 2) + '\n'; assert.ok(Buffer.byteLength(raw) <= 6 * 1024 * 1024);
    const target = path.resolve(file);
    const base = path.resolve('.private/readiness');
    assert.ok(target.startsWith(base + path.sep), 'capture belongs inside .private/readiness');
    fs.mkdirSync(path.dirname(target), { recursive: true, mode: 0o700 });
    assert.equal(fs.realpathSync(path.dirname(target)), path.dirname(target), 'symlink directory refused');
    fs.writeFileSync(target, raw, { mode: 0o600, flag: 'wx' }); return Buffer.from(raw);
  } finally { if (api) await api.disconnect(); }
}

const [mode, file, ...extra] = process.argv.slice(2);
assert.ok(['--file', '--live'].includes(mode) && file && extra.length === 0,
  'Use --file SAVED_CAPTURE or --live NEW_PRIVATE_CAPTURE');
const deadline = setTimeout(() => { console.error('read-only review deadline'); process.exit(2); }, 55000);
try {
  const raw = mode === '--live' ? await capture(file) : readBounded(file);
  const fixture = JSON.parse(raw.toString('utf8')); const report = review(fixture);
  assert.equal(report.channels[0].lockedComputeConsumed, 0);
  assert.ok(BigInt(report.channels[0].minerPaidRaw) > 0n);
  assert.equal(report.channels[2].terminalObservation, 'not_captured');
  assert.equal(report.channels[2].credit, 'not_determined');
  const mutations = [
    ['displayed raw-call arguments', f => { f.channels[0].transition.call.args.aggregate_gn++; }],
    ['displayed transaction hash', f => { f.channels[0].transition.extrinsicHash = '0x' + '00'.repeat(32); }],
    ['block header', f => { f.channels[0].transition.header.number = '0x1'; }],
    ['wrong channel owner', f => { f.channels[0].channel.agent = f.channels[2].channel.agent; }],
    ['missing refund terminal', f => { f.channels[1].transition.events = f.channels[1].transition.events.filter(e => e.method !== 'TimedOutRefunded'); }],
    ['terminal in wrong extrinsic', f => { f.channels[1].transition.events.find(e => e.method === 'TimedOutRefunded').phase.applyExtrinsic = 2; }],
    ['refund amount', f => { f.channels[1].transition.events.find(e => e.method === 'TimedOutRefunded').data[1] = '1'; }],
    ['missing channel is not zero', f => { f.channels[2].present = false; f.channels[2].channel = null; }],
  ];
  for (const [name, change] of mutations) {
    const f = structuredClone(fixture); change(f); assert.throws(() => review(f), undefined, name);
  }
  // Cryptographic negatives use the raw-decoded settlement, not a rewritten display object.
  const c = fixture.channels[0].channel; const t = fixture.channels[0].transition;
  const registry = new TypeRegistry(); registry.setMetadata(new Metadata(registry, t.metadataHex));
  const a = registry.createType('Extrinsic', t.extrinsicHex).method.toJSON().args;
  const changedTurn = { ...a.verified_turns[0], hOut: '0x' + '00'.repeat(32) };
  assert.equal(sr25519Verify(leaf(CASES[0][0], changedTurn), bytes(a.verified_turns[0].enclaveSig), bytes(c.enclaveKey)), false);
  assert.equal(sr25519Verify(receipt(CASES[0][0], a, integer(c.escrow) + 1n), bytes(a.agent_receipt_sig), bytes(c.agentKey)), false);
  console.log(JSON.stringify({ captureSha256: sha256(raw), positive: 'passed', negativeControls: mutations.length + 2, ...report }, null, 2));
} finally { clearTimeout(deadline); }
