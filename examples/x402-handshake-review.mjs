// Network issue 89: local Request/Response objects and inert payment doubles only.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import test from 'node:test';

assert.ok(process.env.SDK_REVIEW_DIR, 'Set SDK_REVIEW_DIR to a preserved package copy.');
const file = resolve(process.env.SDK_REVIEW_DIR, 'dist/x402.js');
const hash = createHash('sha256').update(await readFile(file)).digest('hex');
const allowed = new Set([
  'd2c20e26c9f8e48af6af3218c810b8f06b6bff2084ededa4ef2234ad4510bd8d',
  '77f98a052ece5882bcad6198ef5356b01d2e0b3ca6950ef5ea5074fc3d59760e',
  '1879257cc8e91da0b72c518ef06547f81b5209eafbf2a5121a94b3ad7d345042',
]);
assert.ok(allowed.has(hash), `Unexpected x402 module bytes: ${hash}`);
for (const [name, expected] of Object.entries({
  'index.js': 'be6bb8e56945e599d117734a2e056e613cacc066ef076402fc3f8c9f86bc6eff',
  'channel-types.js': 'b32c18f6f6774727979c3739d1cf07d9363bd0a1ff3933595225f7d7f7d7d0fb',
  'exact-flop.js': 'a4b325da39e61856bf795dab7e2e06fe7795067f2537ea92dd80e66a273eca6f',
})) {
  const data = await readFile(resolve(process.env.SDK_REVIEW_DIR, 'dist/x402-types', name));
  assert.equal(createHash('sha256').update(data).digest('hex'), expected,
    `Unexpected transitive x402 source: ${name}`);
}
const { X402Client, x402Fetch } = await import(pathToFileURL(file));
console.log(JSON.stringify({ module_sha256: hash, node: process.version,
  platform: process.platform, transport: 'in-process fetch double', real_payments: 0 }));
const url = 'https://fixture.invalid/inference';
const headers = {
  'x-payment-price': '1', 'x-payment-hash-lock': '0x' + '11'.repeat(32),
  'x-payment-timeout-blocks': '10', 'x-payment-destination': 'synthetic-destination',
};
const stream = () => new ReadableStream({ start(c) {
  c.enqueue(new TextEncoder().encode('fixture')); c.close();
} });

async function run(kind, config = {}) {
  const prior = globalThis.fetch;
  const observation = { attempts: 0, requests: [], payments: [], settlements: [] };
  const controller = new AbortController();
  const paymentClient = {
    async createHtlc(params) {
      observation.payments.push(params);
      if (config.creationError) throw new Error('synthetic creation refusal');
      return { htlcId: 'fixture-id', txHash: 'fixture-tx' };
    },
    async waitForSettlement(...args) {
      observation.settlements.push(args);
      return config.settlement === undefined ? { status: 'SETTLED' } : config.settlement;
    },
  };
  globalThis.fetch = async (address, opts = {}) => {
    observation.attempts++;
    assert.equal(address, url);
    opts.signal?.throwIfAborted();
    const request = new Request(address, { ...opts, duplex: 'half' });
    const body = await request.text();
    const proof = request.headers.get('X-Payment-Proof');
    observation.requests.push({ method: request.method, body, proof,
      contentType: request.headers.get('Content-Type'), fixture: request.headers.get('X-Fixture') });
    if (proof) return new Response('ok', { status: 200 });
    if (config.passthrough) return new Response('unpaid', { status: 200 });
    if (observation.requests.length > 1 && config.refuseRepeat) {
      return new Response('synthetic repeated challenge refusal', { status: 429 });
    }
    const challenge = { ...headers };
    if (config.changedPrice && observation.requests.length > 1) challenge['x-payment-price'] = '2';
    if (config.invalid) delete challenge['x-payment-price'];
    if (config.abort) controller.abort();
    return new Response('payment needed', { status: 402, headers: challenge });
  };
  try {
    const opts = { method: 'POST', body: config.body === undefined ? 'fixture' : config.body,
      headers: { 'X-Fixture': 'preserved' }, signal: controller.signal, ...config.options };
    try {
      const response = kind === 'class'
        ? await new X402Client({ gatewayUrl: url, flopClient: config.noClient ? undefined : paymentClient }).fetch(url, opts)
        : await x402Fetch(paymentClient, url, opts);
      observation.status = response.status;
    } catch (error) {
      observation.error = { name: error.name, code: error.code, message: error.message };
    }
    return observation;
  } finally {
    globalThis.fetch = prior;
  }
}

