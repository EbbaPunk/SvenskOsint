"use strict";

const BUCKET_RISK = {
  "Darknet » Tor":                 { risk: "CRITICAL", label: "Dark Web (Tor)" },
  "Darknet » I2P":                 { risk: "CRITICAL", label: "Dark Web (I2P)" },
  "Leaks » Restricted » General": { risk: "HIGH",     label: "Restricted Leak Database" },
  "Leaks » Logs":                  { risk: "HIGH",     label: "Credential Logs / Stealers" },
  "Leaks » Public » General":      { risk: "MEDIUM",   label: "Public Leak Database" },
  "Pastes":                        { risk: "MEDIUM",   label: "Paste Sites" },
  "Dumpster":                      { risk: "MEDIUM",   label: "Dumpster" },
  "Usenet":                        { risk: "LOW",      label: "Usenet" },
  "Web » Public » Government":     { risk: "LOW",      label: "Public Web – Government" },
  "Web » Public » European Union": { risk: "LOW",      label: "Public Web – EU" },
  "Web » Public » Western Europe": { risk: "LOW",      label: "Public Web – Western Europe" },
  "Web » Public » China":          { risk: "LOW",      label: "Public Web – China" },
  "Web » Public » Africa":         { risk: "LOW",      label: "Public Web – Africa" },
  "Whois":                         { risk: "INFO",     label: "WHOIS Records" },
  "Documents » Public » Sci-Hub":  { risk: "INFO",     label: "Public Documents (Sci-Hub)" },
};

const RISK_WEIGHTS = { CRITICAL: 100, HIGH: 75, MEDIUM: 45, LOW: 15, INFO: 5, UNKNOWN: 0 };

const RISK_COLORS = {
  CRITICAL: "#dc2626",
  HIGH:     "#ea580c",
  MEDIUM:   "#ca8a04",
  LOW:      "#16a34a",
  INFO:     "#2563eb",
  UNKNOWN:  "#6b7280",
};

function bucketMeta(bucketh) {
  return BUCKET_RISK[bucketh] || { risk: "UNKNOWN", label: bucketh || "Unknown" };
}

function riskLabel(score) {
  if (score >= 80) return "CRITICAL";
  if (score >= 60) return "HIGH";
  if (score >= 40) return "MEDIUM";
  if (score >= 20) return "LOW";
  return "MINIMAL";
}

