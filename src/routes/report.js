"use strict";

const express = require("express");
const multer  = require("multer");
const { analyse } = require("../lib/parser");
const { buildPdf } = require("../lib/pdf");

const router = express.Router();
const upload = multer({
  storage: multer.memoryStorage(),
  limits:  { fileSize: 50 * 1024 * 1024 },
});

router.post("/", async (req, res) => {
  const { records, email, platforms } = req.body || {};
  if (!Array.isArray(records)) {
    return res.status(400).json({ error: "Body must contain a records array." });
  }
  await generate(res, records, { email, platforms });
});

router.post("/upload", upload.single("file"), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: "No file uploaded. Use field name file." });

  let parsed;
  try {
    parsed = JSON.parse(req.file.buffer.toString("utf8"));
  } catch {
    return res.status(400).json({ error: "Uploaded file is not valid JSON." });
  }

  const records = parsed.records;
  if (!Array.isArray(records)) {
    return res.status(422).json({ error: "JSON must contain a records array." });
  }

  await generate(res, records, {});
});

async function generate(res, records, meta = {}) {
  const realRecords = records.filter(r => !r._dummy);
  const hasPlatforms = meta.platforms && Object.keys(meta.platforms).length > 0;

  if (realRecords.length === 0 && !hasPlatforms) {
    return res.status(422).json({ error: "No data to report. Provide records or platform data." });
  }

  try {
    const summary = realRecords.length > 0
      ? analyse(realRecords)
      : emptySummary();
    const pdf     = await buildPdf(summary, meta);
    res.set({
      "Content-Type":        "application/pdf",
      "Content-Disposition": "attachment; filename='security-report.pdf'",
      "Content-Length":      pdf.length,
    });
    res.send(pdf);
  } catch (err) {
    console.error("[report] PDF generation failed:", err);
    res.status(500).json({ error: "Failed to generate report." });
  }
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

module.exports = router;
