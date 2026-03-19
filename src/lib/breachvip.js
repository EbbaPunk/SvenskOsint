"use strict";

const https = require("https");


function breachvipSearch(email) {
  const body = JSON.stringify({
    term:           email,
    fields:         ["email"],
    wildcard:       false,
    case_sensitive: false,
  });

  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: "breach.vip",
      path:     "/api/search",
      method:   "POST",
      headers:  {
        "Content-Type":   "application/json",
        "Content-Length": Buffer.byteLength(body),
        "User-Agent":     "Mozilla/5.0",
        "Accept":         "application/json",
      },
    }, res => {
      let data = "";
      res.on("data", chunk => { data += chunk; });
      res.on("end", () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.results && Array.isArray(parsed.results)) {
            resolve(parsed.results);
          } else {
            resolve([]);
          }
        } catch {
          resolve([]);
        }
      });
    });

    req.on("error", err => {
      console.error("[breachvip] request error:", err.message);
      resolve([]);
    });

    req.setTimeout(15000, () => {
      req.destroy();
      resolve([]);
    });

    req.write(body);
    req.end();
  });
}

module.exports = { breachvipSearch };
