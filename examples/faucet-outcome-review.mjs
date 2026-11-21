// Inspected SDK releases: network/client labels and uncertain funding outcomes.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import test from 'node:test';

assert.ok(process.env.SDK_REVIEW_DIR, 'Set SDK_REVIEW_DIR to an inspected unpacked package.');
const root = resolve(process.env.SDK_REVIEW_DIR, 'dist');
const modulePath = resolve(root, 'faucet.js');
const digest = data => createHash('sha256').update(data).digest('hex');
const moduleHash = digest(await readFile(modulePath));
// Key each inspected module to the telemetry label expected from that release.
const reviewedLabels = new Map([
  ['546c798ab5772a34bd0f7dc40f8d75745c70d5f91485bb0bcfe881bbdca5ac42', null],
  ['2cb714f9cd3fb8ae1a8a46603d560dcda8078bab62fc78177a57eb22317b2215', null],
  ['dd9fc3b7ad76bf2aa317c748759a23cb627ef49f2f18117ac382bdea5f6dd040', 'flop-sdk-ts/0.7.2'],
  ['ae581cbc1bb9d5e2cf0f59528cbbf72205bb9e1b7e4e4abd1ceff55366d680db', 'flop-sdk-ts/0.7.2'],
  ['9dee13d2240cb124d2e0905e7ec212946d315d4c091b436bbe7d80cf134abb31', 'flop-sdk-ts/0.8.0'],
  ['9901fd4ff2fdb09852eccd8fd227d98b2a2d1cc0c4964019f4a0fde970e38a7f', 'flop-sdk-ts/0.8.0'],
]);
assert.ok(reviewedLabels.has(moduleHash), 'faucet module differs from reviewed bytes');
assert.equal(digest(await readFile(resolve(root, 'chain.js'))),
  'ac6eea3a61f4caeda6b24a8cff3344de5e377a562b117ad278a15f115ada64a9');
const sdk = await import(pathToFileURL(modulePath));
const expectedLabel = reviewedLabels.get(moduleHash);
const clientTagged = expectedLabel !== null;
if (clientTagged) assert.equal(sdk.FAUCET_CLIENT, expectedLabel);
console.log(JSON.stringify({ module_sha256: moduleHash, node: process.version,
  platform: process.platform, transport: 'in-process fetch double', real_requests: 0 }));

const endpoint = 'https://fixture.invalid/faucet';
const genesis = '0x' + '11'.repeat(32);
const txHash = '0x' + '22'.repeat(32);
const accepted = { success: true, amount: 25, txHash };
const api = { genesisHash: { toHex: () => genesis } };
const config = extra => ({ endpoint, network: 'devnet', timeout: 1000,
  maxRetries: 99, retryDelay: 0, ...extra });

async function usingFetch(responses, inspect) {
  const previous = globalThis.fetch;
  const calls = [];
  globalThis.fetch = async (url, options = {}) => {
    assert.ok(url === endpoint + '/fund' || url === endpoint + '/chain', 'unexpected URL');
    calls.push({ url, method: options.method ?? 'GET',
      body: options.body === undefined ? undefined : JSON.parse(options.body) });
    assert.ok(calls.length <= responses.length, 'unexpected retry');
    const response = responses[calls.length - 1];
    if (response instanceof Error) throw response;
    if (typeof response === 'function') return response();
    return Response.json(response.body, { status: response.status ?? 200,
      headers: response.headers });
  };
  try { return await inspect(calls); } finally { globalThis.fetch = previous; }
}

function invoke(lane, extra = {}) {
  const options = config(extra);
  return lane === 'class'
    ? new sdk.FaucetClient(options).fund('synthetic-address', 25)
    : sdk.requestFaucetFunding('synthetic-address', { ...options, amount: 25 });
}

for (const lane of ['class', 'functional']) {
  for (const network of ['devnet', 'local', 'testnet']) {
    // Reproduce almondous's issue-244 matrix, including ambiguous outcomes.
    for (const [name, response, outcome, success, status] of [
      ['accepted', { body: accepted }, 'accepted', true, 200],
      ['429 refusal', { status: 429, body: { error: 'synthetic refusal' } }, 'refused', false, 429],
      ['503 unknown', { status: 503, body: { error: 'synthetic failure' } }, 'unknown', false, 503],
      ['lost response', new TypeError('synthetic response loss'), 'unknown', false, undefined],
    ]) {
      test(`${lane}: configured ${network} survives ${name} metadata`, () =>
        usingFetch([response], async calls => {
          const result = await invoke(lane, { network });
          assert.equal(result.network, network);
          assert.equal(result.endpoint, endpoint);
          assert.equal(result.outcome, outcome);
          assert.equal(result.success, success);
          assert.equal(result.status, status);
          if (success) {
            assert.equal(result.txHash, txHash);
            assert.equal(result.amount, 25);
          }
          assert.equal(calls.length, 1);
          assert.equal(calls[0].method, 'POST');
          assert.deepEqual(calls[0].body, { address: 'synthetic-address', amount: 25,
            ...(clientTagged ? { client: sdk.FAUCET_CLIENT } : {}) });
        }));
    }
  }
  test(`${lane}: omitted network retains the existing testnet default`, () =>
    usingFetch([{ body: accepted }], async calls => {
      const result = await invoke(lane, { network: undefined });
      assert.equal(result.network, 'testnet');
      assert.equal(result.outcome, 'accepted');
      assert.equal(calls.length, 1);
    }));
  for (const status of [400, 403, 429, 408, 503]) {
    test(`${lane}: HTTP ${status} preserves uncertainty/refusal and sends once`, () =>
      usingFetch([{ status, body: { error: 'synthetic refusal' },
        headers: { 'Retry-After': '5' } }], async calls => {
        const result = await invoke(lane);
        assert.equal(result.success, false);
        assert.equal(result.status, status);
        assert.equal(result.outcome, status === 408 || status >= 500 ? 'unknown' : 'refused');
        assert.equal(result.retryAfterSeconds, 5);
        assert.equal(typeof result.error, 'string');
        assert.equal(calls.length, 1);
      }));
  }
  const malformed = [
    ['null root', () => Response.json(null)],
    ['array root', () => Response.json([])],
    ['malformed JSON', () => new Response('{bad')],
    ['missing hash', () => Response.json({ success: true, amount: 25 })],
    ['invalid amount', () => Response.json({ success: true, amount: -1, txHash })],
  ];
  for (const [name, response] of malformed) {
    test(`${lane}: ${name} remains unknown without a retry`, () =>
      usingFetch([response], async calls => {
        const result = await invoke(lane);
        assert.equal(result.success, false);
        assert.equal(result.outcome, 'unknown');
        assert.equal(typeof result.error, 'string');
        assert.equal(calls.length, 1);
      }));
  }
  test(`${lane}: lost response remains unknown without a retry`, () =>
    usingFetch([new TypeError('synthetic response loss')], async calls => {
      const result = await invoke(lane);
      assert.equal(result.success, false);
      assert.equal(result.outcome, 'unknown');
      assert.equal(calls.length, 1);
    }));
}

