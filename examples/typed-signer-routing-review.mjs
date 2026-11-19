/** Recording-boundary review of almondous's reconstructed #337 v1.
 * Pinned public helper code only. No real keys, keystore IO, crypto or SDK.
 * This does not execute the peer's nine real-crypto fixture groups.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createHash } from 'node:crypto';
import vm from 'node:vm';

const [originalFile, candidateFile, ...extra] = process.argv.slice(2);
assert.ok(originalFile && candidateFile && extra.length === 0,
  'Use ORIGINAL_HELPER.mjs CANDIDATE_HELPER.mjs from the pinned reconstructed v1');
const hashes = [
  '9d1590c7474222d1676d802ce03256a1b06ff0c2993b5dde454e968601a27069',
  '58595a2020d76f745accacf8f4c16eadf79eba5636cf2fb5e627a41398742f0c',
];
function readPinned(file, expected) {
  assert.ok(file.endsWith('.mjs'), 'expected a public helper module');
  const stat = fs.statSync(file); assert.ok(stat.isFile() && stat.size <= 16384);
  const raw = fs.readFileSync(file);
  assert.equal(createHash('sha256').update(raw).digest('hex'), expected, 'public helper pin mismatch');
  return raw.toString('utf8');
}
const sources = [readPinned(originalFile, hashes[0]), readPinned(candidateFile, hashes[1])];
const plain = value => JSON.parse(JSON.stringify(value));
const rpc = 'mock://no-network';

function recording(source, { keystoreType = 'ed25519', passwordPresent = true } = {}) {
  const trace = { constructors: [], uris: [], reads: [], decodes: [], encodes: 0, pairDecodes: 0, sdk: [] };
  const envName = 'FIXTURE:ENV';
  const env = passwordPresent ? { [envName]: 'public-recording-marker' } : {};
  function pair(type, marker) {
    return { type, marker,
      decodePkcs8(password) { trace.decodes.push(password); },
      encodePkcs8() { trace.encodes++; return 'opaque-recording-marker'; },
    };
  }
  class Keyring {
    constructor(options) { this.type = options.type; trace.constructors.push(plain(options)); }
    addFromUri(uri) { trace.uris.push(uri); return pair(this.type, uri); }
    addFromJson(json) { return pair(this.type, json.marker); }
  }
  const modules = {
    '@polkadot/keyring': { Keyring },
    '@polkadot/util-crypto': { cryptoWaitReady: async () => true },
    '@polkadot/keyring/pair/decode': {
      decodePair(_password, encoded, encoding) {
        assert.equal(encoded, 'opaque-recording-marker'); assert.equal(encoding, 'none');
        trace.pairDecodes++;
        // Two marker bytes, not valid key material or a cryptographic operation.
        return { secretKey: Uint8Array.of(17), publicKey: Uint8Array.of(34) };
      },
    },
    'node:fs/promises': { readFile: async (file, encoding) => {
      trace.reads.push({ file, encoding });
      return JSON.stringify({ marker: 'public-json-marker', encoding: { content: ['pkcs8', keystoreType] } });
    } },
    '../sdk-stub.mjs': {
      FlopClient: {
        create: async opts => { trace.sdk.push('uri'); return { route: 'uri', opts }; },
        createWithKeypair: async (endpoint, keypair) => {
          trace.sdk.push('pair'); return { route: 'pair', endpoint, keypair };
        },
      },
      connectFlopApi: () => { throw Error('network boundary must not be called'); },
    },
  };
  let code = source.replace(/import\("([^"]+)"\)/g, (_match, name) => {
    assert.ok(Object.hasOwn(modules, name), 'unexpected import in pinned source');
    return `__import(${JSON.stringify(name)})`;
  });
  assert.ok(!/\bimport\s*\(/.test(code), 'unreplaced import');
  const exports = '\nexport {loadKeystore, sr25519KeyHex, agentSignerConfig, createClient};\n';
  assert.ok(code.endsWith(exports), 'unexpected helper export shape');
  code = code.slice(0, -exports.length);
  const api = vm.runInNewContext(`(() => { ${code}\nreturn {loadKeystore, sr25519KeyHex, agentSignerConfig, createClient}; })()`,
    { __import: async name => modules[name], process: { env }, Buffer }, { timeout: 1000 });
  return { api, trace, envName };
}
const checks = [];
async function check(name, action) { await action(); checks.push({ name, passed: true }); }

await check('released factory forwards typed-looking URI as legacy data', async () => {
  const r = recording(sources[0]); const input = 'ed25519:PUBLIC_MARKER';
  const got = await r.api.createClient(rpc, input);
  assert.equal(got.route, 'uri'); assert.equal(got.opts.signer, input);
  assert.equal(r.trace.constructors.length, 0);
});
for (const type of ['ed25519', 'sr25519']) {
  await check(`candidate routes explicit ${type} through a pair`, async () => {
    const r = recording(sources[1]); const config = await r.api.agentSignerConfig(type + ':PUBLIC_MARKER');
    const got = await r.api.createClient(rpc, type + ':PUBLIC_MARKER');
    assert.equal(config.keypair.type, type); assert.equal(got.route, 'pair');
    assert.equal(got.keypair.type, type); assert.equal(got.keypair.marker, 'PUBLIC_MARKER');
    assert.deepEqual(r.trace.uris, ['PUBLIC_MARKER', 'PUBLIC_MARKER']);
    assert.deepEqual(r.trace.constructors, [{ type, ss58Format: 42 }, { type, ss58Format: 42 }]);
  });
}
await check('unprefixed URI remains a passthrough', async () => {
  const a = recording(sources[0]), b = recording(sources[1]);
  assert.deepEqual(plain(await a.api.createClient(rpc, 'PUBLIC_MARKER')), plain(await b.api.createClient(rpc, 'PUBLIC_MARKER')));
  assert.deepEqual(plain(await a.api.agentSignerConfig('PUBLIC_MARKER')), plain(await b.api.agentSignerConfig('PUBLIC_MARKER')));
  assert.equal(b.trace.constructors.length, 0);
});
await check('all empty typed URIs fail before constructing a pair or calling SDK', async () => {
  for (const type of ['ed25519', 'sr25519']) {
    const r = recording(sources[1]);
    await assert.rejects(r.api.agentSignerConfig(type + ':'), /must not be empty/);
    await assert.rejects(r.api.createClient(rpc, type + ':'), /must not be empty/);
    assert.equal(r.trace.constructors.length, 0); assert.equal(r.trace.sdk.length, 0);
  }
});
await check('undefined, null and empty no-signer routing stay unchanged', async () => {
  for (const value of [undefined, null, '']) {
    const a = recording(sources[0]), b = recording(sources[1]);
    assert.deepEqual(plain(await a.api.createClient(rpc, value)), plain(await b.api.createClient(rpc, value)));
    assert.equal(b.trace.constructors.length, 0);
  }
});
await check('required DA rejects ed25519 without invoking encoding or decoding', async () => {
  const r = recording(sources[1]); await assert.rejects(r.api.sr25519KeyHex('ed25519:PUBLIC_MARKER'), /signed with sr25519/);
  assert.equal(r.trace.encodes, 0); assert.equal(r.trace.pairDecodes, 0);
});
await check('optional DA omits ed25519 without invoking encoding or decoding', async () => {
  const r = recording(sources[1]); assert.equal(await r.api.sr25519KeyHex('ed25519:PUBLIC_MARKER', false), undefined);
  assert.equal(r.trace.encodes, 0); assert.equal(r.trace.pairDecodes, 0);
});
await check('explicit and legacy sr25519 DA use the same recording boundary', async () => {
  const a = recording(sources[0]), b = recording(sources[1]);
  assert.equal(await a.api.sr25519KeyHex('PUBLIC_MARKER'), await b.api.sr25519KeyHex('sr25519:PUBLIC_MARKER'));
  assert.deepEqual(a.trace.uris, b.trace.uris); assert.equal(b.trace.encodes, 1); assert.equal(b.trace.pairDecodes, 1);
});
for (const type of ['ed25519', 'sr25519']) {
  await check(`keystore metadata preserves ${type} and encoded delimiters`, async () => {
    for (const source of sources) {
      const r = recording(source, { keystoreType: type }); const file = '/recording/public file:π.json';
      const input = 'keystore:' + encodeURIComponent(file) + ':' + encodeURIComponent(r.envName);
      const got = await r.api.createClient(rpc, input);
      assert.equal(got.route, 'pair'); assert.equal(got.keypair.type, type);
      assert.deepEqual(r.trace.reads, [{ file, encoding: 'utf8' }]);
      assert.deepEqual(r.trace.decodes, ['public-recording-marker']); assert.equal(r.trace.encodes, 0);
    }
  });
}
await check('missing keystore password refuses before the filesystem boundary', async () => {
  for (const source of sources) {
    const r = recording(source, { passwordPresent: false });
    await assert.rejects(r.api.agentSignerConfig('keystore:public.json:' + encodeURIComponent(r.envName)), /environment variable is unset/);
    assert.equal(r.trace.reads.length, 0); assert.equal(r.trace.constructors.length, 0);
  }
});
await check('unknown prefix stays legacy data rather than gaining a new type', async () => {
  const r = recording(sources[1]); const input = 'ecdsa:PUBLIC_MARKER';
  const got = await r.api.createClient(rpc, input); assert.equal(got.route, 'uri');
  assert.equal(got.opts.signer, input); assert.equal(r.trace.constructors.length, 0);
});
await check('only the explicit prefix is removed; remaining delimiters survive', async () => {
  const r = recording(sources[1]); const uri = '//PUBLIC_MARKER///public:π/password';
  await r.api.agentSignerConfig('ed25519:' + uri); assert.deepEqual(r.trace.uris, [uri]);
});
assert.equal(checks.length, 14);
console.log(JSON.stringify({ schema: 'flop-typed-signer-recording-review-v1', helperSha256: hashes,
  passed: checks.length, checks, scope: 'Pinned common-helper routing with recording key/fs/crypto/SDK boundaries only',
  peerNineRealCryptoGroupsExecuted: false, realKeysOrKeystoreIO: false,
  signingOrRPCOrFunding: false, fullCLIOrReleaseQualification: false }, null, 2));
