/**
 * Views Badge - GitHub Action Entry Point
 * Reads .viewsbadge from user's own repo
 * Writes badge JSON that shields.io can read
 * @author OmniNodeCo
 */

const fs   = require('fs');
const path = require('path');
const { isExcluded } = require('./user-filter');

// ─── GitHub Actions helpers ────────────────────────────────────────────────

function getInput(name) {
  return process.env[`INPUT_${name.toUpperCase().replace(/-/g, '_')}`] || '';
}

function setOutput(name, value) {
  const outputFile = process.env.GITHUB_OUTPUT;
  if (outputFile) {
    fs.appendFileSync(outputFile, `${name}=${value}\n`);
  }
}

function log(msg) {
  console.log(`[views-badge] ${msg}`);
}

// ─── Load config from user's repo ─────────────────────────────────────────

function loadConfig(configFile) {
  const filePath = path.join(process.env.GITHUB_WORKSPACE || '.', configFile);

  if (!fs.existsSync(filePath)) {
    log(`No config found at ${filePath} — counting all visitors`);
    return null;
  }

  try {
    const raw = fs.readFileSync(filePath, 'utf8');
    const config = JSON.parse(raw);
    log(`Config loaded from ${filePath}`);
    return config;
  } catch (err) {
    log(`Config file invalid JSON: ${err.message}`);
    return null;
  }
}

// ─── Load / save count JSON ────────────────────────────────────────────────

function loadCount(outputFile) {
  const fullPath = path.join(process.env.GITHUB_WORKSPACE || '.', outputFile);

  if (!fs.existsSync(fullPath)) {
    return { count: 0, visitors: {} };
  }

  try {
    return JSON.parse(fs.readFileSync(fullPath, 'utf8'));
  } catch {
    return { count: 0, visitors: {} };
  }
}

function saveCount(outputFile, data) {
  const fullPath = path.join(process.env.GITHUB_WORKSPACE || '.', outputFile);
  fs.mkdirSync(path.dirname(fullPath), { recursive: true });
  fs.writeFileSync(fullPath, JSON.stringify(data, null, 2));
  log(`Count saved to ${outputFile}`);
}

// ─── Format number ─────────────────────────────────────────────────────────

function formatNum(n) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (n >= 1_000)     return (n / 1_000).toFixed(1) + 'K';
  return String(n);
}

// ─── Main ──────────────────────────────────────────────────────────────────

async function main() {
  const visitor    = getInput('visitor')     || process.env.GITHUB_ACTOR || '';
  const outputFile = getInput('output_file') || '.views/badge.json';
  const configFile = getInput('config_file') || '.viewsbadge';

  log(`Visitor: ${visitor || '(none)'}`);
  log(`Output:  ${outputFile}`);
  log(`Config:  ${configFile}`);

  // Load config from user's own repo
  const config = loadConfig(configFile);

  // Load existing count
  const data = loadCount(outputFile);

  // Check exclusion
  const excluded = isExcluded(config, visitor);

  if (excluded) {
    log(`"${visitor}" is in exclude list — not counting`);
  } else {
    data.count++;

    // Track per-visitor counts (no IPs, usernames only)
    if (visitor) {
      data.visitors[visitor] = (data.visitors[visitor] || 0) + 1;
    }

    log(`View counted. Total: ${data.count}`);
  }

  // Always write updated file so shields.io always has something to read
  saveCount(outputFile, data);

  // Set action output
  setOutput('count', data.count);

  // Write shields.io compatible JSON
  // shields.io endpoint badge needs: { schemaVersion, label, message, color }
  const label   = config?.label   || 'views';
  const color   = config?.color   || 'blue';
  const message = formatNum(data.count);

  const shieldsJson = {
    schemaVersion: 1,
    label,
    message,
    color,
    style:         config?.style || 'flat',
    cacheSeconds:  300,
  };

  const shieldsFile = path.join(
    process.env.GITHUB_WORKSPACE || '.',
    path.dirname(outputFile),
    'shields.json'
  );

  fs.writeFileSync(shieldsFile, JSON.stringify(shieldsJson, null, 2));
  log(`Shields JSON written to ${shieldsFile}`);
  log(`Badge message: ${message}`);
}

main().catch(err => {
  console.error('[views-badge] Fatal error:', err);
  process.exit(1);
});