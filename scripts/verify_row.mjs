import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';

const [address, key, rfcText, expectedCoverage, expectedHash, expectedBytes] = process.argv.slice(2);
const canonical = value => {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (value !== null && typeof value === 'object') return '{' + Object.keys(value).sort()
    .map(key => canonical(key) + ':' + canonical(value[key])).join(',') + '}';
  return JSON.stringify(value).replace(/[\u0080-\uffff]/g, char => '\\u' + char.charCodeAt(0).toString(16).padStart(4, '0'));
};
try {
  const client = createClient({chain: studionet});
  const rfc = Number(rfcText);
  const pack = await client.readContract({address, functionName: 'get_pack', args: [key]});
  const row = await client.readContract({address, functionName: 'get_row', args: [key, rfc]});
  const {root, ...payload} = row;
  assert.equal(root, crypto.createHash('sha256').update(canonical(payload)).digest('hex'));
  assert.equal(row.spec.pack, key);
  assert.equal(row.spec.definition_root, pack.definition_root);
  assert.equal(row.spec.rfc, rfc);
  assert.equal(row.state, 'OBSERVED');
  assert.equal(row.status, 200);
  assert.deepEqual(row.coverage, expectedCoverage.split(','));
  assert.equal(row.hash, expectedHash);
  assert.equal(row.bytes, Number(expectedBytes));
  console.log(JSON.stringify({rfc, state: row.state, coverage: row.coverage, bytes: row.bytes,
    hash: row.hash, report_root_verified: true, binding_verified: true}));
} catch (error) {
  console.error(error.code === 'ERR_ASSERTION' ? error.message : error.shortMessage ?? 'Row verification failed');
  process.exitCode = 1;
}
