const fs = require('fs');
const path = 'C:/Users/93724/Desktop/Alpha monitor/AGENTS.md';
let content = fs.readFileSync(path, 'utf8');
const old = "4. `specs/spec.md`\n5. relevant `specs/*.md`";
const rep = "4. `specs/spec.md`\n5. `specs/api-reference.md`\n6. relevant `specs/*.md`";
content = content.replace(old, rep);
fs.writeFileSync(path, content, 'utf8');
console.log('Done');
