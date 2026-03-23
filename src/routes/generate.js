"use strict";

const express      = require("express");
const { spawn }    = require("child_process");
const path         = require("path");
const { intelxSearch }    = require("../lib/intelx");
const { breachvipSearch } = require("../lib/breachvip");
const { analyse, normalizeBreach } = require("../lib/parser");
const { buildPdf }        = require("../lib/pdf");

const router = express.Router();
const ROOT   = path.join(__dirname, "..", "..");

const MAX_CONCURRENT = 5;
let   _active        = 0;
const _queue         = [];

function acquireSlot() {
  return new Promise(resolve => {
    if (_active < MAX_CONCURRENT) { _active++; resolve(); }
    else _queue.push(resolve);
  });
}

function releaseSlot() {
  if (_queue.length > 0) { _queue.shift()(); }
  else _active--;
}

async function runPlatformCheck(email, personnummer = "") {
  await acquireSlot();
  return new Promise((resolve) => {
    const py = spawn("python", [path.join("src", "check_email.py"), email, personnummer], { cwd: ROOT });
    let out = "", err = "";
    py.stdout.on("data", d => { out += d; });
    py.stderr.on("data", d => { err += d; });
    py.on("close", code => {
      releaseSlot();
      if (code !== 0) { console.error("[generate] python error:", err); resolve(null); return; }
      try { resolve(JSON.parse(out)); } catch { resolve(null); }
    });
    py.on("error", () => { releaseSlot(); resolve(null); });
  });
}

function emptySummary() {
  return {
    total: 0, overallScore: 0, overallLabel: "MINIMAL",
    riskBreakdown: { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0, INFO: 0, UNKNOWN: 0 },
    byBucket: {}, byMedia: {}, byAccess: {},
    earliestDate: "N/A", latestDate: "N/A", yearDist: {},
    avgScore: 0, maxScore: 0, minScore: 0,
    uniqueGroups: 0, perfectMatches: 0, inStoreCount: 0,
    darknetCount: 0, credLogsCount: 0, restrictedCount: 0,
    threats: [], recs: ["Enable MFA wherever possible.", "Use unique passwords per service."],
    percent: () => "0.0",
  };
}

router.post("/", async (req, res) => {
  const {
    email,
    name, phone, username,
    personnummer,
  } = req.body || {};

  if (!email || typeof email !== "string" || !email.includes("@")) {
    return res.status(400).json({ error: "A valid email address is required." });
  }

  const target  = email.trim();
  const targets = {
    email:    target,
    name:     name?.trim()     || "",
    phone:    phone?.trim()    || "",
    username: username?.trim() || "",
  };

  const [records, platforms, breaches] = await Promise.all([
    intelxSearch(target).catch(err => { console.error("[generate] intelx:", err.message); return []; }),
    runPlatformCheck(target, personnummer || ""),
    breachvipSearch(target).catch(err => { console.error("[generate] breachvip:", err.message); return []; }).then(bs => bs.map(normalizeBreach)),
  ]);

  const summary = records.length > 0 ? analyse(records) : emptySummary();

  try {
    const pdf = await buildPdf(summary, { targets, platforms, breaches });

    const slug     = target.replace(/[^a-z0-9]/gi, "_");
    const filename = `report-${slug}.pdf`;
    res.set({
      "Content-Type":        "application/pdf",
      "Content-Disposition": `attachment; filename="${filename}"`,
      "Content-Length":      pdf.length,
    });
    res.send(pdf);
  } catch (err) {
    console.error("[generate] PDF build failed:", err);
    res.status(500).json({ error: "Failed to generate PDF." });
  }
});

module.exports = router;
