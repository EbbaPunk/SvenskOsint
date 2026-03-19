"use strict";

const PLATFORM_META = {
  aftonbladet: { category: "Media",    country: "SE", tag: "Tabloid / left-leaning" },
  expressen:   { category: "Media",    country: "SE", tag: "Tabloid / liberal" },
  dn:          { category: "Media",    country: "SE", tag: "Broadsheet / center-liberal" },
  di:          { category: "Media",    country: "SE", tag: "Business press" },
  tv4:         { category: "Media",    country: "SE", tag: "Commercial TV" },
  samnytt:     { category: "Media",    country: "SE", tag: "Alt-right / nationalist" },

  "Liberalerna":         { category: "Political", country: "SE", tag: "Centre-liberal",     lean: "center" },
  "Miljöpartiet":        { category: "Political", country: "SE", tag: "Green / ecological", lean: "left" },
  "zetk/Vänsterpartiet": { category: "Political", country: "SE", tag: "Socialist left",     lean: "far-left" },

  blocket:      { category: "Marketplace", country: "SE", tag: "Classifieds marketplace" },
  hemnet:       { category: "Real estate", country: "SE", tag: "Property listings" },
  willys:       { category: "Retail",      country: "SE", tag: "Grocery loyalty (Willys)" },
  systembolaget:{ category: "Retail",      country: "SE", tag: "Systembolaget" },
  elgiganten:   { category: "Retail",      country: "SE", tag: "Electronics retailer" },
  inet:         { category: "Retail",      country: "SE", tag: "Electronics retailer" },
  bytbil:       { category: "Marketplace", country: "SE", tag: "Car marketplace" },
  byggahus:     { category: "Community",   country: "SE", tag: "Home improvement forum" },
  loveable:     { category: "Community",   country: "SE", tag: "AI development platform" },

  "mail.ru": { category: "Email",        country: "RU", tag: "Russian email/social" },
  rambler:   { category: "Email",        country: "RU", tag: "Russian portal" },

  deliveroo: { category: "Food delivery", country: "UK", tag: "Food delivery (UK/EU)" },

  adobe:         { category: "Software",  country: "US", tag: "Creative cloud" },
  "archive.org": { category: "Research",  country: "US", tag: "Digital archive" },
  bible:         { category: "Religious", country: "US", tag: "Bible / faith content" },
  bodybuilding:  { category: "Fitness",   country: "US", tag: "Fitness / supplements" },
  devrant:       { category: "Tech",      country: "US", tag: "Developer community" },
  flickr:        { category: "Creative",  country: "US", tag: "Photo sharing" },
  insightly:     { category: "Business",  country: "US", tag: "CRM / business tool" },
  lastpass:      { category: "Security",  country: "US", tag: "Password manager" },
  medal:         { category: "Gaming",    country: "US", tag: "Game clip sharing" },
  microsoft:     { category: "Software",  country: "US", tag: "Microsoft account" },
  office365:     { category: "Software",  country: "US", tag: "Microsoft 365" },
  teamtreehouse: { category: "Education", country: "US", tag: "Coding education" },
  vimeo:         { category: "Creative",  country: "US", tag: "Video hosting" },
  vivino:        { category: "Lifestyle", country: "US", tag: "Wine / dining" },

  lovense:    { category: "Adult",     country: "GLOBAL", tag: "Adult — intimate devices" },
  xvideos:    { category: "Adult",     country: "GLOBAL", tag: "Adult content" },
  plurk:      { category: "Social",    country: "GLOBAL", tag: "Social microblogging" },
  w3schools:  { category: "Education", country: "GLOBAL", tag: "Web development learning" },
  freelancer: { category: "Work",      country: "GLOBAL", tag: "Freelance marketplace" },
};