function fmtDate(iso) {
  if (!iso) return "Unknown";
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}-${String(d.getUTCDate()).padStart(2, "0")}`;
}

function percent(n, total) {
  return total === 0 ? "0.0" : ((n / total) * 100).toFixed(1);
}


function analyse(records) {
  const total = records.length;

  const byBucket      = {};
  const byMedia       = {};
  const byAccess      = {};
  const riskBreakdown = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0, INFO: 0, UNKNOWN: 0 };

  for (const r of records) {
    const bucket = r.bucketh      || "Unknown";
    const media  = r.mediah       || "Unknown";
    const access = r.accesslevelh || "Unknown";
    const meta   = bucketMeta(bucket);

    byBucket[bucket] = (byBucket[bucket] || 0) + 1;
    byMedia[media]   = (byMedia[media]   || 0) + 1;
    byAccess[access] = (byAccess[access] || 0) + 1;
    riskBreakdown[meta.risk] = (riskBreakdown[meta.risk] || 0) + 1;
  }


  const validDates = records
    .map(r => r.date)
    .filter(d => d && !isNaN(new Date(d)))
    .map(d => new Date(d))
    .sort((a, b) => a - b);

  const earliestDate = validDates.length ? fmtDate(validDates[0].toISOString()) : "N/A";
  const latestDate   = validDates.length ? fmtDate(validDates[validDates.length - 1].toISOString()) : "N/A";

  const yearDist = {};
  validDates
    .filter(d => d.getUTCFullYear() >= 2004)
    .forEach(d => {
      const y = d.getUTCFullYear();
      yearDist[y] = (yearDist[y] || 0) + 1;
    });

  const scores   = records.map(r => r.xscore).filter(s => typeof s === "number");
  const avgScore = scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
  const maxScore = scores.length ? Math.max(...scores) : 0;
  const minScore = scores.length ? Math.min(...scores) : 0;

  const uniqueGroups   = new Set(records.map(r => r.group).filter(Boolean));
  const perfectMatches = records.filter(r => r.perfectmatch).length;
  const inStoreCount   = records.filter(r => r.instore).length;

  const darknetCount    = (byBucket["Darknet » Tor"] || 0) + (byBucket["Darknet » I2P"] || 0);
  const credLogsCount   = byBucket["Leaks » Logs"]                 || 0;
  const restrictedCount = byBucket["Leaks » Restricted » General"] || 0;
  const pasteCount      = byBucket["Pastes"]                       || 0;
  const emailFileCount  = byMedia["Email File"]                    || 0;
  const dbFileCount     = byMedia["Database File"]                 || 0;
  const csvFileCount    = byMedia["CSV File"]                      || 0;
  const publicCount     = byAccess["Public"]                       || 0;
  const whoisCount      = byBucket["Whois"]                        || 0;

  let weightedSum = 0;
  for (const [level, count] of Object.entries(riskBreakdown)) {
    weightedSum += (RISK_WEIGHTS[level] || 0) * count;
  }
  let overallScore = Math.min(100, Math.round(weightedSum / total));
  if (riskBreakdown.CRITICAL > 0 && overallScore < 60)                    overallScore = 60;
  if ((riskBreakdown.HIGH || 0) / total > 0.2 && overallScore < 40)       overallScore = 40;
  const overallLabel = riskLabel(overallScore);

  const threats = [];
  if (darknetCount    > 0) threats.push({ severity: "CRITICAL", message: `Found in ${darknetCount} dark web records (Tor/I2P).`,          detail: "Credentials may be circulating in criminal marketplaces." });
  if (credLogsCount   > 0) threats.push({ severity: "HIGH",     message: `${credLogsCount} credential stealer log records.`,              detail: "Infostealer malware may have harvested passwords from infected devices." });
  if (restrictedCount > 0) threats.push({ severity: "HIGH",     message: `${restrictedCount} records in restricted breach databases.`,    detail: "Data present in databases requiring elevated access." });
  if (emailFileCount  > 0) threats.push({ severity: "HIGH",     message: `${emailFileCount} actual email files indexed.`,                 detail: "Full email messages exposed — potential content leakage." });
  if (dbFileCount     > 0) threats.push({ severity: "HIGH",     message: `${dbFileCount} database dump exposures.`,                      detail: "Structured data (logins, personal info) from breached databases." });
  if (csvFileCount    > 0) threats.push({ severity: "MEDIUM",   message: `${csvFileCount} CSV file exposures.`,                          detail: "Tabular exports often contain credentials or personal details." });
  if (publicCount     > 0) threats.push({ severity: "MEDIUM",   message: `${publicCount} publicly accessible records.`,                  detail: "Any actor can access these records without authentication." });
  if (pasteCount      > 0) threats.push({ severity: "MEDIUM",   message: `${pasteCount} appearances on paste sites.`,                    detail: "Data has been publicly posted — common method for distributing dumps." });
  if (uniqueGroups.size > 100) threats.push({ severity: "HIGH", message: `Spans ${uniqueGroups.size} distinct source datasets.`,         detail: "Broad multi-breach exposure significantly increases account takeover risk." });

  const hasCriticalOrHigh = (riskBreakdown.CRITICAL || 0) > 0 || (riskBreakdown.HIGH || 0) > 0;
  const recs = [];

  if (hasCriticalOrHigh) {
    recs.push("Change passwords immediately on all accounts linked to this email.");
    recs.push("Enable multi-factor authentication (MFA/2FA) on every service.");
    recs.push("Audit active sessions and revoke any unrecognized access.");
    recs.push("Check for unauthorized account activity (banking, social, email).");
    recs.push("Use a password manager with unique passwords per service.");
    if (credLogsCount > 0) recs.push("Scan devices for infostealer malware — credential logs detected.");
  } else if (overallLabel === "MEDIUM") {
    recs.push("Review and update passwords for accounts using this email.");
    recs.push("Enable MFA on critical services (email, banking, social media).");
    recs.push("Monitor accounts for suspicious activity.");
    recs.push("Use a password manager to avoid credential reuse.");
  } else {
    recs.push("Maintain strong, unique passwords for each service.");
    recs.push("Enable MFA wherever possible.");
    recs.push("Periodically re-check exposure as new breaches are discovered.");
  }
  if (whoisCount     > 0) recs.push("Consider WHOIS privacy to reduce public domain registration data.");
  if (emailFileCount > 0) recs.push("Audit email account for unauthorized forwarding rules or app access.");

  return {
    total,
    overallScore,
    overallLabel,
    riskBreakdown,
    byBucket,
    byMedia,
    byAccess,
    earliestDate,
    latestDate,
    yearDist,
    avgScore:      parseFloat(avgScore.toFixed(2)),
    maxScore,
    minScore,
    uniqueGroups:  uniqueGroups.size,
    perfectMatches,
    inStoreCount,
    darknetCount,
    credLogsCount,
    restrictedCount,
    threats,
    recs,
    percent: (n) => percent(n, total),
  };
}

module.exports = { analyse, bucketMeta, riskLabel, fmtDate, percent, RISK_COLORS };
