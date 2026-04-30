const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const app = read('ui/src/App.jsx');
const styles = read('ui/src/styles.css');

// Search state
assert.ok(/searchQuery|search.*State/i.test(app), 'App should have search state');

// Search input
assert.ok(/SearchBar|search.*input|placeholder.*搜索/i.test(app), 'App should have search input');

// Sort state or click handlers
assert.ok(/sortConfig|sortKey|onClick.*sort|handleSort/i.test(app), 'App should have sort functionality');

// Search bar styles
assert.ok(styles.includes('search-bar') || styles.includes('search-input'), 'Styles should include search bar styles');

console.log('ui search filter ok');
