"use strict";

const PLATFORM_META = {
  aftonbladet:           { category: "Media",        country: "SE", tag: "Kvällstidning / vänster" },
  expressen:             { category: "Media",        country: "SE", tag: "Kvällstidning / liberal" },
  dn:                    { category: "Media",        country: "SE", tag: "Dagstidning / center-liberal" },
  di:                    { category: "Media",        country: "SE", tag: "Affärspress" },
  tv4:                   { category: "Media",        country: "SE", tag: "Kommersiell TV" },
  samnytt:               { category: "Media",        country: "SE", tag: "Alternativmedia / nationalistisk" },
  omni:                  { category: "Media",        country: "SE", tag: "Nyhetsaggregator / centrisk" },
  "Liberalerna":         { category: "Political",    country: "SE", tag: "Center-liberal",          lean: "center"   },
  "Miljöpartiet":        { category: "Political",    country: "SE", tag: "Grön / ekologisk",        lean: "left"     },
  "zetk/Vänsterpartiet": { category: "Political",    country: "SE", tag: "Socialistisk vänster",    lean: "far-left" },
  blocket:               { category: "Marketplace",  country: "SE", tag: "Annonsmarknad" },
  hemnet:                { category: "Marketplace",  country: "SE", tag: "Bostadsmarknaden" },
  bytbil:                { category: "Marketplace",  country: "SE", tag: "Bilmarknad" },
  willys:                { category: "Retail",       country: "SE", tag: "Dagligvaror (Willys)" },
  systembolaget:         { category: "Retail",       country: "SE", tag: "Systembolaget" },
  elgiganten:            { category: "Retail",       country: "SE", tag: "Elektronikhandel" },
  inet:                  { category: "Retail",       country: "SE", tag: "Elektronikhandel" },
  komplett:              { category: "Retail",       country: "SE", tag: "Elektronikhandel" },
  byggahus:              { category: "Community",    country: "SE", tag: "Byggforum" },
  lovable:               { category: "Tech",         country: "SE", tag: "AI-plattform för webbutveckling" },
  "Jägarförbundet":      { category: "Community",    country: "SE", tag: "Svenska Jägarförbundet — jakt & friluftsliv" },
  "Jägarförbundet/SSN":  { category: "Community",    country: "SE", tag: "Svenska Jägarförbundet (personnummer)" },
  utsidan:               { category: "Community",    country: "SE", tag: "Friluftsforum — vandring, jakt, fiske" },
  "7-Eleven":            { category: "Retail",       country: "SE", tag: "Butikskedja / kvittoapp" },
  "Pressbyrån":          { category: "Retail",       country: "SE", tag: "Butikskedja / kvittoapp" },
  foodora:               { category: "Food",         country: "SE", tag: "Matleverans" },
  "mail.ru":             { category: "Email",        country: "RU", tag: "Rysk e-post / socialt" },
  rambler:               { category: "Email",        country: "RU", tag: "Ryskt webbportal" },
  deliveroo:             { category: "Food",         country: "UK", tag: "Matleverans (UK/EU)" },
  adobe:                 { category: "Creative",     country: "US", tag: "Creative Cloud" },
  "archive.org":         { category: "Research",     country: "US", tag: "Digitalt arkiv" },
  bible:                 { category: "Religious",    country: "US", tag: "Bibel / religiöst innehåll" },
  bodybuilding:          { category: "Fitness",      country: "US", tag: "Träning / kosttillskott" },
  flickr:                { category: "Creative",     country: "US", tag: "Fotodelning" },
  insightly:             { category: "Business",     country: "US", tag: "CRM / affärsverktyg" },
  lastpass:              { category: "Security",     country: "US", tag: "Lösenordshanterare" },
  medal:                 { category: "Gaming",       country: "US", tag: "Spelklipp" },
  microsoft:             { category: "Software",     country: "US", tag: "Microsoft-konto" },
  office365:             { category: "Software",     country: "US", tag: "Microsoft 365" },
  teamtreehouse:         { category: "Education",    country: "US", tag: "Kodutbildning" },
  vimeo:                 { category: "Creative",     country: "US", tag: "Videoplattform" },
  lovense:               { category: "Adult",        country: "GLOBAL", tag: "Vuxen — intima enheter" },
  xvideos:               { category: "Adult",        country: "GLOBAL", tag: "Vuxeninnehåll" },
  plurk:                 { category: "Social",       country: "GLOBAL", tag: "Social mikroblogg" },
  w3schools:             { category: "Education",    country: "GLOBAL", tag: "Webbutvecklingsutbildning" },
  freelancer:            { category: "Work",         country: "GLOBAL", tag: "Frilansmarknad" },
};


