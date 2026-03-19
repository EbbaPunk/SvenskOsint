"use strict";

const express         = require("express");
const { intelxSearch } = require("../lib/intelx");

const router = express.Router();

router.post("/", async (req, res) => {
  const { email } = req.body || {};
  if (!email || typeof email !== "string" || !email.includes("@")) {
    return res.status(400).json({ error: "A valid email address is required." });
  }

  try {
    const records = await intelxSearch(email.trim());
    res.json({ records });
  } catch (err) {
    console.error("[intelx]", err.message);
    res.status(502).json({ error: "IntelX query failed.", detail: err.message });
  }
});

module.exports = router;
