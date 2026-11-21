import {spawnSync} from 'node:child_process';
import {existsSync, readdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const python = process.env.PYTHON || (existsSync(path.join(root, '.venv-catalog/bin/python'))
  ? path.join(root, '.venv-catalog/bin/python') : 'python3');
const suites = [
  ['JavaScript', process.execPath, ['--test', ...readdirSync(path.join(root, 'tests'))
    .filter(name => name.endsWith('.test.mjs')).sort().map(name => `tests/${name}`)]],
  ['Python (OCR, verification and review server)', python,
    ['-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py', '-v']],
];
let failed = false;
for (const [label, command, args] of suites) {
  console.log(`\n${label}\n`);
  const result = spawnSync(command, args, {cwd: root, stdio: 'inherit'});
  if (result.error) console.error(result.error.message);
  if (result.status !== 0) failed = true;
}
process.exitCode = failed ? 1 : 0;