function _found(platforms, key) {
  const d = platforms?.[key];
  if (!d || typeof d !== "object") return false;
  return (typeof d.accountExists === "boolean" ? d.accountExists : null)
      ?? (typeof d.exists        === "boolean" ? d.exists        : false);
}

function _anyFound(platforms, keys) {
  return keys.some(k => _found(platforms, k));
}


function _latestActivity(platforms) {
  let latest = null;
  for (const data of Object.values(platforms || {})) {
    for (const field of ["lastLogin", "lastActive"]) {
      const v = data?.[field];
      if (!v) continue;
      const d = new Date(v);
      if (!isNaN(d) && (!latest || d > latest)) latest = d;
    }
  }
  return latest;
}

function _earliestBreach(breaches) {
  if (!Array.isArray(breaches) || breaches.length === 0) return null;
  let earliest = null;
  for (const b of breaches) {
    const raw = b?.BreachDate || b?.date || b?.AddedDate;
    if (!raw) continue;
    const d = new Date(raw);
    if (!isNaN(d) && (!earliest || d < earliest)) earliest = d;
  }
  return earliest;
}

function _inferOccupation(platforms) {
  const scores = {
    "Mjukvaruutvecklare / Tech":      0,
    "Kreativ / Designer":             0,
    "Affärsprofil / Säljare":         0,
    "Hantverkare / Heminredning":     0,
    "Religiös / Konservativ profil":  0,
    "Jakt / Friluftsliv":             0,
  };

  if (_found(platforms, "teamtreehouse")) scores["Mjukvaruutvecklare / Tech"]  += 3;
  if (_found(platforms, "w3schools"))     scores["Mjukvaruutvecklare / Tech"]  += 2;
  if (_found(platforms, "lovable"))       scores["Mjukvaruutvecklare / Tech"]  += 2;
  if (_found(platforms, "lastpass"))      scores["Mjukvaruutvecklare / Tech"]  += 1;
  if (_found(platforms, "komplett"))      scores["Mjukvaruutvecklare / Tech"]  += 1;
  if (_found(platforms, "inet"))          scores["Mjukvaruutvecklare / Tech"]  += 1;

  if (_found(platforms, "adobe"))         scores["Kreativ / Designer"]         += 3;
  if (_found(platforms, "flickr"))        scores["Kreativ / Designer"]         += 2;
  if (_found(platforms, "vimeo"))         scores["Kreativ / Designer"]         += 2;
  if (_found(platforms, "freelancer"))    scores["Kreativ / Designer"]         += 1;

  if (_found(platforms, "insightly"))     scores["Affärsprofil / Säljare"]     += 4;
  if (_found(platforms, "di"))            scores["Affärsprofil / Säljare"]     += 3;
  if (_found(platforms, "office365"))     scores["Affärsprofil / Säljare"]     += 2;
  if (_found(platforms, "freelancer"))    scores["Affärsprofil / Säljare"]     += 1;

  if (_found(platforms, "byggahus"))      scores["Hantverkare / Heminredning"] += 4;
  if (_found(platforms, "hemnet"))        scores["Hantverkare / Heminredning"] += 2;
  if (_found(platforms, "elgiganten"))    scores["Hantverkare / Heminredning"] += 1;

  if (!scores["Jakt / Friluftsliv"]) scores["Jakt / Friluftsliv"] = 0;
  if (_found(platforms, "Jägarförbundet") || _found(platforms, "Jägarförbundet/SSN"))
                                          scores["Jakt / Friluftsliv"] += 5;
  if (_found(platforms, "utsidan"))       scores["Jakt / Friluftsliv"] += 3;

  if (_found(platforms, "bible"))         scores["Religiös / Konservativ profil"] += 4;

  const top = Object.entries(scores).sort((a, b) => b[1] - a[1]);
  if (top[0][1] === 0) return null;
  const results = top.filter(([, s]) => s > 0).map(([label, score]) => ({
    label,
    score,
    confidence: Math.min(95, score * 12),
  }));
  return results.length > 0 ? results : null;
}

