'use strict';

const PDFDocument = require('pdfkit');
const { bucketMeta } = require('./parser');
const { buildProfile } = require('./profile');

const C = {
  ink:    '#111827',
  body:   '#374151',
  muted:  '#6b7280',
  dim:    '#9ca3af',
  rule:   '#e5e7eb',
  stripe: '#e8ecf0',
  accent: '#4f46e5',
  white:  '#ffffff',
};

const RISK = {
  CRITICAL: '#ef4444',
  HIGH:     '#f97316',
  MEDIUM:   '#eab308',
  LOW:      '#22c55e',
  INFO:     '#3b82f6',
  UNKNOWN:  '#9ca3af',
  MINIMAL:  '#6b7280',
};

function riskColor(label) { return RISK[label] || RISK.UNKNOWN; }

function fillRect(doc, x, y, w, h, color) {
  doc.save().rect(x, y, w, h).fill(color).restore();
}

function hRule(doc, x, y, w, color = C.rule, lw = 0.5) {
  doc.save().moveTo(x, y).lineTo(x + w, y).lineWidth(lw).stroke(color).restore();
}

function bar(doc, x, y, count, total, color, maxW = 180) {
  const filled = total === 0 ? 0 : Math.round((count / total) * maxW);
  fillRect(doc, x, y + 5, maxW, 4, C.rule);
  if (filled > 0) fillRect(doc, x, y + 5, filled, 4, color);
}

function normalizePlatforms(platforms) {
  if (!platforms || typeof platforms !== 'object') return [];
  const rows = Object.entries(platforms).map(([name, data]) => {
    if (!data || typeof data !== 'object') return { name, exists: null, details: [] };
    let exists = null;
    if (typeof data.accountExists === 'boolean') exists = data.accountExists;
    else if (typeof data.exists   === 'boolean') exists = data.exists;
    const details = [];
    if (data.backupEmail)      details.push(`Backup: ${data.backupEmail}`);
    if (data.emailRecovery)    details.push(`Recovery: ${data.emailRecovery}`);
    if (data.phoneNumber)      details.push(`Phone: ${data.phoneNumber}`);
    if (data.securityQuestion) details.push('Security Q set');
    if (data.twoFA === true)   details.push('2FA on');
    if (Array.isArray(data.phones) && data.phones.length) details.push(`Phone: ${data.phones[0]}`);
    const fullName = [data.firstName, data.lastName].filter(Boolean).join(' ');
    if (fullName)           details.push(`Name: ${fullName}`);
    if (data.lastLogin)     details.push(`Login: ${data.lastLogin.slice(0, 10)}`);
    if (data.lastActive)    details.push(`Active: ${data.lastActive.slice(0, 10)}`);
    if (data.method)        details.push(`Login: ${data.method}`);
    return { name, exists, details };
  });
  const rank = v => (v === true ? 0 : v === false ? 1 : 2);
  return rows.sort((a, b) => rank(a.exists) - rank(b.exists));
}

