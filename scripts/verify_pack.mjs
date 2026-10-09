import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';

const [address, creator, id, expectedState, expectedSelected = ''] = process.argv.slice(2);
const canonical = value => {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (value !== null && typeof value === 'object') return '{' + Object.keys(value).sort()
    .map(key => canonical(key) + ':' + canonical(value[key])).join(',') + '}';
  return JSON.stringify(value).replace(/[\u0080-\uffff]/g, char => '\\u' + char.charCodeAt(0).toString(16).padStart(4, '0'));
};
const digest = value => crypto.createHash('sha256').update(canonical(value)).digest('hex');
const checkRoot = value => {const {root, ...payload} = value; assert.equal(root, digest(payload));};
try {
  assert.match(address, /^0x[0-9a-fA-F]{40}$/);
  assert.match(creator, /^0x[0-9a-fA-F]{40}$/);
  const client = createClient({chain: studionet});
  const read = (functionName, args) => client.readContract({address, functionName, args});
  const key = await read('pack_key', [creator, id]);
  const pack = await read('get_pack', [key]);
  assert.equal(pack.definition_root, digest(pack.definition));
  assert.equal(pack.state, expectedState);
  if (expectedState === 'OPEN') {
    assert.deepEqual(pack.result, {});
    console.log(JSON.stringify({key, state: pack.state, definition_root_verified: true}));
  } else {
    const result = pack.result;
    checkRoot(result);
    assert.equal(result.pack, key);
    assert.equal(result.definition_root, pack.definition_root);
    assert.equal(result.state, pack.state);
    const matrix = [], rejected = [], roots = [];
    for (const rfc of pack.definition.rfcs) {
      if (result.rejected.some(row => row.rfc === rfc && row.reason === 'MISSING')) {
        assert(result.at >= pack.definition.deadline);
        rejected.push({rfc, reason: 'MISSING'});
        continue;
      }
      const row = await read('get_row', [key, rfc]);
      checkRoot(row);
      assert.equal(row.spec.pack, key);
      assert.equal(row.spec.definition_root, pack.definition_root);
      assert.equal(row.spec.rfc, rfc);
      assert.equal(row.spec.url, `https://www.rfc-editor.org/rfc/rfc${rfc}.txt`);
      roots.push({rfc, root: row.root});
      if (row.state !== 'OBSERVED') rejected.push({rfc, reason: row.state});
      else if (result.at - row.spec.observed_at < 0 || result.at - row.spec.observed_at > pack.definition.max_age)
        rejected.push({rfc, reason: 'STALE'});
      else {
        assert.equal(row.status, 200);
        assert(row.bytes > 0 && row.bytes <= 16384);
        assert.match(row.hash, /^[a-f0-9]{64}$/);
        assert.equal(row.coverage.length, pack.definition.requirements.length);
        assert(row.coverage.every(item => item === 'YES' || item === 'NO'));
        matrix.push({rfc, bytes: row.bytes, hash: row.hash, coverage: row.coverage});
      }
    }
    assert.deepEqual(result.matrix, matrix);
    assert.deepEqual(result.row_roots, roots);
    assert.deepEqual(result.rejected, rejected);
    // Independent recursive enumeration, not the contract's bitmask loop.
    let best;
    const subsets = (index, chosen) => {
      if (index < matrix.length) {
        subsets(index + 1, chosen);
        subsets(index + 1, [...chosen, matrix[index]]);
        return;
      }
      if (!chosen.length || !pack.definition.requirements.every((_, j) => chosen.some(row => row.coverage[j] === 'YES'))) return;
      const cost = chosen.reduce((sum, row) => sum + row.bytes, 0);
      const ids = chosen.map(row => row.rfc);
      const smaller = best && ids.some((id, i) => ids.slice(0, i).every((v, j) => v === best.ids[j]) && id < best.ids[i]);
      if (!best || cost < best.cost || (cost === best.cost && (smaller ||
          (ids.length < best.ids.length && ids.every((id, i) => id === best.ids[i]))))) best = {ids, cost};
    };
    if (!rejected.length) subsets(0, []);
    const selected = best?.ids ?? [], cost = best?.cost ?? 0;
    assert.deepEqual(result.selected, selected);
    assert.equal(result.total_bytes, cost);
    assert.equal(result.state, rejected.length ? 'INCOMPLETE' : selected.length ? 'COVERED' : 'UNCOVERED');
    assert.deepEqual(selected, expectedSelected ? expectedSelected.split(',').map(Number) : []);
    console.log(JSON.stringify({key, state: result.state, selected, total_bytes: cost, matrix,
      roots_verified: true, bindings_verified: true, global_minimum_reconstructed: !rejected.length}));
  }
} catch (error) {
  console.error(error.code === 'ERR_ASSERTION' ? error.message : error.shortMessage ?? 'Pack verification failed');
  process.exitCode = 1;
}
