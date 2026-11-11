/** Local response-contract review for pinned SDK releases and issue 71/72 candidates.
 * SDK_REVIEW_TARGET selects faucet or x402. SDK_REVIEW_DIR points to a caller's
 * unpacked package. The known module hash is checked before importing its code.
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { createServer } from 'node:http';

const target = process.env.SDK_REVIEW_TARGET;
const directory = process.env.SDK_REVIEW_DIR;
assert.ok(['faucet', 'x402'].includes(target) && directory,
  'Set SDK_REVIEW_TARGET=faucet|x402 and SDK_REVIEW_DIR to an unpacked package');
const expected = {
  faucet: [
    '8819278213c1d5078bbb97ac66aa98984ba2e334b2e742f8fd25a3cda766a507',
    '586ad8a1ed22a66d39c358c8d804445ccd5436d448dc390136ba3d55a744f164',
    'e1b8098ca5d18c9b425432c69aaa1580451b2b6636ffdca3284d2fb68f70d597',
    'f8c6992cc7a9dcf7f017bf0d9cdf5b534dd9629de0516be85b9c63e14cc66b59',
  ],
  x402: [
    'd2c20e26c9f8e48af6af3218c810b8f06b6bff2084ededa4ef2234ad4510bd8d',
    '28a836ffe1a9314c99536a56b1a289939daf8f8967230566b8c9028ef2676d04',
    '3efba4fb82b77ff207499e8ca3379b25574946ededfb0640d44f76accd4485d6',
    'c3500d148df8d7bed7f2aa72b2888d425c66d234b8054aa4b8c69d6f228ca899',
    '585456ea4765b2650fb2c7d5ba55f0e0b52e3300030f4ecbf8049e7bd268080e',
    'b746ff062ab1c2673f9768405ae6d9914d99a614c2300773def0e310c3542d18',
  ],
};
function readModule(file) {
  const info = fs.statSync(file);
  assert.ok(info.isFile() && info.size <= 128 * 1024, 'bounded regular module required');
  return fs.readFileSync(file);
}
const modulePath = path.resolve(directory, 'dist', target + '.js');
const moduleBytes = readModule(modulePath);
const moduleHash = createHash('sha256').update(moduleBytes).digest('hex');
assert.ok(expected[target].includes(moduleHash), 'module differs from reviewed artifact');
if (target === 'faucet') {
  const chain = readModule(path.resolve(directory, 'dist/chain.js'));
  assert.equal(createHash('sha256').update(chain).digest('hex'),
    'ac6eea3a61f4caeda6b24a8cff3344de5e377a562b117ad278a15f115ada64a9');
}
const sdk = await import(pathToFileURL(modulePath));
console.log(JSON.stringify({ target, module_sha256: moduleHash, node: process.version,
  platform: process.platform, arch: process.arch }));

async function usingServer(responses, inspect) {
  const calls = [];
  const server = createServer(async (request, response) => {
    let raw = '';
    for await (const chunk of request) raw += chunk;
    calls.push({ method: request.method, path: request.url, body: raw });
    const result = responses[Math.min(calls.length - 1, responses.length - 1)];
    if (result.truncate) {
      response.writeHead(200, { 'Content-Type': 'application/json', 'Content-Length': '1000' });
      response.write('{"partial":');
      setTimeout(() => response.destroy(), 25);
      return;
    }
    response.writeHead(result.status, { 'Content-Type': 'application/json', ...result.headers });
    response.end(typeof result.body === 'string' ? result.body : JSON.stringify(result.body ?? {}));
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  try {
    await inspect(`http://127.0.0.1:${server.address().port}`, calls);
  } finally {
    server.closeAllConnections();
    await new Promise(resolve => server.close(resolve));
  }
}

if (target === 'faucet') {
  const samples = [
    ['string error', { error: 'synthetic refusal' }, 'synthetic refusal'],
    ['plain text', 'plain refusal', 'plain refusal'],
    ['null error', { error: null }, '{"error":null}'],
    ['null JSON root', 'null', 'null'],
    ['object error', { error: { code: 'CAP' } }, '{"error":{"code":"CAP"}}'],
    ['array error', { error: ['CAP'] }, '{"error":["CAP"]}'],
    ['numeric error', { error: 7 }, '{"error":7}'],
    ['true error', { error: true }, '{"error":true}'],
    ['zero error', { error: 0 }, '{"error":0}'],
    ['false error', { error: false }, '{"error":false}'],
    ['empty string', { error: '' }, 'Faucet request failed: HTTP 429'],
    ['malformed JSON', '{invalid', '{invalid'],
  ];
  for (const lane of ['class', 'functional']) {
    for (const [name, body, error] of samples) {
      test(`${lane}: ${name} preserves a string error`, () => usingServer([
        { status: 429, body, headers: { 'Retry-After': '120' } },
      ], async (endpoint, calls) => {
        const config = { endpoint, maxRetries: 3, retryDelay: 1, timeout: 1000 };
        const result = lane === 'class'
          ? await new sdk.FaucetClient(config).fund('synthetic')
          : await sdk.requestFaucetFunding('synthetic', config);
        assert.equal(result.success, false);
        assert.equal(result.status, 429);
        assert.equal(calls.length, 1);
        assert.equal(typeof result.error, 'string');
        assert.equal(result.error, error);
      }));
    }
  }
} else {
  const client = endpoint => new sdk.X402Client({ gatewayUrl: endpoint,
    retry: { maxAttempts: 3, backoffMs: 0, maxBackoffMs: 0 } });
  const posts = [
    ['createChannel', '/x402/channels', { agentAddress: 'synthetic', balance: 2 },
      value => value.createChannel({ agentAddress: 'synthetic', balance: 2 })],
    ['depositToChannel', '/x402/channels/synthetic/deposit', { amount: 1 },
      value => value.depositToChannel('synthetic', 1)],
    ['closeChannel', '/x402/channels/synthetic/close', undefined,
      value => value.closeChannel('synthetic')],
    ['setSessionCap', '/x402/sessions/synthetic', { maxSpendFlop: 2, expiresAt: 0 },
      value => value.setSessionCap('synthetic', 2)],
    ['verifyPayment', '/x402/verify', { type: 'htlc', proof: { marker: 'synthetic' } },
      value => value.verifyPayment('htlc', { marker: 'synthetic' })],
  ];
  for (const [name, route, payload, invoke] of posts) {
    test(`${name}: success preserves one request and JSON payload`, () => usingServer([
      { status: 200, body: { marker: name } },
    ], async (endpoint, calls) => {
      assert.deepEqual(await invoke(client(endpoint)), { marker: name });
      assert.equal(calls.length, 1);
      assert.equal(calls[0].method, 'POST');
      assert.equal(calls[0].path, route);
      assert.equal(calls[0].body, payload === undefined ? '' : JSON.stringify(payload));
    }));
    test(`${name}: refusal throws once and preserves the response`, () => usingServer([
      { status: 403, body: { error: 'synthetic refusal' }, headers: { 'Retry-After': '120' } },
    ], async (endpoint, calls) => {
      let error;
      try { await invoke(client(endpoint)); } catch (caught) { error = caught; }
      assert.ok(error instanceof sdk.PaymentError);
      assert.equal(error.status, 403);
      assert.equal(error.code, 'HTTP_ERROR');
      assert.equal(error.response.headers.get('Retry-After'), '120');
      assert.deepEqual(await error.response.json(), { error: 'synthetic refusal' });
      assert.equal(calls.length, 1);
    }));
  }
  const gets = [
    ['getChannel', '/x402/channels/synthetic', value => value.getChannel('synthetic')],
    ['listChannels', '/x402/channels?agent=synthetic', value => value.listChannels('synthetic')],
    ['getSession', '/x402/sessions/synthetic', value => value.getSession('synthetic')],
    ['getSupportedChains', '/x402/chains', value => value.getSupportedChains()],
  ];
  for (const [name, route, invoke] of gets) {
    test(`${name}: transient read failure recovers with two GETs`, () => usingServer([
      { status: 503 }, { status: 200, body: { marker: name } },
    ], async (endpoint, calls) => {
      assert.deepEqual(await invoke(client(endpoint)), { marker: name });
      assert.equal(calls.length, 2);
      assert.ok(calls.every(call => call.method === 'GET' && call.path === route));
    }));
  }
  test('plain-text refusal remains readable without entering the error message', () => usingServer([
    { status: 403, body: '<html>synthetic proxy refusal</html>' },
  ], async (endpoint, calls) => {
    let error;
    try { await client(endpoint).getSession('synthetic'); } catch (caught) { error = caught; }
    assert.ok(error instanceof sdk.PaymentError);
    assert.equal(await error.response.text(), '<html>synthetic proxy refusal</html>');
    assert.ok(!error.message.includes('synthetic proxy refusal'));
    assert.equal(calls.length, 1);
  }));
  test('truncated successful POST body does not cause a replay', () => usingServer([
    { truncate: true },
  ], async (endpoint, calls) => {
    await assert.rejects(client(endpoint).depositToChannel('synthetic', 1));
    assert.equal(calls.length, 1);
  }));
  test('discarded GET body is cancelled before retry', async () => {
    const originalFetch = globalThis.fetch;
    let calls = 0;
    let cancelled = false;
    globalThis.fetch = async () => {
      calls++;
      if (calls === 1) {
        return new Response(new ReadableStream({ cancel() { cancelled = true; } }), { status: 503 });
      }
      assert.equal(cancelled, true);
      return Response.json({ marker: 'recovered' });
    };
    try {
      assert.deepEqual(await client('http://127.0.0.1:1').getChannel('synthetic'), { marker: 'recovered' });
      assert.equal(calls, 2);
    } finally {
      globalThis.fetch = originalFetch;
    }
  });
  // Adjacent control reported independently by almondous on network issue 72.
  test('rejected GET body cancellation still consumes one retry and recovers', async () => {
    const originalFetch = globalThis.fetch;
    let calls = 0;
    let cancelAttempts = 0;
    globalThis.fetch = async () => {
      calls++;
      if (calls === 1) {
        return new Response(new ReadableStream({ cancel() {
          cancelAttempts++;
          throw new Error('synthetic cancellation rejection');
        } }), { status: 503 });
      }
      assert.equal(cancelAttempts, 1);
      return Response.json({ marker: 'recovered after rejected cancellation' });
    };
    try {
      assert.deepEqual(await client('http://127.0.0.1:1').getChannel('synthetic'),
        { marker: 'recovered after rejected cancellation' });
      assert.equal(calls, 2);
      assert.equal(cancelAttempts, 1);
    } finally {
      globalThis.fetch = originalFetch;
    }
  });
  test('final GET refusal preserves the unread response without another fetch', async () => {
    const originalFetch = globalThis.fetch;
    let calls = 0;
    const response = new Response('synthetic terminal refusal', { status: 503 });
    globalThis.fetch = async () => { calls++; return response; };
    try {
      const value = new sdk.X402Client({ gatewayUrl: 'http://127.0.0.1:1',
        retry: { maxAttempts: 1, backoffMs: 0, maxBackoffMs: 0 } });
      await assert.rejects(value.getChannel('synthetic'), error => {
        assert.ok(error instanceof sdk.PaymentError);
        assert.equal(error.response, response);
        assert.equal(error.status, 503);
        assert.equal(response.bodyUsed, false);
        return true;
      });
      assert.equal(await response.text(), 'synthetic terminal refusal');
      assert.equal(calls, 1);
    } finally {
      globalThis.fetch = originalFetch;
    }
  });
}