function buildPdf(summary, meta = {}) {
  return new Promise((resolve, reject) => {
    const PAGE_W   = 595;
    const PAGE_H   = 842;
    const GM       = 48;
    const CW       = PAGE_W - GM * 2;
    const FOOTER_H = 36;
    const BOTTOM   = PAGE_H - FOOTER_H;

    const rLabel = summary.overallLabel;
    const rColor = riskColor(rLabel);

    const doc = new PDFDocument({
      size: 'A4', margin: 0, autoFirstPage: false,
      info: { Title: 'Intelligence Report' },
    });
    const chunks = [];
    doc.on('data',  c  => chunks.push(c));
    doc.on('end',   () => resolve(Buffer.concat(chunks)));
    doc.on('error', reject);

    let pageNum = 0;

    doc.on('pageAdded', () => {
      pageNum++;
      let contentStart;

      if (pageNum === 1) {
        fillRect(doc, 0, 0, PAGE_W, 64, C.ink);

        doc.fontSize(13).font('Helvetica-Bold').fillColor(C.white)
           .text('INTELLIGENCE REPORT', GM, 16, { lineBreak: false });

        const tgt = meta.targets || {};
        const sub = [tgt.email || meta.email, tgt.name, tgt.phone, tgt.username, new Date().toISOString().slice(0, 10)]
          .filter(Boolean).join('  ·  ');
        doc.fontSize(8).font('Helvetica').fillColor(C.dim)
           .text(sub, GM, 35, { lineBreak: false });

        doc.fontSize(8).font('Helvetica').fillColor(C.dim)
           .text(`${summary.overallScore}/100`, PAGE_W - GM - 60, 22, { width: 60, align: 'right', lineBreak: false });
        doc.fontSize(11).font('Helvetica-Bold').fillColor(rColor)
           .text(rLabel, PAGE_W - GM - 60, 35, { width: 60, align: 'right', lineBreak: false });

        fillRect(doc, 0, 64, PAGE_W, 2, rColor);
        contentStart = 82;
      } else {
        fillRect(doc, 0, 0, PAGE_W, 18, C.ink);
        fillRect(doc, 0, 18, PAGE_W, 1, rColor);
        doc.fontSize(7).font('Helvetica').fillColor(C.dim)
           .text('INTELLIGENCE REPORT  ·  CONTINUED', GM, 6, { lineBreak: false });
        contentStart = 30;
      }

      hRule(doc, GM, PAGE_H - FOOTER_H, CW);
      doc.fontSize(7).font('Helvetica').fillColor(C.dim)
         .text('Confidential — for authorized security assessment use only.',
               GM, PAGE_H - FOOTER_H + 10, { width: CW, align: 'center', lineBreak: false });

      doc.y = contentStart;
    });

    function ensureSpace(needed) {
      if (doc.y + needed > BOTTOM) doc.addPage();
    }

    function sectionHeader(title) {
      ensureSpace(56);
      const y = doc.y + 14;
      fillRect(doc, GM, y, 3, 16, C.accent);
      doc.fontSize(8).font('Helvetica-Bold').fillColor(C.ink)
         .text(title, GM + 10, y + 4, { lineBreak: false });
      hRule(doc, GM + 10, y + 18, CW - 10);
      doc.y = y + 26;
    }

    function colHead(doc, x, y, text, width) {
      doc.fontSize(7).font('Helvetica-Bold').fillColor(C.body)
         .text(text, x, y, { lineBreak: false, width });
    }

    doc.addPage();

    sectionHeader('1  ·  EXECUTIVE SUMMARY');

    const ROW = 16;
    const metrics = [
      ['Total Records',        summary.total.toLocaleString()],
      ['Unique Datasets',      summary.uniqueGroups.toLocaleString()],
      ['Dark Web Appearances', `${summary.darknetCount} (${summary.percent(summary.darknetCount)}%)`],
      ['Credential Logs',      `${summary.credLogsCount} (${summary.percent(summary.credLogsCount)}%)`],
      ['Restricted Leaks',     `${summary.restrictedCount} (${summary.percent(summary.restrictedCount)}%)`],
      ['Earliest Exposure',    summary.earliestDate],
      ['Most Recent Record',   summary.latestDate],
      ['Retrievable Records',  `${summary.inStoreCount.toLocaleString()} of ${summary.total.toLocaleString()}`],
    ];

    const sumY = doc.y;
    metrics.forEach(([label, value], i) => {
      const y = sumY + i * ROW;
      if (i % 2 === 0) fillRect(doc, GM, y, CW, ROW, C.stripe);
      doc.fontSize(8.5).font('Helvetica').fillColor(C.body)
         .text(label, GM + 8, y + 4, { lineBreak: false, width: 180 });
      doc.fontSize(8.5).font('Helvetica-Bold').fillColor(C.ink)
         .text(value, GM + 196, y + 4, { lineBreak: false });
    });
    hRule(doc, GM, sumY, CW);
    hRule(doc, GM, sumY + metrics.length * ROW, CW);
    doc.y = sumY + metrics.length * ROW + 10;

    const profile = buildProfile(meta.platforms, summary, meta.breaches);

    sectionHeader('2  ·  PROFILE ANALYSIS');

    const profileRows = [];

    if (profile.names.length > 0) {
      profileRows.push(['Name(s) Found', profile.names.join(', ')]);
    }

    const countryMap = { SE: 'Sweden', RU: 'Russia', UK: 'United Kingdom', US: 'United States', GLOBAL: 'Global' };
    if (profile.geography.length > 0) {
      const geo     = profile.geography.map(c => countryMap[c] || c);
      const primary = profile.swedishSignals >= 2 ? 'Sweden (strong signal)' : geo.join(', ');
      profileRows.push(['Geographic Signal', primary]);
    }

    if (profile.political.length > 0) {
      profileRows.push(['Political Parties', profile.political.map(p => p.tag).join(', ')]);
      if (profile.politicalLean) profileRows.push(['Political Lean', profile.politicalLean]);
    }

    if (profile.mediaOutlets.length > 0) {
      profileRows.push(['Media Consumption', profile.mediaOutlets.map(m => m.name).join(', ')]);
      if (profile.mediaBias) profileRows.push(['Media Bias Signal', profile.mediaBias]);
    }

    const skipCats   = new Set(['Political', 'Media', 'Adult']);
    const interests  = profile.interests.filter(c => !skipCats.has(c));
    if (interests.length > 0) {
      profileRows.push(['Platform Categories', interests.join(', ')]);
    }

    profileRows.push(['Digital Footprint', `${profile.totalFound} of ${profile.totalChecked} platforms checked`]);

    if (profileRows.length === 0) {
      doc.fontSize(8.5).font('Helvetica').fillColor(C.muted)
         .text('Insufficient data to build profile.', GM + 8, doc.y);
      doc.moveDown(1);
    } else {
      ensureSpace(ROW + profileRows.length * ROW + 10);
      const prY = doc.y;
      colHead(doc, GM + 8,   prY + 4, 'ATTRIBUTE', 160);
      colHead(doc, GM + 176, prY + 4, 'VALUE',     CW - 186);
      hRule(doc, GM, prY + ROW, CW);

      profileRows.forEach(([label, value], i) => {
        const y = prY + ROW + i * ROW;
        if (i % 2 === 0) fillRect(doc, GM, y, CW, ROW, C.stripe);
        doc.fontSize(8.5).font('Helvetica').fillColor(C.muted)
           .text(label, GM + 8, y + 4, { lineBreak: false, width: 160 });
        doc.fontSize(8.5).font('Helvetica-Bold').fillColor(C.body)
           .text(value, GM + 176, y + 4, { lineBreak: false, width: CW - 186 });
      });

      hRule(doc, GM, prY, CW);
      hRule(doc, GM, prY + ROW + profileRows.length * ROW, CW);
      doc.y = prY + ROW + profileRows.length * ROW + 10;
    }

    if (profile.riskSignals.length > 0) {
      ensureSpace(12 + profile.riskSignals.length * 14);
      doc.fontSize(7.5).font('Helvetica-Bold').fillColor(C.ink)
         .text('Risk Signals', GM + 8, doc.y);
      doc.moveDown(0.3);
      profile.riskSignals.forEach(sig => {
        ensureSpace(14);
        fillRect(doc, GM + 8, doc.y, 4, 4, RISK.HIGH);
        doc.fontSize(7.5).font('Helvetica').fillColor(C.body)
           .text(sig, GM + 18, doc.y - 1, { lineBreak: false, width: CW - 28 });
        doc.moveDown(0.85);
      });
      doc.moveDown(0.4);
    }

    sectionHeader('3  ·  RISK BREAKDOWN');

    const levels = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'];
    const rbY    = doc.y;
    let   rbOff  = 0;

    levels.forEach(level => {
      const count = summary.riskBreakdown[level] || 0;
      if (count === 0) return;
      const y   = rbY + rbOff;
      const col = riskColor(level);
      if ((rbOff / ROW) % 2 === 0) fillRect(doc, GM, y, CW, ROW, C.stripe);
      doc.fontSize(8).font('Helvetica-Bold').fillColor(col)
         .text(level, GM + 8, y + 4, { lineBreak: false, width: 72 });
      doc.fontSize(8).font('Helvetica').fillColor(C.body)
         .text(String(count), GM + 84, y + 4, { lineBreak: false, width: 36 });
      bar(doc, GM + 124, y + 4, count, summary.total, col, 220);
      doc.fontSize(8).font('Helvetica').fillColor(C.muted)
         .text(`${summary.percent(count)}%`, GM + 352, y + 4, { lineBreak: false });
      rbOff += ROW;
    });

    if (rbOff === 0) {
      doc.fontSize(8.5).font('Helvetica').fillColor(C.muted)
         .text('No data.', GM + 8, rbY + 4);
      rbOff = ROW;
    }
    hRule(doc, GM, rbY, CW);
    hRule(doc, GM, rbY + rbOff, CW);
    doc.y = rbY + rbOff + 10;

    sectionHeader('4  ·  SOURCE CATEGORIES');

    const RISK_ORDER = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3, INFO: 4, UNKNOWN: 5, MINIMAL: 6 };
    const sorted = Object.entries(summary.byBucket).sort((a, b) => {
      const ra = RISK_ORDER[bucketMeta(a[0]).risk] ?? 99;
      const rb = RISK_ORDER[bucketMeta(b[0]).risk] ?? 99;
      return ra !== rb ? ra - rb : b[1] - a[1];
    });

    if (sorted.length === 0) {
      doc.fontSize(8.5).font('Helvetica').fillColor(C.muted)
         .text('No data.', GM + 8, doc.y);
      doc.moveDown(1);
    } else {
      ensureSpace(ROW + sorted.length * ROW + 10);
      const scY = doc.y;
      colHead(doc, GM + 8,   scY + 4, 'SOURCE', 220);
      colHead(doc, GM + 236, scY + 4, 'COUNT', 40);
      colHead(doc, GM + 284, scY + 4, 'RISK', 70);
      colHead(doc, GM + 362, scY + 4, '%', 40);
      hRule(doc, GM, scY + ROW, CW);

      sorted.forEach(([bucket, count], i) => {
        const y     = scY + ROW + i * ROW;
        const bmeta = bucketMeta(bucket);
        const col   = riskColor(bmeta.risk);
        if (i % 2 === 0) fillRect(doc, GM, y, CW, ROW, C.stripe);
        doc.fontSize(8.5).font('Helvetica').fillColor(C.body)
           .text(bmeta.label, GM + 8, y + 4, { lineBreak: false, width: 220 });
        doc.fontSize(8.5).fillColor(C.body)
           .text(String(count), GM + 236, y + 4, { lineBreak: false, width: 40 });
        doc.fontSize(7.5).font('Helvetica-Bold').fillColor(col)
           .text(bmeta.risk, GM + 284, y + 4, { lineBreak: false, width: 70 });
        doc.fontSize(8.5).font('Helvetica').fillColor(C.muted)
           .text(`${summary.percent(count)}%`, GM + 362, y + 4, { lineBreak: false });
      });

      hRule(doc, GM, scY, CW);
      hRule(doc, GM, scY + ROW + sorted.length * ROW, CW);
      doc.y = scY + ROW + sorted.length * ROW + 10;
    }

    sectionHeader('5  ·  THREAT INDICATORS');

    if (summary.threats.length === 0) {
      doc.fontSize(8.5).font('Helvetica').fillColor(C.muted)
         .text('No significant threat indicators detected.', GM + 8, doc.y);
      doc.moveDown(1);
    } else {
      const notable = summary.threats.filter(t => t.severity === 'CRITICAL' || t.severity === 'HIGH');
      const rest    = summary.threats.filter(t => t.severity !== 'CRITICAL' && t.severity !== 'HIGH');

      for (const t of notable) {
        ensureSpace(38);
        const col = riskColor(t.severity);
        const y   = doc.y;
        fillRect(doc, GM, y, 3, 30, col);
        fillRect(doc, GM + 3, y, CW - 3, 30, C.stripe);
        doc.fontSize(8.5).font('Helvetica-Bold').fillColor(C.ink)
           .text(t.message, GM + 12, y + 5, { lineBreak: false, width: CW - 20 });
        doc.fontSize(7.5).font('Helvetica').fillColor(C.muted)
           .text(t.detail, GM + 12, y + 18, { lineBreak: false, width: CW - 20 });
        doc.y = y + 36;
      }

      if (rest.length > 0) {
        ensureSpace(16);
        doc.fontSize(8).font('Helvetica').fillColor(C.muted)
           .text(`+ ${rest.length} additional indicator${rest.length > 1 ? 's' : ''} (medium severity).`, GM + 8, doc.y);
        doc.moveDown(0.8);
      }
    }

    const platforms      = normalizePlatforms(meta.platforms);
    const foundPlatforms = platforms.filter(p => p.exists === true);
    if (platforms.length > 0) {
      sectionHeader('6  ·  PLATFORM PRESENCE');

      if (foundPlatforms.length === 0) {
        ensureSpace(ROW + 24);
        doc.fontSize(8.5).font('Helvetica').fillColor(C.muted)
           .text('No accounts found on any checked platform.', GM + 8, doc.y + 6);
        doc.y += ROW + 10;
      } else {
        ensureSpace(ROW + foundPlatforms.length * ROW + 10 + 56);
        const ppY = doc.y;
        colHead(doc, GM + 8,   ppY + 4, 'PLATFORM', 140);
        colHead(doc, GM + 224, ppY + 4, 'DETAILS', CW - 234);
        hRule(doc, GM, ppY + ROW, CW);

        foundPlatforms.forEach(({ name, details }, i) => {
          const y = ppY + ROW + i * ROW;
          if (i % 2 === 0) fillRect(doc, GM, y, CW, ROW, C.stripe);
          doc.fontSize(8.5).font('Helvetica-Bold').fillColor(RISK.HIGH)
             .text(name, GM + 8, y + 4, { lineBreak: false, width: 140 });
          if (details.length) {
            doc.fontSize(7.5).font('Helvetica').fillColor(C.muted)
               .text(details.join('  ·  '), GM + 224, y + 4, { lineBreak: false, width: CW - 234 });
          }
        });

        hRule(doc, GM, ppY, CW);
        hRule(doc, GM, ppY + ROW + foundPlatforms.length * ROW, CW);
        doc.y = ppY + ROW + foundPlatforms.length * ROW + 10;
      }
    }

    const breaches   = Array.isArray(meta.breaches) ? meta.breaches : [];
    let   sectionNum = platforms.length > 0 ? 7 : 6;

    if (breaches.length > 0) {
      const BV_ROW = 16;
      const visible = breaches.slice(0, 200);
      sectionHeader(`${sectionNum}  ·  BREACH.VIP`);
      sectionNum++;

      doc.fontSize(8).font('Helvetica').fillColor(C.muted)
         .text(`${breaches.length.toLocaleString()} record${breaches.length > 1 ? 's' : ''} matched.`,
               GM + 8, doc.y, { lineBreak: false });
      doc.y += 14;

      function bvHeader() {
        const base = doc.y;
        colHead(doc, GM + 8,   base + 4, 'BREACH SOURCE', 270);
        colHead(doc, GM + 286, base + 4, 'CATEGORIES', CW - 296);
        hRule(doc, GM, base + BV_ROW, CW);
        doc.y = base + BV_ROW;
        return base;
      }

      let tableStart = bvHeader();
      let rowsOnPage = 0;
      hRule(doc, GM, tableStart, CW);

      visible.forEach((result) => {
        if (doc.y + BV_ROW > BOTTOM) {
          hRule(doc, GM, doc.y, CW);
          doc.addPage();
          tableStart = bvHeader();
          hRule(doc, GM, tableStart, CW);
          rowsOnPage = 0;
        }

        const y    = doc.y;
        const cats = Array.isArray(result.categories) ? result.categories.join(', ') : (result.categories || '');
        if (rowsOnPage % 2 === 0) fillRect(doc, GM, y, CW, BV_ROW, C.stripe);
        doc.fontSize(8.5).font('Helvetica').fillColor(C.body)
           .text(result.source || '—', GM + 8, y + 4, { lineBreak: false, width: 270 });
        doc.fontSize(7.5).font('Helvetica').fillColor(C.muted)
           .text(cats, GM + 286, y + 4, { lineBreak: false, width: CW - 296 });
        doc.y += BV_ROW;
        rowsOnPage++;
      });

      hRule(doc, GM, doc.y, CW);
      doc.y += 10;

      if (breaches.length > 200) {
        ensureSpace(16);
        doc.fontSize(8).font('Helvetica').fillColor(C.muted)
           .text(`+ ${(breaches.length - 200).toLocaleString()} additional records not shown.`, GM + 8, doc.y);
        doc.moveDown(0.6);
      }
    }

    sectionHeader(`${sectionNum}  ·  RECOMMENDATIONS`);

    summary.recs.forEach((rec) => {
      ensureSpace(20);
      const y = doc.y;
      fillRect(doc, GM + 8, y + 6, 4, 4, C.accent);
      doc.fontSize(8.5).font('Helvetica').fillColor(C.body)
         .text(rec, GM + 20, y + 2, { width: CW - 24 });
      doc.y += 4;
    });

    doc.end();
  });
}

module.exports = { buildPdf };