function _inferAge(platforms, breaches) {
  const signals = [];
  let minAge = 13;
  let maxAge = 90;

  if (_found(platforms, "systembolaget")) {
    const method = platforms["systembolaget"]?.method;
    if (method === "bankid") signals.push({ note: "BankID verifierad — myndig svensk person", weight: 95 });
    minAge = Math.max(minAge, 20);
  }
  if (_found(platforms, "willys"))  { minAge = Math.max(minAge, 18); }
  if (_found(platforms, "hemnet"))  { minAge = Math.max(minAge, 22); signals.push({ note: "Bostadsintresse tyder på vuxen (22+)", weight: 60 }); }
  if (_found(platforms, "bytbil"))  { minAge = Math.max(minAge, 18); signals.push({ note: "Bilsökning — körkortsålder (18+)", weight: 70 }); }
  if (_found(platforms, "blocket")) { minAge = Math.max(minAge, 16); }

  if (_found(platforms, "insightly") || _found(platforms, "di")) {
    minAge = Math.max(minAge, 23);
    maxAge = Math.min(maxAge, 65);
    signals.push({ note: "Affärsplattformar — trolig yrkesverksam ålder (23–65)", weight: 55 });
  }

  if (_found(platforms, "teamtreehouse") || _found(platforms, "w3schools")) {
    maxAge = Math.min(maxAge, 50);
    signals.push({ note: "Utbildningsplattformar — trolig studerandeålder", weight: 45 });
  }

  const earliest = _earliestBreach(breaches);
  if (earliest) {
    const yearsSince = new Date().getFullYear() - earliest.getFullYear();
    const impliedMinAge = 13 + yearsSince;
    if (impliedMinAge > minAge) {
      minAge = impliedMinAge;
      signals.push({ note: `Tidigaste intrång ${earliest.getFullYear()} — konto sedan minst ${yearsSince} år`, weight: 70 });
    }
  }

  const latest = _latestActivity(platforms);
  if (latest) {
    signals.push({ note: `Senaste aktivitet: ${latest.toISOString().slice(0, 10)}`, weight: 80 });
  }

  return { minAge, maxAge: Math.max(minAge, maxAge), signals };
}

function _inferLocation(platforms) {
  const locations = [];

  const seCount = Object.keys(PLATFORM_META)
    .filter(k => PLATFORM_META[k].country === "SE" && _found(platforms, k)).length;

  if (seCount >= 3) locations.push({ country: "Sverige", confidence: Math.min(95, 50 + seCount * 8), note: `${seCount} svenska plattformar funna` });

  const bankid = platforms?.["systembolaget"]?.method === "bankid" && _found(platforms, "systembolaget");
  if (bankid) locations.push({ country: "Sverige (bekräftat)", confidence: 98, note: "BankID-inloggning = folkbokförd i Sverige" });

  if (_found(platforms, "deliveroo")) locations.push({ country: "UK / EU", confidence: 60, note: "Deliveroo-konto" });
  if (_anyFound(platforms, ["mail.ru", "rambler"])) locations.push({ country: "Ryssland / rysk koppling", confidence: 75, note: "Ryskt e-postkonto" });
  const jagarFound = _found(platforms, "Jägarförbundet") || _found(platforms, "Jägarförbundet/SSN");
  if (jagarFound) locations.push({ country: "Sverige (landsbygd / glesbygd möjlig)", confidence: 72, note: "Jägarförbundet-konto — sannolikt ruralt intresse" });

  return locations;
}

function _inferLifestyle(platforms) {
  const traits = [];

  if (_found(platforms, "bodybuilding"))traits.push({ trait: "Träning / fitness",         confidence: 75 });
  if (_found(platforms, "bible"))       traits.push({ trait: "Religiös livsstil",          confidence: 80 });
  if (_found(platforms, "medal"))       traits.push({ trait: "Aktiv spelare / gamer",     confidence: 75 });
  if (_found(platforms, "byggahus"))    traits.push({ trait: "Hem- och byggintresse",     confidence: 70 });
  if (_found(platforms, "hemnet"))      traits.push({ trait: "Bostadsintresse (köp/sälj)", confidence: 65 });
  if (_found(platforms, "bytbil"))      traits.push({ trait: "Bilintresse",               confidence: 60 });
  if (_found(platforms, "Jägarförbundet") || _found(platforms, "Jägarförbundet/SSN"))
                                        traits.push({ trait: "Jägare / skogsbruk",        confidence: 90 });
  if (_found(platforms, "utsidan"))     traits.push({ trait: "Friluftsliv / natur",        confidence: 80 });
  if (_found(platforms, "foodora"))     traits.push({ trait: "Urban livsstil",             confidence: 60 });
  if (_found(platforms, "plurk"))       traits.push({ trait: "Social medieanvändare",     confidence: 55 });
  if (_found(platforms, "flickr") || _found(platforms, "vimeo"))
                                        traits.push({ trait: "Kreativ / visuell",          confidence: 65 });
  if (_anyFound(platforms, ["lovense", "xvideos"]))
                                        traits.push({ trait: "Vuxeninnehållskonsument",   confidence: 85 });

  return traits;
}

