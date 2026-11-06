// Offline regression for network issue 42; no requests or credential access.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { open } from 'node:fs/promises';
import test from 'node:test';

const file = process.env.GATEWAY_CONTRACT_FILE;
assert.ok(file, 'Set GATEWAY_CONTRACT_FILE to the saved public OpenAPI JSON.');
const handle = await open(file, 'r');
let bytes;
try {
  assert.ok((await handle.stat()).isFile(), 'Expected a regular file.');
  const buffer = Buffer.alloc(2 * 1024 * 1024 + 1);
  let size = 0;
  while (size < buffer.length) {
    const read = await handle.read(buffer, size, buffer.length - size, null);
    if (!read.bytesRead) break;
    size += read.bytesRead;
  }
  assert.ok(size < buffer.length, 'Public contract exceeds the 2 MiB bound.');
  bytes = buffer.subarray(0, size);
} finally {
  await handle.close();
}
const sha256 = createHash('sha256').update(bytes).digest('hex');
assert.equal(sha256, '36650bd958115339018c0c2045b42d59d610def14f4b54e4718e91a2bf24d92a',
  'This reproduction is pinned to the November 6 served schema; review changed bytes separately.');
const original = JSON.parse(bytes.toString('utf8'));
assert.equal(original.openapi, '3.1.0');
console.log(JSON.stringify({ source_sha256: sha256, node: process.version,
  platform: process.platform, network_requests: 0, scope: 'saved OpenAPI only' }));

const receiptPath = '/keys/me/receipts/{request_id}';
function boundary(document) {
  const models = document.paths?.['/models']?.get;
  const receipt = document.paths?.[receiptPath]?.get;
  const bearer = document.components?.securitySchemes?.BearerAuth;
  return {
    modelsExplicitlyPublic: Object.hasOwn(models ?? {}, 'security') &&
      Array.isArray(models.security) && models.security.length === 0,
    receiptExplicitlyBearer: JSON.stringify(receipt?.security) ===
      JSON.stringify([{ BearerAuth: [] }]) && bearer?.type === 'http' &&
      bearer?.scheme === 'bearer',
  };
}
function candidate() {
  const document = structuredClone(original);
  document.paths['/models'].get.security = [];
  return document;
}
const accepted = { modelsExplicitlyPublic: true, receiptExplicitlyBearer: true };

test('served schema reproduces the model omission while receipt auth stays explicit', () => {
  assert.deepEqual(boundary(original), {
    modelsExplicitlyPublic: false, receiptExplicitlyBearer: true,
  });
});
test('one-operation anonymous override fixes discovery and preserves protected lookup', () => {
  const document = candidate();
  assert.deepEqual(boundary(document), accepted);
  assert.deepEqual(document.security, original.security);
  assert.deepEqual(document.paths[receiptPath], original.paths[receiptPath]);
});
test('credential requirement on model discovery is rejected', () => {
  const document = candidate();
  document.paths['/models'].get.security = [{ BearerAuth: [] }];
  assert.equal(boundary(document).modelsExplicitlyPublic, false);
});
test('path-level security is not an operation-level anonymous override', () => {
  const document = structuredClone(original);
  document.paths['/models'].security = [];
  assert.equal(boundary(document).modelsExplicitlyPublic, false);
});
test('changing global security alone leaves the explicit operation contract missing', () => {
  const document = structuredClone(original);
  document.security = [];
  assert.equal(boundary(document).modelsExplicitlyPublic, false);
});
test('anonymous receipt lookup is rejected', () => {
  const document = candidate();
  document.paths[receiptPath].get.security = [];
  assert.equal(boundary(document).receiptExplicitlyBearer, false);
});
test('receipt inheritance is rejected instead of admitting the global payment alternative', () => {
  const document = candidate();
  delete document.paths[receiptPath].get.security;
  assert.equal(boundary(document).receiptExplicitlyBearer, false);
});
test('a payment alternative must not replace scoped bearer receipt authority', () => {
  const document = candidate();
  document.paths[receiptPath].get.security.push({ X402Payment: [] });
  assert.equal(boundary(document).receiptExplicitlyBearer, false);
});
test('an optional anonymous alternative on receipt lookup is rejected', () => {
  const document = candidate();
  document.paths[receiptPath].get.security.push({});
  assert.equal(boundary(document).receiptExplicitlyBearer, false);
});
test('a missing bearer definition is not a validated protected operation', () => {
  const document = candidate();
  delete document.components.securitySchemes.BearerAuth;
  assert.equal(boundary(document).receiptExplicitlyBearer, false);
});
