#!/usr/bin/env node
'use strict';

/**
 * CLI tool — generates a plain-text security report from an IntelX JSON file.
 * Usage: node cli/report.js <input.json> [output.txt]
 */

const fs   = require('fs');
const path = require('path');
const { analyse } = require('../src/lib/parser');

function pad(n, w = 2) { return String(n).padStart(w, '0'); }

function bar(count, total, width = 30) {
  const filled = total === 0 ? 0 : Math.round((count / total) * width);
  return '[' + '█'.repeat(filled) + '░'.repeat(width - filled) + ']';
}

function section(title) {
  const line = '═'.repeat(68);
  return `\n${line}\n  ${title}\n${line}`;
}

function buildTextReport(summary) {
  const lines = [];
  const now   = new Date().toISOString().slice(0, 10);

  lines.push('');
  lines.push('╔══════════════════════════════════════════════════════════════════════╗');
  lines.push('║          EMAIL SECURITY EXPOSURE REPORT                             ║');
  lines.push('╚══════════════════════════════════════════════════════════════════════╝');
  lines.push('');
  lines.push(`  Report generated : ${now}`);
  lines.push(`  Total records    : ${summary.total.toLocaleString()}`);
  lines.push('');

  // Executive summary
  lines.push(section('1. EXECUTIVE SUMMARY'));
  lines.push('');
  lines.push(`  Overall Risk Level   : ${summary.overallLabel} (score ${summary.overallScore}/100)`);
  lines.push(`  Total Exposures      : ${summary.total.toLocaleString()} records across ${summary.uniqueGroups} unique datasets`);
  lines.push(`  Earliest Exposure    : ${summary.earliestDate}`);
  lines.push(`  Most Recent Exposure : ${summary.latestDate}`);
  lines.push(`  Dark Web Appearances : ${summary.darknetCount} (${summary.percent(summary.darknetCount)}%)`);
  lines.push(`  Credential Logs      : ${summary.credLogsCount} (${summary.percent(summary.credLogsCount)}%)`);
  lines.push(`  Restricted Leaks     : ${summary.restrictedCount} (${summary.percent(summary.restrictedCount)}%)`);
  lines.push(`  Retrievable Records  : ${summary.inStoreCount.toLocaleString()} of ${summary.total}`);
  lines.push('');

  const crit = summary.riskBreakdown.CRITICAL || 0;
  const high = summary.riskBreakdown.HIGH     || 0;
  const parts = [];
  if (crit > 0) parts.push(`${crit} records on dark web platforms`);
  if (high > 0) parts.push(`${high} records in restricted/credential-log databases`);
  if (parts.length) {
    lines.push(`  ! Significant threat profile: ${parts.join(', ')}.`);
    lines.push('    Immediate password changes and account audits are strongly advised.');
  } else {
    lines.push('  Exposure is primarily on public or informational sources.');
    lines.push('  Standard security hygiene is recommended.');
  }
  lines.push('');

  // Risk breakdown
  lines.push(section('2. RISK LEVEL BREAKDOWN'));
  lines.push('');
  for (const level of ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO', 'UNKNOWN']) {
    const count = summary.riskBreakdown[level] || 0;
    if (count === 0) continue;
    lines.push(`  ${level.padEnd(9)} ${String(count).padStart(5)}  ${bar(count, summary.total)}  ${summary.percent(count).padStart(5)}%`);
  }
  lines.push('');

  // Source categories
  lines.push(section('3. SOURCE CATEGORY BREAKDOWN'));
  lines.push('');
  lines.push('  Category                                      Count     %     Risk');
  lines.push('  ' + '─'.repeat(66));
  const { bucketMeta } = require('../src/lib/parser');
  Object.entries(summary.byBucket)
    .sort((a, b) => b[1] - a[1])
    .forEach(([bucket, count]) => {
      const meta  = bucketMeta(bucket);
      const label = meta.label.length > 44 ? meta.label.slice(0, 41) + '...' : meta.label;
      lines.push(`  ${label.padEnd(46)} ${String(count).padStart(4)}  ${summary.percent(count).padStart(5)}%  ${meta.risk}`);
    });
  lines.push('');

  // Media types
  lines.push(section('4. MEDIA TYPE BREAKDOWN'));
  lines.push('');
  lines.push('  Type                           Count     %');
  lines.push('  ' + '─'.repeat(44));
  Object.entries(summary.byMedia)
    .sort((a, b) => b[1] - a[1])
    .forEach(([type, count]) => {
      lines.push(`  ${type.padEnd(32)} ${String(count).padStart(4)}  ${summary.percent(count).padStart(5)}%`);
    });
  lines.push('');

  // Exposure timeline
  lines.push(section('5. EXPOSURE TIMELINE'));
  lines.push('');
  const years = Object.keys(summary.yearDist).map(Number).sort();
  if (years.length === 0) {
    lines.push('  No usable date data.');
  } else {
    const maxY = Math.max(...Object.values(summary.yearDist));
    lines.push('  Year   Count  Distribution');
    lines.push('  ' + '─'.repeat(50));
    years.forEach(y => {
      const c = summary.yearDist[y];
      lines.push(`  ${y}  ${String(c).padStart(5)}  ${bar(c, maxY, 25)}`);
    });
  }
  lines.push('');
  lines.push(`  Earliest record : ${summary.earliestDate}`);
  lines.push(`  Latest record   : ${summary.latestDate}`);
  lines.push('');

  // Threat indicators
  lines.push(section('6. THREAT INDICATORS'));
  lines.push('');
  if (summary.threats.length === 0) {
    lines.push('  No critical threat indicators detected.');
  } else {
    summary.threats.forEach(t => {
      lines.push(`  [${t.severity}] ${t.message}`);
      lines.push(`          ${t.detail}`);
      lines.push('');
    });
  }

  // Recommendations
  lines.push(section('7. RECOMMENDATIONS'));
  lines.push('');
  summary.recs.forEach((r, i) => lines.push(`  ${i + 1}. ${r}`));
  lines.push('');

  lines.push('═'.repeat(70));
  lines.push('  END OF REPORT');
  lines.push('═'.repeat(70));
  lines.push('');

  return lines.join('\n');
}

// ── entry point ───────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: node cli/report.js <input.json> [output.txt]');
  process.exit(1);
}

const inputFile  = args[0];
const outputFile = args[1] || null;

if (!fs.existsSync(inputFile)) {
  console.error(`File not found: ${inputFile}`);
  process.exit(1);
}

const data    = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
const records = data.records || [];
if (records.length === 0) {
  console.error('No records found in input file.');
  process.exit(1);
}

const summary = analyse(records);
const report  = buildTextReport(summary);

if (outputFile) {
  fs.writeFileSync(outputFile, report, 'utf8');
  console.log(`Report written to: ${outputFile}`);
} else {
  process.stdout.write(report);
}