function _inferIncomeSignal(platforms) {
  let score = 0;
  const signals = [];

  if (_found(platforms, "di"))          { score += 3; signals.push("DI-prenumerant"); }
  if (_found(platforms, "insightly"))   { score += 2; signals.push("CRM-verktyg"); }
  if (_found(platforms, "adobe"))       { score += 2; signals.push("Adobe Creative Cloud"); }
  if (_found(platforms, "lastpass"))    { score += 1; signals.push("Lösenordshanterare"); }
  if (_found(platforms, "hemnet"))      { score += 2; signals.push("Bostadssökning"); }
  if (_found(platforms, "office365"))   { score += 1; signals.push("Microsoft 365"); }
  if (_found(platforms, "freelancer"))  { score -= 1; signals.push("Frilansmarknad"); }

  if (score >= 6) return { level: "Hög",    score, signals };
  if (score >= 3) return { level: "Medel",  score, signals };
  if (score >= 1) return { level: "Medel–", score, signals };
  return { level: "Okänd", score, signals };
}

function _inferSecurityPosture(platforms, breaches) {
  let score = 100;
  const notes = [];

  const ms = platforms?.["microsoft"];
  if (ms?.twoFA === false && _found(platforms, "microsoft")) { score -= 20; notes.push("Microsoft-konto saknar 2FA"); }
  if (ms?.twoFA === true)                                    { score += 5;  notes.push("2FA aktiverat på Microsoft"); }
  if (_found(platforms, "lastpass"))                         { score += 10; notes.push("Använder lösenordshanterare"); }

  const bc = Array.isArray(breaches) ? breaches.length : 0;
  if (bc >= 10)      { score -= 30; notes.push(`${bc} dataintrång — kritiskt`); }
  else if (bc >= 5)  { score -= 15; notes.push(`${bc} dataintrång`); }
  else if (bc >= 1)  { score -= 5;  notes.push(`${bc} dataintrång`); }

  score = Math.max(0, Math.min(100, score));
  const label = score >= 80 ? "Bra" : score >= 55 ? "Medel" : score >= 30 ? "Svag" : "Kritisk";
  return { score, label, notes };
}

function _buildNarrative(profile) {
  const parts = [];

  if (profile.locationSignals.some(l => l.confidence >= 90)) {
    parts.push("Personen är med hög säkerhet folkbokförd i Sverige.");
  } else if (profile.locationSignals.some(l => l.country === "Sverige")) {
    parts.push("Personen har trolig anknytning till Sverige baserat på plattformsnärvaro.");
  }

  if (profile.occupation?.length > 0) {
    const top = profile.occupation[0];
    parts.push(`Trolig yrkesroll: ${top.label} (konfidens ${top.confidence}%).`);
  }

  if (profile.political.length > 0) {
    const parties = profile.political.map(p => p.name).join(", ");
    parts.push(`Politisk aktivitet registrerad: ${parties}.`);
  }

  if (profile.mediaOutlets.length > 0) {
    const outlets = profile.mediaOutlets.map(m => m.name).join(", ");
    parts.push(`Mediakonsumtion: ${outlets}.`);
  }

  if (profile.securityPosture.label === "Kritisk" || profile.securityPosture.label === "Svag") {
    parts.push(`Säkerhetsprofil bedöms som ${profile.securityPosture.label.toLowerCase()} — ${profile.securityPosture.notes[0] || ""}.`);
  }

  return parts.join(" ") || "Otillräcklig data för att bygga profil.";
}


