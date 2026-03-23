"use strict";

const PLATFORM_META = {
  aftonbladet:           { category: "Media",        country: "SE", tag: "Kvällstidning / vänster" },
  expressen:             { category: "Media",        country: "SE", tag: "Kvällstidning / liberal" },
  dn:                    { category: "Media",        country: "SE", tag: "Dagstidning / center-liberal" },
  di:                    { category: "Media",        country: "SE", tag: "Affärspress" },
  svd:                   { category: "Media",        country: "SE", tag: "Dagstidning / konservativ-liberal" },
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
  power:                 { category: "Retail",       country: "SE", tag: "Elektronikhandel" },
  nelly:                 { category: "Retail",       country: "SE", tag: "Modehandel (kvinna)" },
  cocopanda:             { category: "Retail",       country: "SE", tag: "Skönhet / kosmetika" },
  "7-Eleven":            { category: "Retail",       country: "SE", tag: "Butikskedja / kvittoapp" },
  "Pressbyrån":          { category: "Retail",       country: "SE", tag: "Butikskedja / kvittoapp" },
  foodora:               { category: "Food",         country: "SE", tag: "Matleverans" },
  byggahus:              { category: "Community",    country: "SE", tag: "Byggforum" },
  lovable:               { category: "Tech",         country: "SE", tag: "AI-plattform för webbutveckling" },
  "Jägarförbundet":      { category: "Community",    country: "SE", tag: "Jakt & friluftsliv" },
  "Jägarförbundet/SSN":  { category: "Community",    country: "SE", tag: "Jakt & friluftsliv (personnummer)" },
  utsidan:               { category: "Community",    country: "SE", tag: "Friluftsforum — vandring, jakt, fiske" },
  allsvenskan:           { category: "Sports",       country: "SE", tag: "Svensk fotboll" },
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

const OCCUPATION_MAX = {
  "Mjukvaruutvecklare / Tech":      12,
  "Kreativ / Designer":              9,
  "Affärsprofil / Säljare":         10,
  "Hantverkare / Heminredning":      7,
  "Religiös / Konservativ profil":   4,
  "Jakt / Friluftsliv":              8,
  "Mode / Skönhet":                  5,
  "Sport / Idrott":                  4,
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
    const raw = b?.date;
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
    "Mode / Skönhet":                 0,
    "Sport / Idrott":                 0,
  };

  if (_found(platforms, "teamtreehouse")) scores["Mjukvaruutvecklare / Tech"] += 3;
  if (_found(platforms, "w3schools"))     scores["Mjukvaruutvecklare / Tech"] += 2;
  if (_found(platforms, "lovable"))       scores["Mjukvaruutvecklare / Tech"] += 2;
  if (_found(platforms, "lastpass"))      scores["Mjukvaruutvecklare / Tech"] += 1;
  if (_found(platforms, "komplett"))      scores["Mjukvaruutvecklare / Tech"] += 1;
  if (_found(platforms, "inet"))          scores["Mjukvaruutvecklare / Tech"] += 1;
  if (_found(platforms, "elgiganten"))    scores["Mjukvaruutvecklare / Tech"] += 1;
  if (_found(platforms, "power"))         scores["Mjukvaruutvecklare / Tech"] += 1;

  if (_found(platforms, "adobe"))         scores["Kreativ / Designer"]        += 3;
  if (_found(platforms, "flickr"))        scores["Kreativ / Designer"]        += 2;
  if (_found(platforms, "vimeo"))         scores["Kreativ / Designer"]        += 2;
  if (_found(platforms, "freelancer"))    scores["Kreativ / Designer"]        += 1;
  if (_found(platforms, "nelly"))         scores["Kreativ / Designer"]        += 1;

  if (_found(platforms, "insightly"))     scores["Affärsprofil / Säljare"]    += 4;
  if (_found(platforms, "di"))            scores["Affärsprofil / Säljare"]    += 3;
  if (_found(platforms, "office365"))     scores["Affärsprofil / Säljare"]    += 2;
  if (_found(platforms, "freelancer"))    scores["Affärsprofil / Säljare"]    += 1;

  if (_found(platforms, "byggahus"))      scores["Hantverkare / Heminredning"] += 4;
  if (_found(platforms, "hemnet"))        scores["Hantverkare / Heminredning"] += 2;
  if (_found(platforms, "elgiganten"))    scores["Hantverkare / Heminredning"] += 1;

  if (_found(platforms, "Jägarförbundet") || _found(platforms, "Jägarförbundet/SSN"))
                                          scores["Jakt / Friluftsliv"]        += 5;
  if (_found(platforms, "utsidan"))       scores["Jakt / Friluftsliv"]        += 3;

  if (_found(platforms, "bible"))         scores["Religiös / Konservativ profil"] += 4;

  if (_found(platforms, "nelly"))         scores["Mode / Skönhet"]            += 3;
  if (_found(platforms, "cocopanda"))     scores["Mode / Skönhet"]            += 2;

  if (_found(platforms, "allsvenskan"))   scores["Sport / Idrott"]            += 3;
  if (_found(platforms, "bodybuilding"))  scores["Sport / Idrott"]            += 1;

  const top = Object.entries(scores).sort((a, b) => b[1] - a[1]);
  if (top[0][1] === 0) return null;

  return top
    .filter(([, s]) => s > 0)
    .map(([label, score]) => ({
      label,
      score,
      confidence: Math.min(95, Math.round((score / OCCUPATION_MAX[label]) * 100)),
    }));
}