function buildProfile(platforms, summary, breaches) {
  const profile = {
    names:          [],
    geography:      [],
    political:      [],
    politicalLean:  null,
    mediaOutlets:   [],
    mediaBias:      null,
    interests:      [],
    riskSignals:    [],
    swedishSignals: 0,
    totalChecked:   0,
    totalFound:     0,
    breachCount:    0,
  };

  if (platforms && typeof platforms === "object") {
    for (const [, data] of Object.entries(platforms)) {
      if (!data || typeof data !== "object") continue;
      const full = [data.firstName, data.lastName].filter(Boolean).join(" ");
      if (full && !profile.names.includes(full)) profile.names.push(full);
    }
  }

  if (platforms && typeof platforms === "object") {
    for (const [key, data] of Object.entries(platforms)) {
      if (!data || typeof data !== "object") continue;
      profile.totalChecked++;

      const found =
        (typeof data.accountExists === "boolean" ? data.accountExists : null) ??
        (typeof data.exists        === "boolean" ? data.exists        : null);

      if (!found) continue;
      profile.totalFound++;

      const meta = PLATFORM_META[key];
      if (!meta) continue;

      if (meta.country === "SE") profile.swedishSignals++;
      if (!profile.geography.includes(meta.country)) profile.geography.push(meta.country);

      if (meta.category === "Political") {
        profile.political.push({ name: key, tag: meta.tag, lean: meta.lean });
      }

      if (meta.category === "Media") {
        profile.mediaOutlets.push({ name: key, tag: meta.tag });
      }

      if (!profile.interests.includes(meta.category)) {
        profile.interests.push(meta.category);
      }
    }
  }

  if (profile.political.length > 0) {
    const leans = profile.political.map(p => p.lean).filter(Boolean);
    if (leans.includes("far-left"))    profile.politicalLean = "Far Left";
    else if (leans.includes("left"))   profile.politicalLean = "Left / Green";
    else if (leans.includes("center")) profile.politicalLean = "Centre";
  }

  const altRight = profile.mediaOutlets.some(m => m.name === "samnytt");
  const leftTab  = profile.mediaOutlets.some(m => m.name === "aftonbladet");
  const business = profile.mediaOutlets.some(m => m.name === "di");
  if (altRight)      profile.mediaBias = "Nationalist / alt-right present";
  else if (business) profile.mediaBias = "Business-oriented";
  else if (leftTab)  profile.mediaBias = "Tabloid / left-leaning";

  profile.breachCount = Array.isArray(breaches) ? breaches.length : 0;

  if (platforms) {
    const ms = platforms["microsoft"];
    if (ms?.backupEmail) profile.riskSignals.push(`Microsoft backup email: ${ms.backupEmail}`);
    if (ms?.twoFA === false && ms?.accountExists) profile.riskSignals.push("Microsoft account has no 2FA");
    if (Array.isArray(ms?.phones) && ms.phones.length) profile.riskSignals.push(`Phone on Microsoft: ${ms.phones[0]}`);
  }

  if (profile.breachCount > 0) {
    profile.riskSignals.push(`Found in ${profile.breachCount} breach record${profile.breachCount > 1 ? "s" : ""}`);
  }
  if (summary && summary.darknetCount > 0) {
    profile.riskSignals.push(`Appears in ${summary.darknetCount} dark web dataset${summary.darknetCount > 1 ? "s" : ""}`);
  }
  if (summary && summary.credLogsCount > 0) {
    profile.riskSignals.push(`Present in ${summary.credLogsCount} credential log${summary.credLogsCount > 1 ? "s" : ""}`);
  }

  const adultPlatforms = Object.keys(platforms || {}).filter(k => {
    const found = platforms[k]?.accountExists || platforms[k]?.exists;
    return found && PLATFORM_META[k]?.category === "Adult";
  });
  if (adultPlatforms.length) {
    profile.riskSignals.push(`Adult platform presence: ${adultPlatforms.join(", ")}`);
  }

  if (profile.geography.includes("RU")) {
    profile.riskSignals.push("Russian platform presence (mail.ru / Rambler)");
  }

  return profile;
}

module.exports = { buildProfile };
