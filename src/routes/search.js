"use strict";

const express = require("express");
const { spawn } = require("child_process");
const path    = require("path");

const router  = express.Router();
const ROOT    = path.join(__dirname, "..", "..");

router.post("/", (req, res) => {
  const { email } = req.body || {};
  if (!email || typeof email !== "string" || !email.includes("@")) {
    return res.status(400).json({ error: "A valid email address is required." });
  }
  const py  = spawn("python", ["check_email.py", email.trim()], { cwd: ROOT });
  let stdout = "";
  let stderr = "";

  py.stdout.on("data", d => { stdout += d; });
  py.stderr.on("data", d => { stderr += d; });

  py.on("close", code => {
    if (code !== 0) {
      console.error("[search] python exited", code, stderr);
      return res.status(500).json({ error: "Platform check failed.", detail: stderr.slice(0, 500) });
    }
    try {
      res.json(JSON.parse(stdout));
    } catch {
      res.status(500).json({ error: "Could not parse platform results." });
    }
  });

  py.on("error", err => {
    res.status(500).json({ error: "Failed to start Python.", detail: err.message });
  });
});

module.exports = router;