function _inferGender(platforms) {
  const femaleHits = [];
  const maleHits   = [];

  if (_found(platforms, "nelly"))        femaleHits.push({ s: "nelly",          weight: 3 });
  if (_found(platforms, "cocopanda"))    femaleHits.push({ s: "cocopanda",       weight: 2 });
  if (_found(platforms, "bodybuilding")) maleHits.push(  { s: "bodybuilding",    weight: 2 });
  if (_found(platforms, "allsvenskan"))  maleHits.push(  { s: "allsvenskan",     weight: 2 });
  if (_found(platforms, "Jägarförbundet") || _found(platforms, "Jägarförbundet/SSN"))
                                         maleHits.push(  { s: "jägarförbundet",  weight: 2 });
  if (_found(platforms, "medal"))        maleHits.push(  { s: "medal",           weight: 2 });
  if (_found(platforms, "bytbil"))       maleHits.push(  { s: "bytbil",          weight: 1 });

  const femaleSignals = femaleHits.length;
  const maleSignals   = maleHits.length;

  if (femaleSignals + maleSignals < 2) return null;

  const femaleScore = femaleHits.reduce((s, h) => s + h.weight, 0);
  const maleScore   = maleHits.reduce((s, h)   => s + h.weight, 0);
  const total       = femaleScore + maleScore;

  const BASE_CONFIDENCE = 55;
  const signalBonus     = Math.min(20, (femaleSignals + maleSignals - 2) * 5);

  if (femaleScore > maleScore) {
    const raw = Math.round((femaleScore / total) * 100);
    return { gender: "Kvinna", confidence: Math.min(82, BASE_CONFIDENCE + signalBonus + Math.round((raw - 50) * 0.4)), signals: femaleHits };
  } else if (maleScore > femaleScore) {
    const raw = Math.round((maleScore / total) * 100);
    return { gender: "Man",   confidence: Math.min(82, BASE_CONFIDENCE + signalBonus + Math.round((raw - 50) * 0.4)), signals: maleHits };
  }
  return { gender: "Okänt", confidence: 50, signals: [...femaleHits, ...maleHits] };
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
  if (_found(platforms, "willys"))      { minAge = Math.max(minAge, 18); }
  if (_found(platforms, "hemnet"))      { minAge = Math.max(minAge, 22); signals.push({ note: "Bostadsintresse tyder på vuxen (22+)", weight: 60 }); }
  if (_found(platforms, "bytbil"))      { minAge = Math.max(minAge, 18); signals.push({ note: "Bilsökning — körkortsålder (18+)", weight: 70 }); }
  if (_found(platforms, "blocket"))     { minAge = Math.max(minAge, 16); }
  if (_found(platforms, "allsvenskan")) { minAge = Math.max(minAge, 15); signals.push({ note: "Allsvenskan-konto — trolig fotbollsintresserad vuxen", weight: 45 }); }
  if (_found(platforms, "nelly"))       { minAge = Math.max(minAge, 18); maxAge = Math.min(maxAge, 50); signals.push({ note: "Nelly-konto — trolig ung kvinna (18–50)", weight: 55 }); }

  if (_found(platforms, "insightly") || _found(platforms, "di")) {
    minAge = Math.max(minAge, 23);
    maxAge = Math.min(maxAge, 65);
    signals.push({ note: "Affärsplattformar — trolig yrkesverksam ålder (23–65)", weight: 55 });
  }

  if (_found(platforms, "teamtreehouse") || _found(platforms, "w3schools")) {
    maxAge = Math.min(maxAge, 50);
    signals.push({ note: "Utbildningsplattformar — trolig studerandeålder", weight: 45 });
  }

  if (_found(platforms, "Jägarförbundet") || _found(platforms, "Jägarförbundet/SSN")) {
    minAge = Math.max(minAge, 16);
    signals.push({ note: "Jägarförbundet kräver minst 16 år", weight: 60 });
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

  if (seCount >= 3) locations.push({ country: "Sverige", confidence: Math.min(95, 50 + seCount * 7), note: `${seCount} svenska plattformar funna` });

  const bankid = platforms?.["systembolaget"]?.method === "bankid" && _found(platforms, "systembolaget");
  if (bankid) locations.push({ country: "Sverige (bekräftat)", confidence: 98, note: "BankID-inloggning = folkbokförd i Sverige" });

  if (_found(platforms, "deliveroo"))   locations.push({ country: "UK / EU", confidence: 60, note: "Deliveroo-konto" });
  if (_anyFound(platforms, ["mail.ru", "rambler"])) locations.push({ country: "Ryssland / rysk koppling", confidence: 75, note: "Ryskt e-postkonto" });
  if (_found(platforms, "Jägarförbundet") || _found(platforms, "Jägarförbundet/SSN"))
    locations.push({ country: "Sverige (landsbygd / glesbygd möjlig)", confidence: 72, note: "Jägarförbundet — sannolikt ruralt intresse" });

  return locations;
}

function _inferUrbanRural(platforms) {
  let urbanScore = 0;
  let ruralScore = 0;
  const urbanSignals = [];
  const ruralSignals = [];

  if (_found(platforms, "foodora"))     { urbanScore += 3; urbanSignals.push("Foodora"); }
  if (_found(platforms, "7-Eleven"))    { urbanScore += 2; urbanSignals.push("7-Eleven"); }
  if (_found(platforms, "Pressbyrån"))  { urbanScore += 2; urbanSignals.push("Pressbyrån"); }
  if (_found(platforms, "deliveroo"))   { urbanScore += 2; urbanSignals.push("Deliveroo"); }
  if (_found(platforms, "allsvenskan")) { urbanScore += 1; urbanSignals.push("Allsvenskan"); }
  if (_found(platforms, "hemnet"))      { urbanScore += 1; urbanSignals.push("Hemnet"); }
  if (_found(platforms, "nelly"))       { urbanScore += 1; urbanSignals.push("Nelly"); }

  if (_found(platforms, "Jägarförbundet") || _found(platforms, "Jägarförbundet/SSN"))
                                        { ruralScore += 4; ruralSignals.push("Jägarförbundet"); }
  if (_found(platforms, "utsidan"))     { ruralScore += 3; ruralSignals.push("Utsidan"); }
  if (_found(platforms, "byggahus"))    { ruralScore += 1; ruralSignals.push("Byggahus"); }
  if (_found(platforms, "bytbil"))      { ruralScore += 1; ruralSignals.push("Bytbil"); }

  if (urbanScore === 0 && ruralScore === 0) return null;

  const total = urbanScore + ruralScore;
  if (urbanScore > ruralScore) {
    return { label: "Urban", confidence: Math.round((urbanScore / total) * 100), signals: urbanSignals };
  } else if (ruralScore > urbanScore) {
    return { label: "Landsbygd / glesbygd", confidence: Math.round((ruralScore / total) * 100), signals: ruralSignals };
  }
  return { label: "Blandad", confidence: 50, signals: [...urbanSignals, ...ruralSignals] };
}

function _inferLifestyle(platforms) {
  const traits = [];

  if (_found(platforms, "bodybuilding"))  traits.push({ trait: "Träning / fitness",            confidence: 75 });
  if (_found(platforms, "bible"))         traits.push({ trait: "Religiös livsstil",             confidence: 80 });
  if (_found(platforms, "medal"))         traits.push({ trait: "Aktiv spelare / gamer",         confidence: 75 });
  if (_found(platforms, "byggahus"))      traits.push({ trait: "Hem- och byggintresse",         confidence: 70 });
  if (_found(platforms, "hemnet"))        traits.push({ trait: "Bostadsintresse (köp/sälj)",   confidence: 65 });
  if (_found(platforms, "bytbil"))        traits.push({ trait: "Bilintresse",                   confidence: 60 });
  if (_found(platforms, "allsvenskan"))   traits.push({ trait: "Fotbollsintresserad",           confidence: 78 });
  if (_found(platforms, "nelly"))         traits.push({ trait: "Modeintresse",                  confidence: 72 });
  if (_found(platforms, "cocopanda"))     traits.push({ trait: "Skönhet / kosmetika",           confidence: 75 });
  if (_found(platforms, "Jägarförbundet") || _found(platforms, "Jägarförbundet/SSN"))
                                          traits.push({ trait: "Jägare / skogsbruk",            confidence: 90 });
  if (_found(platforms, "utsidan"))       traits.push({ trait: "Friluftsliv / natur",           confidence: 80 });
  if (_found(platforms, "foodora") || _found(platforms, "7-Eleven") || _found(platforms, "Pressbyrån"))
                                          traits.push({ trait: "Urban livsstil",                confidence: 65 });
  if (_found(platforms, "plurk"))         traits.push({ trait: "Social medieanvändare",         confidence: 55 });
  if (_found(platforms, "flickr") || _found(platforms, "vimeo"))
                                          traits.push({ trait: "Kreativ / visuell",             confidence: 65 });
  if (_anyFound(platforms, ["lovense", "xvideos"]))
                                          traits.push({ trait: "Vuxeninnehållskonsument",       confidence: 85 });

  return traits;
}

function _inferIncomeSignal(platforms) {
  let score = 0;
  const signals = [];

  if (_found(platforms, "di"))          { score += 3; signals.push("DI-prenumerant"); }
  if (_found(platforms, "svd"))         { score += 2; signals.push("SvD-prenumerant"); }
  if (_found(platforms, "insightly"))   { score += 2; signals.push("CRM-verktyg"); }
  if (_found(platforms, "adobe"))       { score += 2; signals.push("Adobe Creative Cloud"); }
  if (_found(platforms, "hemnet"))      { score += 2; signals.push("Bostadssökning"); }
  if (_found(platforms, "lastpass"))    { score += 1; signals.push("Lösenordshanterare"); }
  if (_found(platforms, "office365"))   { score += 1; signals.push("Microsoft 365"); }
  if (_found(platforms, "nelly"))       { score += 1; signals.push("Modehandel"); }
  if (_found(platforms, "freelancer"))  { score -= 1; signals.push("Frilansmarknad"); }

  if (score >= 6) return { level: "Hög",    score, signals };
  if (score >= 3) return { level: "Medel",  score, signals };
  if (score >= 1) return { level: "Medel–", score, signals };
  return { level: "Okänd", score, signals };
}

function _inferMediaBias(platforms, mediaOutlets) {
  const found = new Set(mediaOutlets.map(m => m.name));
  if (found.size === 0) return null;

  let right = 0, left = 0, business = 0, broad = 0;

  if (found.has("samnytt"))     right    += 4;
  if (found.has("svd"))         right    += 1;
  if (found.has("aftonbladet")) left     += 3;
  if (found.has("expressen"))   left     += 1;
  if (found.has("di"))          business += 3;
  if (found.has("dn"))          business += 1;
  if (found.has("omni"))        broad    += 2;
  if (found.has("tv4"))         broad    += 1;

  const scores = { right, left, business, broad };
  const top = Object.entries(scores).sort((a, b) => b[1] - a[1]);

  if (top[0][1] === 0) return null;

  const dominant = top[0][0];
  const second   = top[1][0];
  const mixed    = top[1][1] > 0 && top[0][1] - top[1][1] <= 1;

  if (mixed) {
    if (dominant === "right"    && second === "business") return "Höger / affärsorienterad";
    if (dominant === "business" && second === "right")    return "Affärs- / högerorienterad";
    if (dominant === "left"     && second === "broad")    return "Vänster / bred nyhetskonsumtion";
    if (dominant === "business" && second === "broad")    return "Affärsorienterad / bred";
    return "Blandad medieprofil";
  }

  const labels = {
    right:    "Nationalistisk / höger",
    left:     "Vänster / kvällstidning",
    business: "Affärsorienterad",
    broad:    "Bred nyhetskonsumtion",
  };
  return labels[dominant] ?? null;
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

const HEDGE = {
  HIGH:   "",
  MEDIUM: "Indikationer tyder på att ",
  LOW:    "Svaga signaler antyder möjligen att ",
};

function _hedged(confidence, statement) {
  if (confidence >= 80) return statement;
  if (confidence >= 55) return HEDGE.MEDIUM + statement.charAt(0).toLowerCase() + statement.slice(1);
  return HEDGE.LOW + statement.charAt(0).toLowerCase() + statement.slice(1);
}

function _buildNarrative(profile) {
  if (profile.totalFound < 3) {
    return `För få plattformsträffar (${profile.totalFound}) för att bygga en tillförlitlig profil. Alla slutledningar nedan bör betraktas som osäkra.`;
  }

  const parts = [];

  const bestLocation = profile.locationSignals.sort((a, b) => b.confidence - a.confidence)[0];
  if (bestLocation) {
    parts.push(_hedged(bestLocation.confidence, `Personen är folkbokförd eller verksam i ${bestLocation.country}.`));
  }

  if (profile.genderSignal && profile.genderSignal.confidence >= 60) {
    parts.push(_hedged(profile.genderSignal.confidence, `Könssignal pekar mot ${profile.genderSignal.gender.toLowerCase()}.`));
  }

  if (profile.urbanRural && profile.urbanRural.label !== "Blandad") {
    const ur = profile.urbanRural;
    parts.push(_hedged(ur.confidence, `Livsstilssignaler pekar mot ${ur.label.toLowerCase()} miljö (${ur.signals.join(", ")}).`));
  }

  if (profile.occupation?.length > 0) {
    const top = profile.occupation[0];
    if (top.confidence >= 25) {
      parts.push(_hedged(top.confidence, `Trolig yrkesroll: ${top.label}.`));
    }
  }

  if (profile.ageEstimate) {
    const { minAge, maxAge, signals } = profile.ageEstimate;
    const bestWeight = signals.length ? Math.max(...signals.map(s => s.weight)) : 0;
    if ((minAge !== 13 || maxAge !== 90) && bestWeight >= 50) {
      parts.push(_hedged(bestWeight, `Uppskattad ålder: ${minAge}–${maxAge} år.`));
    }
  }

  if (profile.incomeSignal?.level && profile.incomeSignal.level !== "Okänd" && profile.incomeSignal.score >= 3) {
    parts.push(_hedged(55, `Inkomstsignal: ${profile.incomeSignal.level} (${profile.incomeSignal.signals.join(", ")}).`));
  }

  const topLifestyle = profile.lifestyle.filter(l => l.confidence >= 75).map(l => l.trait);
  if (topLifestyle.length > 0) {
    parts.push(`Starka livsstilssignaler: ${topLifestyle.join(", ")}.`);
  }

  if (profile.political.length > 0) {
    const parties = profile.political.map(p => p.name).join(", ");
    const leanNote = profile.politicalLean ? ` (${profile.politicalLean})` : "";
    parts.push(`Politisk aktivitet registrerad: ${parties}${leanNote}.`);
  }

  if (profile.mediaOutlets.length > 0) {
    const outlets = profile.mediaOutlets.map(m => m.name).join(", ");
    const biasNote = profile.mediaBias ? ` — ${profile.mediaBias}` : "";
    parts.push(`Mediakonsumtion: ${outlets}${biasNote}.`);
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
    genderSignal:    null,
    locationSignals: [],
    urbanRural:      null,
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

  if (profile.political.length > 0 || _found(platforms, "samnytt")) {
    const leans = profile.political.map(p => p.lean).filter(Boolean);
    const uniqueLeans = [...new Set(leans)];

    if (_found(platforms, "samnytt")) uniqueLeans.push("far-right");

    if (uniqueLeans.length > 1) {
      profile.politicalLean = "Blandad / oklar politisk signal";
    } else if (uniqueLeans.includes("far-right"))  {
      profile.politicalLean = "Nationalistisk / höger";
    } else if (uniqueLeans.includes("far-left"))   {
      profile.politicalLean = "Långt vänster";
    } else if (uniqueLeans.includes("left"))       {
      profile.politicalLean = "Vänster / Grön";
    } else if (uniqueLeans.includes("center"))     {
      profile.politicalLean = "Center";
    }
  }

  profile.mediaBias = _inferMediaBias(platforms, profile.mediaOutlets);

  profile.breachCount     = Array.isArray(breaches) ? breaches.length : 0;
  profile.occupation      = _inferOccupation(platforms);
  profile.genderSignal    = _inferGender(platforms);
  profile.ageEstimate     = _inferAge(platforms, breaches);
  profile.locationSignals = _inferLocation(platforms);
  profile.urbanRural      = _inferUrbanRural(platforms);
  profile.lifestyle       = _inferLifestyle(platforms);
  profile.incomeSignal    = _inferIncomeSignal(platforms);
  profile.securityPosture = _inferSecurityPosture(platforms, breaches);

  const ms = platforms?.["microsoft"];
  if (ms?.backupEmail)                                       profile.riskSignals.push(`Microsoft backup-e-post: ${ms.backupEmail}`);
  if (ms?.twoFA === false && _found(platforms, "microsoft")) profile.riskSignals.push("Microsoft-konto saknar 2FA");
  if (Array.isArray(ms?.phones) && ms.phones.length)        profile.riskSignals.push(`Telefon på Microsoft: ${ms.phones[0]}`);

  if (profile.breachCount > 0)    profile.riskSignals.push(`Hittad i ${profile.breachCount} dataintrång`);
  if (summary?.darknetCount  > 0) profile.riskSignals.push(`Förekommer i ${summary.darknetCount} darknet-dataset`);
  if (summary?.credLogsCount > 0) profile.riskSignals.push(`Förekommer i ${summary.credLogsCount} credential logs`);

  const adultFound = Object.keys(platforms || {})
    .filter(k => _found(platforms, k) && PLATFORM_META[k]?.category === "Adult");
  if (adultFound.length)              profile.riskSignals.push(`Vuxenplattformar: ${adultFound.join(", ")}`);
  if (profile.geography.includes("RU")) profile.riskSignals.push("Ryskt plattformsnärvaro (mail.ru / Rambler)");
  if (_found(platforms, "Jägarförbundet") || _found(platforms, "Jägarförbundet/SSN"))
    profile.riskSignals.push("Registrerad jägare — trolig vapeninnehavare [KÄNSLIG UPPGIFT — behandla med diskretion]");

  profile.narrative = _buildNarrative(profile);

  return profile;
}

module.exports = { buildProfile };
