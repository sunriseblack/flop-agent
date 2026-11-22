// Read fixed historical devnet records for the Yellow Paper #293 comparison.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');
const { createHash } = require('node:crypto');

const GENESIS = '0x99c172c095340ace980631f9123544c6bebd4839f3437e463533422d8be2d631';
const PEAK_IDS_SHA256 = '31b8e4874b2afd3a33fd63ca282e530deebeddd2e38c879c56cc5b3e30c8210a';
const CHANNEL = '0x63357101e72f3f015a76e1d4186867f99f2672e6f33cf724053c2856fbe0bbfb';
const BLOCKS = [
  [3858556, '0x9b839f96714f2c517159026b375d314fb5fdcf27b4cc4d8d690d3156f4d840cf'],
  [3924489, '0x3f1f385a3f192a4f18a70d9ac1e9b0e3b8df039cf42c0cd12487908ac662ecf6', 'ChannelOpened'],
  [3924510, '0x08d555f506d974471858ba4d175f7cedb1f1b0b81da19ef0cbbdd0fc6102fdd6', 'EscrowToppedUp'],
  [3925389, '0xcc3e5393c9fbd2c888390f544ef32f1feed23296da156ee5b60ce149abf2c5b0', 'Settled'],
  [4234248, '0xa0c66c0348fe0877b327eba2bb3967df4c50f4e36bea41032e24c54a0d708568'],
];

async function main() {
  const [file, ...extra] = process.argv.slice(2);
  assert.equal(extra.length, 0, 'usage: node escrow_turnover_anchors.cjs [offline-replay.json]');
  let ids;
  if (file) {
    ids = JSON.parse(fs.readFileSync(file, 'utf8')).peak_channel_ids;
    assert.ok(Array.isArray(ids) && ids.length === 56, 'expected 56 peak channels');
    assert.equal(createHash('sha256').update(ids.join('\n') + '\n').digest('hex'), PEAK_IDS_SHA256);
  }
  const load = process.env.POLKADOT_PACKAGE_ROOT
    ? createRequire(path.resolve(process.env.POLKADOT_PACKAGE_ROOT)) : require;
  const { ApiPromise, HttpProvider } = load('@polkadot/api');
  const api = await ApiPromise.create({
    provider: new HttpProvider('https://rpc.devnet.flop.network', {}, 9000), noInitWarn: true,
  });
  try {
    assert.equal(api.genesisHash.toHex(), GENESIS);
    const finalized = await api.rpc.chain.getFinalizedHead();
    assert.ok((await api.rpc.chain.getHeader(finalized)).number.toNumber() >= BLOCKS.at(-1)[0]);
    const results = [];
    for (const [height, expectedHash, eventName] of BLOCKS) {
      const hash = await api.rpc.chain.getBlockHash(height);
      assert.equal(hash.toHex(), expectedHash);
      const header = await api.rpc.chain.getHeader(hash);
      assert.equal(header.hash.toHex(), expectedHash);
      assert.equal(header.number.toNumber(), height);
      const at = await api.at(hash);
      const result = { height, hash: expectedHash, timestampMs: (await at.query.timestamp.now()).toNumber() };
      if (eventName) {
        const events = (await at.query.system.events()).filter(({ event }) =>
          event.section === 'computeChannel' && event.method === eventName && event.data[0].toHex() === CHANNEL);
        assert.equal(events.length, 1, 'expected the specific channel event');
        result.event = eventName;
        const event = events[0].event;
        const amounts = ['escrow', 'added', 'total', 'miner_paid'];
        result.amountsRaw = Object.fromEntries(event.meta.fields.map((f, i) =>
          [f.name.toString(), event.data[i].toString()]).filter(([name]) => amounts.includes(name)));
        const record = (await at.query.computeChannel.channels(CHANNEL)).unwrap();
        result.state = record.state.type;
        result.escrowRaw = record.escrow.toBigInt().toString();
      }
      if (ids && height === 3924489) {
        const states = await at.query.computeChannel.channels.multi(ids);
        assert.equal(states.length, ids.length);
        let sum = 0n;
        for (const state of states) {
          const record = state.unwrap();
          assert.equal(record.state.type, 'Open');
          sum += record.escrow.toBigInt();
        }
        result.cohortOpenChannels = states.length;
        result.cohortEscrowRaw = sum.toString();
      }
      results.push(result);
    }
    console.log(JSON.stringify(results, null, 2));
  } finally {
    await api.disconnect();
  }
}

const deadline = setTimeout(() => { console.error('devnet read deadline exceeded'); process.exit(2); }, 55_000);
main().catch(e => { console.error(e.message); process.exitCode = 1; }).finally(() => clearTimeout(deadline));
