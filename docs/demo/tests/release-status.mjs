// Static contract to prevent a stale demo UI from misdescribing release/source status.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const read = (p) => fs.readFileSync(path.join(root, p), 'utf8');
const releaseCommit = '3f622a2cfd5cf1826d22d9266b542710d8b0faf1';
const pkg = read('pyproject.toml');
const readme = read('README.md');
const page = read('docs/demo/index.html');
const demo = read('docs/demo/demo.js');
const input = read('docs/demo/input.js');
const conformance = read('docs/demo/tests/conformance.mjs');
const workflow = read('.github/workflows/pages.yml');

assert.match(pkg, /^version\s*=\s*"0\.1\.3"$/m, 'project version must match the pinned release source');
assert.ok(readme.includes(releaseCommit), 'README release source must point at the pinned commit');
assert.ok(workflow.includes('CLI_REF: ' + releaseCommit), 'Pages workflow must use the same immutable CLI source');
assert.ok(page.includes(releaseCommit), 'demo page must expose the exact source commit');
assert.ok(page.includes('La release <code>v0.1.3</code> existe como alpha de GitHub'), 'demo page must distinguish a published GitHub alpha');
assert.ok(page.includes('la distribución PyPI'), 'PyPI must remain a separate distribution gate');
assert.ok(page.includes('Resultado de CI'), 'CI state must be tied to a specific workflow rather than a stale previous run');
assert.ok(conformance.includes('v0.1.3 alpha CLI source'), 'conformance instructions must state the current CLI release');
assert.ok(workflow.includes('node docs/demo/tests/release-status.mjs'), 'Pages workflow must execute this contract');
for (const stale of [
  'CANDIDATO v0.1.3 · BORRADOR NO PUBLICADO',
  'No se afirma que la release v0.1.3, el paquete PyPI ni la imagen GHCR estén publicados.',
  'candidato v0.1.3 · no publicado',
  '55cba4500daf7b5cc803c63ccaff01985e4d965f',
  'v0.1.1',
]) {
  assert.ok(!page.includes(stale), 'stale page text remains: ' + stale);
}
assert.ok(!demo.includes('v0.1.1'), 'browser UI must not instruct users to compare against the old CLI');
assert.ok(!input.includes('v0.1.1'), 'input layer must document the pinned release input contract');
console.log('Demo/release source contract OK: v0.1.3 alpha source ' + releaseCommit);