if (clientTagged) for (const lane of ['class', 'functional']) {
  for (const [name, response, outcome] of [
    ['accepted', { body: accepted }, 'accepted'],
    ['429 refusal', { status: 429, body: { error: 'synthetic refusal' } }, 'refused'],
    ['503 unknown', { status: 503, body: { error: 'synthetic failure' } }, 'unknown'],
    ['lost response', new TypeError('synthetic response loss'), 'unknown'],
  ]) {
    test(`${lane}: explicit telemetry client survives ${name}`, () =>
      usingFetch([response], async calls => {
        const result = await invoke(lane, { client: 'review-fixture/v1' });
        assert.equal(result.outcome, outcome);
        assert.equal(result.network, 'devnet');
        assert.equal(calls.length, 1);
        assert.deepEqual(calls[0].body, { address: 'synthetic-address', amount: 25,
          client: 'review-fixture/v1' });
      }));
  }
  test(`${lane}: explicit empty telemetry client preserves nullish-default semantics`, () =>
    usingFetch([{ body: accepted }], async calls => {
      const result = await invoke(lane, { client: '' });
      assert.equal(result.outcome, 'accepted');
      assert.equal(calls.length, 1);
      assert.deepEqual(calls[0].body, { address: 'synthetic-address', amount: 25, client: '' });
    }));
}

for (const [name, chain] of [
  ['different genesis', { network: 'devnet', genesisHash: '0x' + '33'.repeat(32) }],
  ['different network', { network: 'testnet', genesisHash: genesis }],
  ['incomplete identity', { network: 'devnet' }],
]) {
  test(`detailed: ${name} prevents the funding POST`, () =>
    usingFetch([{ body: chain }], async calls => {
      const result = await sdk.fundFromFaucetDetailed(api, 'synthetic-address', config());
      assert.equal(result.status, 'unavailable');
      assert.equal(calls.length, 1);
      assert.equal(calls[0].method, 'GET');
    }));
}

test('detailed: accepted metadata is still not an attributable grant', () =>
  usingFetch([{ body: { network: 'devnet', genesisHash: genesis } }, { body: accepted }],
    async calls => {
      let balanceReads = 0;
      const observedApi = { ...api, query: { system: { account() {
        balanceReads++;
        throw new Error('balance must not substitute for a grant receipt');
      } } } };
      const result = await sdk.fundFromFaucetDetailed(observedApi, 'synthetic-address', config());
      assert.equal(result.status, 'unknown');
      assert.equal(result.request.outcome, 'accepted');
      assert.equal(result.request.txHash, txHash);
      assert.equal(balanceReads, 0);
      assert.deepEqual(calls.map(c => c.method), ['GET', 'POST']);
    }));

for (const [status, expected] of [[429, 'refused'], [503, 'unknown']]) {
  test(`detailed: HTTP ${status} preserves request outcome without retrying`, () =>
    usingFetch([{ body: { network: 'devnet', genesisHash: genesis } },
      { status, body: { error: 'synthetic refusal' } }], async calls => {
      const result = await sdk.fundFromFaucetDetailed(api, 'synthetic-address', config());
      assert.equal(result.status, expected);
      assert.equal(result.request.status, status);
      assert.equal(calls.length, 2);
    }));
}

test('detailed: a profile without a faucet is refused without a request', () =>
  usingFetch([], async calls => {
    const result = await sdk.fundFromFaucetDetailed(api, 'synthetic-address', config({ network: 'mainnet' }));
    assert.equal(result.status, 'refused');
    assert.equal(calls.length, 0);
  }));

test('deprecated boolean false does not imply no funding POST happened', () =>
  usingFetch([{ body: { network: 'devnet', genesisHash: genesis } }, { body: accepted }],
    async calls => {
      assert.equal(await sdk.fundFromFaucet(api, 'synthetic-address', config()), false);
      assert.deepEqual(calls.map(c => c.method), ['GET', 'POST']);
    }));