function buildProfile(platforms, summary, breaches) {
  const profile = {
    names:           [],
    geography:       [],
    political:       [],
    politicalLean:   null,
    mediaOutlets:    [],
    mediaBias:       null,
    interests:       [],
    riskSignals:     [],
    swedishSignals:  0,
    totalChecked:    0,
    totalFound:      0,
    breachCount:     0,
    occupation:      null,
    ageEstimate:     null,
    locationSignals: [],
    lifestyle:       [],
    incomeSignal:    null,
    securityPosture: null,
    narrative:       "",
  };

  for (const data of Object.values(platforms || {})) {
    if (!data || typeof data !== "object") continue;
    const full = [data.firstName, data.lastName].filter(Boolean).join(" ");
    if (full && !profile.names.includes(full)) profile.names.push(full);
  }

  for (const [key, data] of Object.entries(platforms || {})) {
    if (!data || typeof data !== "object") continue;
    profile.totalChecked++;

    const found =
      (typeof data.accountExists === "boolean" ? data.accountExists : null) ??
      (typeof data.exists        === "boolean" ? data.exists        : false);

    if (!found) continue;
    profile.totalFound++;

    const meta = PLATFORM_META[key];
    if (!meta) continue;

    if (meta.country === "SE") profile.swedishSignals++;
    if (!profile.geography.includes(meta.country)) profile.geography.push(meta.country);
    if (meta.category === "Political") profile.political.push({ name: key, tag: meta.tag, lean: meta.lean });
    if (meta.category === "Media")     profile.mediaOutlets.push({ name: key, tag: meta.tag });
    if (!profile.interests.includes(meta.category)) profile.interests.push(meta.category);
  }

  if (profile.political.length > 0) {
    const leans = profile.political.map(p => p.lean).filter(Boolean);
    if (leans.includes("far-left"))    profile.politicalLean = "Långt vänster";
    else if (leans.includes("left"))   profile.politicalLean = "Vänster / Grön";
    else if (leans.includes("center")) profile.politicalLean = "Center";
  }

  const altRight = profile.mediaOutlets.some(m => m.name === "samnytt");
  const leftTab  = profile.mediaOutlets.some(m => m.name === "aftonbladet");
  const business = profile.mediaOutlets.some(m => m.name === "di");
  if (altRight)      profile.mediaBias = "Nationalistisk / alternativmedia";
  else if (business) profile.mediaBias = "Affärsorienterad";
  else if (leftTab)  profile.mediaBias = "Kvällstidning / vänster";

  profile.breachCount = Array.isArray(breaches) ? breaches.length : 0;

  profile.occupation      = _inferOccupation(platforms);
  profile.ageEstimate     = _inferAge(platforms, breaches);
  profile.locationSignals = _inferLocation(platforms);
  profile.lifestyle       = _inferLifestyle(platforms);
  profile.incomeSignal    = _inferIncomeSignal(platforms);
  profile.securityPosture = _inferSecurityPosture(platforms, breaches);

  const ms = platforms?.["microsoft"];
  if (ms?.backupEmail)                               profile.riskSignals.push(`Microsoft backup-e-post: ${ms.backupEmail}`);
  if (ms?.twoFA === false && _found(platforms, "microsoft")) profile.riskSignals.push("Microsoft-konto saknar 2FA");
  if (Array.isArray(ms?.phones) && ms.phones.length) profile.riskSignals.push(`Telefon på Microsoft: ${ms.phones[0]}`);

  if (profile.breachCount > 0)        profile.riskSignals.push(`Hittad i ${profile.breachCount} dataintrång`);
  if (summary?.darknetCount  > 0)     profile.riskSignals.push(`Förekommer i ${summary.darknetCount} darknet-dataset`);
  if (summary?.credLogsCount > 0)     profile.riskSignals.push(`Förekommer i ${summary.credLogsCount} credential logs`);

  const adultFound = Object.keys(platforms || {})
    .filter(k => _found(platforms, k) && PLATFORM_META[k]?.category === "Adult");
  if (adultFound.length)              profile.riskSignals.push(`Vuxenplattformar: ${adultFound.join(", ")}`);
  if (profile.geography.includes("RU")) profile.riskSignals.push("Ryskt plattformsnärvaro (mail.ru / Rambler)");
  if (_found(platforms, "Jägarförbundet") || _found(platforms, "Jägarförbundet/SSN"))
    profile.riskSignals.push("Registrerad jägare — trolig vapeninnehavare");

  profile.narrative = _buildNarrative(profile);

  return profile;
}

module.exports = { buildProfile };
