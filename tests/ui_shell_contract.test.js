const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function exists(relativePath) {
  return fs.existsSync(path.join(root, relativePath));
}

assert.ok(exists('ui/package.json'), 'ui/package.json should define the React app package');
assert.ok(exists('ui/src/App.jsx'), 'ui/src/App.jsx should define the terminal dashboard shell');
assert.ok(exists('ui/src/styles.css'), 'ui/src/styles.css should hold the terminal design system styles');

const packageJson = JSON.parse(read('package.json'));
assert.ok(packageJson.scripts['ui:build'], 'root package should expose ui:build');
assert.ok(packageJson.scripts['ui:check'], 'root package should expose ui:check');

const server = read('start_server.js');
assert.ok(server.includes("'/legacy'"), 'server should expose /legacy for the old dashboard');
assert.ok(server.includes('ui/dist'), 'server should serve the new React build from ui/dist');

const app = read('ui/src/App.jsx');
assert.ok(app.includes('Opportunity Command Center'), 'new UI should include the opportunity command center');
assert.ok(app.includes('/api/market/convertible-bond-arbitrage'), 'new UI should consume the real cbArb API');

const styles = read('ui/src/styles.css');
assert.ok(styles.includes('font-variant-numeric: tabular-nums'), 'styles should enforce tabular numeric rendering');
assert.ok(styles.includes('--terminal-bg'), 'styles should define terminal color tokens');

console.log('ui shell contract ok');
