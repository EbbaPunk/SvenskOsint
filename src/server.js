"use strict";

require("dotenv").config({ path: require("path").join(__dirname, "..", ".env") });

const express      = require("express");
const path         = require("path");
const reportRouter   = require("./routes/report");
const searchRouter   = require("./routes/search");
const intelxRouter   = require("./routes/intelx");
const generateRouter = require("./routes/generate");

const app  = express();
const PORT = process.env.PORT || 33;

app.use(express.json({ limit: "50mb" }));
app.use(express.static(path.join(__dirname, "public")));

app.use("/report",   reportRouter);
app.use("/search",   searchRouter);
app.use("/intelx",   intelxRouter);
app.use("/generate", generateRouter);

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
