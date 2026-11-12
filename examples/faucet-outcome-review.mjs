// SDK 0.6.0: network labels and uncertain funding outcomes, with inert fetch only.
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
const allowed = new Set([
  '546c798ab5772a34bd0f7dc40f8d75745c70d5f91485bb0bcfe881bbdca5ac42',
  '2cb714f9cd3fb8ae1a8a46603d560dcda8078bab62fc78177a57eb22317b2215',
]);
assert.ok(allowed.has(moduleHash), 'faucet module differs from reviewed bytes');
assert.equal(digest(await readFile(resolve(root, 'chain.js'))),
  'ac6eea3a61f4caeda6b24a8cff3344de5e377a562b117ad278a15f115ada64a9');
const sdk = await import(pathToFileURL(modulePath));
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
    test(`${lane}: configured ${network} survives in accepted metadata`, () =>
      usingFetch([{ body: accepted }], async calls => {
        const result = await invoke(lane, { network });
        assert.equal(result.network, network);
        assert.equal(result.endpoint, endpoint);
        assert.equal(result.outcome, 'accepted');
        assert.equal(result.success, true);
        assert.equal(result.txHash, txHash);
        assert.equal(calls.length, 1);
        assert.equal(calls[0].method, 'POST');
      }));
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
  test(`${lane}: configured network is retained on refusal too`, () =>
    usingFetch([{ status: 429, body: { error: 'synthetic refusal' } }], async calls => {
      const result = await invoke(lane, { network: 'local' });
      assert.equal(result.network, 'local');
      assert.equal(result.outcome, 'refused');
      assert.equal(calls.length, 1);
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
