#!/usr/bin/env node
import fs from 'fs';
import path from 'path';

const VAULT_PATH = process.env.STZ_VAULT_PATH || 'C:\\OPENCLAW\\obsidian-vault';

function showUsage() {
  console.log(`Usage: node vault-cli.mjs <command> [args]
Commands:
  search <query>           Search notes by keyword in title or content
  read <relativePath>      Read note content and frontmatter
  list [subDir]            List notes in a directory
  write <relPath> <title> <owner> <content>  Write note with frontmatter
`);
}

const [,, cmd, ...args] = process.argv;

if (!cmd) {
  showUsage();
  process.exit(1);
}

if (!fs.existsSync(VAULT_PATH)) {
  console.error(`Error: Vault not found at ${VAULT_PATH}`);
  process.exit(1);
}

switch (cmd) {
  case 'search': {
    const q = (args[0] || '').toLowerCase();
    const hits = [];
    function scan(dir) {
      const items = fs.readdirSync(dir, { withFileTypes: true });
      for (const item of items) {
        const full = path.join(dir, item.name);
        if (item.isDirectory() && !item.name.startsWith('.')) {
          scan(full);
        } else if (item.isFile() && item.name.endsWith('.md')) {
          const content = fs.readFileSync(full, 'utf-8');
          if (item.name.toLowerCase().includes(q) || content.toLowerCase().includes(q)) {
            hits.push({
              file: path.relative(VAULT_PATH, full).replace(/\\/g, '/'),
              title: item.name.replace(/\.md$/, '')
            });
          }
        }
      }
    }
    scan(VAULT_PATH);
    console.log(JSON.stringify({ success: true, count: hits.length, results: hits }, null, 2));
    break;
  }

  case 'read': {
    const rel = args[0];
    if (!rel) {
      console.error('Specify relative path');
      process.exit(1);
    }
    const full = path.resolve(VAULT_PATH, rel);
    if (!full.startsWith(path.resolve(VAULT_PATH)) || !fs.existsSync(full)) {
      console.error('File not found or path traversal blocked');
      process.exit(1);
    }
    const content = fs.readFileSync(full, 'utf-8');
    console.log(content);
    break;
  }

  case 'list': {
    const sub = args[0] || '';
    const target = path.resolve(VAULT_PATH, sub);
    if (!target.startsWith(path.resolve(VAULT_PATH)) || !fs.existsSync(target)) {
      console.error('Invalid directory');
      process.exit(1);
    }
    const files = fs.readdirSync(target, { withFileTypes: true })
      .filter(f => f.isFile() && f.name.endsWith('.md'))
      .map(f => f.name);
    console.log(JSON.stringify({ directory: sub, files }, null, 2));
    break;
  }

  default:
    showUsage();
    process.exit(1);
}