for (const kind of ['function', 'class']) {
  test(`${kind}: non-402 response remains unpaid passthrough`, async () => {
    const r = await run(kind, { passthrough: true });
    assert.equal(r.status, 200); assert.equal(r.attempts, 1); assert.equal(r.payments.length, 0);
  });
  test(`${kind}: uses the first challenge when repeated unpaid requests are refused`, async () => {
    const r = await run(kind, { refuseRepeat: true });
    assert.equal(r.status, 200); assert.equal(r.attempts, 2);
    assert.equal(r.requests.filter(x => !x.proof).length, 1); assert.equal(r.payments.length, 1);
    assert.deepEqual(JSON.parse(r.requests[1].proof), {
      hash_lock: '11'.repeat(32), htlc_id: 'fixture-id', tx_hash: 'fixture-tx',
    });
  });
  test(`${kind}: does not replace the first challenge with changed quote terms`, async () => {
    const r = await run(kind, { changedPrice: true });
    assert.equal(r.status, 200); assert.equal(r.payments[0].rewardFlop, 1); assert.equal(r.attempts, 2);
  });
  test(`${kind}: invalid challenge cannot trigger payment`, async () => {
    const r = await run(kind, { invalid: true });
    assert.ok(r.error); assert.equal(r.attempts, 1); assert.equal(r.payments.length, 0);
  });
  test(`${kind}: challenged ReadableStream is refused before mock payment`, async () => {
    const r = await run(kind, { body: stream() });
    assert.equal(r.error?.code, 'UNREPLAYABLE_BODY');
    assert.equal(r.attempts, 1); assert.equal(r.payments.length, 0); assert.equal(r.settlements.length, 0);
  });
  test(`${kind}: a non-402 streaming body remains ordinary passthrough`, async () => {
    const r = await run(kind, { body: stream(), passthrough: true });
    assert.equal(r.status, 200); assert.equal(r.attempts, 1); assert.equal(r.requests[0].body, 'fixture');
    assert.equal(r.payments.length, 0);
  });
  test(`${kind}: challenged async iterable is refused before mock payment`, async () => {
    async function* body() { yield new TextEncoder().encode('fixture'); }
    const r = await run(kind, { body: body() });
    assert.equal(r.error?.code, 'UNREPLAYABLE_BODY'); assert.equal(r.payments.length, 0);
  });
  test(`${kind}: abort after challenge is checked before payment`, async () => {
    const r = await run(kind, { abort: true });
    assert.equal(r.error?.name, 'AbortError'); assert.equal(r.payments.length, 0);
  });
  test(`${kind}: unsuccessful settlement cannot send payment proof`, async () => {
    const r = await run(kind, { settlement: { status: 'REFUNDED' } });
    assert.match(r.error?.message, /HTLC settlement failed/); assert.equal(r.payments.length, 1);
    assert.equal(r.requests.filter(x => x.proof).length, 0);
  });
  test(`${kind}: creation failure cannot send payment proof or restart the handshake`, async () => {
    const r = await run(kind, { creationError: true });
    assert.equal(r.error?.message, 'synthetic creation refusal'); assert.equal(r.attempts, 1);
    assert.equal(r.settlements.length, 0);
  });
  for (const [name, body] of [['string', 'fixture'], ['bytes', new Uint8Array([65, 66])],
    ['parameters', new URLSearchParams({ key: 'value' })]]) {
    test(`${kind}: replayable ${name} preserves method, body and ordinary headers`, async () => {
      const r = await run(kind, { body });
      assert.equal(r.status, 200); assert.equal(r.requests.length, 2);
      assert.equal(r.requests[0].body, r.requests[1].body);
      assert.equal(r.requests[1].method, 'POST'); assert.equal(r.requests[1].fixture, 'preserved');
      assert.equal(r.requests[1].contentType, r.requests[0].contentType);
    });
  }
}
test('class: a valid challenge without a payment client remains NO_CLIENT', async () => {
  const r = await run('class', { noClient: true });
  assert.equal(r.error?.code, 'NO_CLIENT'); assert.equal(r.attempts, 1); assert.equal(r.payments.length, 0);
});
test('function: caller payment identity, timeout and TEE requirements remain intact', async () => {
  const tee = 'synthetic-requirements';
  const r = await run('function', { options: { agent: 'fixture-agent', settlementTimeoutMs: 123,
    teeRequirements: tee } });
  assert.equal(r.status, 200); assert.equal(r.payments[0].agent, 'fixture-agent');
  assert.equal(r.payments[0].task.tee_requirements, tee); assert.equal(r.settlements[0][1], 123);
});
