# SvenkOsint

Egenhostad OSINT-verktyg. Mata in en e-postadress och få tillbaka en PDF med intrångsdata, kontokontroller mot 40+ tjänster och en automatiskt genererad beteendeprofil med yrkesroll, åldersuppskattning, livsstils- och inkomstsignaler.

Node.js-server för UI och PDF-generering. Python-processer för plattformskontrollerna, körda parallellt.

---

Äldre video från några dagar sen (pdf har ändrats drastiskt)


https://github.com/user-attachments/assets/8b23aace-c876-48f7-ad1f-e36c046cacd4


---
## Stack

- Node.js + Express - server, PDF-generering (PDFKit)
- Python - alla plattformskontroller, körs parallellt via `ThreadPoolExecutor`
- IntelX + Breach.vip - sökning i läckta databaser

---

## Installation

**Krav:** Node.js 18+, Python 3.10+

```bash
npm install
pip install -r requirements.txt
```

Valfritt - skapa en `.env` i projektmappen för att ändra porten:

```env
PORT=33
```

```bash
npm start
# → http://localhost:33
```

---

## Vad som kontrolleras

### Sverige
| Kategori | |
|---|---|
| Media | Aftonbladet, Expressen, DN, DI, TV4, Samnytt, Omni |
| Marknadsplatser | Blocket, Hemnet, Bytbil |
| Handel | Willys, Systembolaget, Elgiganten, Inet, Komplett |
| Politik | Liberalerna, Miljöpartiet, Vänsterpartiet |
| Community | Byggahus, Lovable |

### Internationellt
| | |
|---|---|
| USA | Adobe, Archive.org, Bible.com, Bodybuilding, DevRant, Flickr, Insightly, LastPass, Medal, Microsoft, Office365, TeamTreehouse, Vimeo, Vivino |
| Ryssland | Mail.ru, Rambler |
| Storbritannien | Deliveroo |
| Globalt | Lovense, xVideos, Plurk, W3Schools, Freelancer |

---

## Rapportens innehåll

1. **Sammanfattning** — antal träffar, datumintervall, darknet- och lösenordsloggsträffar
2. **Profilanalys** — automatisk narrativ, yrkesroll med konfidensprocent, åldersuppskattning, platsindikationer, inkomstsignal, säkerhetsprofil, livsstil, media- och politiska signaler
3. **Riskfördelning** — per allvarlighetsgrad (Critical → Info)
4. **Källkategorier** — IntelX-träffar sorterade per källa
5. **Hotindikatorer** — lösenord, API-nycklar, kreditkort m.m.
6. **Plattformsnärvaro** — endast hittade konton visas, med detaljer (namn, login-datum, inloggningsmetod)
7. **Breach.vip-träffar** — läckta lösenord och användardata
8. **Rekommendationer** — åtgärdsförslag baserade på fynden

---

## Inmatningsfält

| Fält | Notering |
|---|---|
| E-post | Obligatoriskt |
| Namn | Förbättrar sökprecisionen |
| Telefon / Användarnamn | Visas i rapporthuvudet |
| Personnummer | Används för Willys-kontroll |

---

## Struktur

```
src/
├── server.js
├── check_email.py          startas per rapport, kör alla plattformskontroller
├── public/index.html
├── routes/
│   ├── generate.js         POST /generate
│   ├── report.js           POST /report
│   ├── search.js           POST /search
│   └── intelx.js           POST /intelx
├── lib/
│   ├── pdf.js
│   ├── profile.js
│   ├── parser.js
│   ├── intelx.js
│   └── breachvip.js
└── modules/
    ├── sweden/
    │   ├── media/
    │   ├── marketplace/
    │   ├── retail/
    │   ├── political/
    │   └── community/
    ├── us/
    ├── russia/
    ├── uk/
    └── global_/
```

---

## Ansvarsfriskrivning

Endast för auktoriserad användning. Se till att du har tillstånd innan du kör detta mot någon person.
