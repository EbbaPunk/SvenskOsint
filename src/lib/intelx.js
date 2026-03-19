'use strict';

const https = require('https');

const API_KEY = 'e0eb96e8-100b-401b-b0d8-a7d1c7c45282';
const HOST    = 'public.intelx.io';

const BASE_HEADERS = {
  'accept':          '*/*',
  'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
  'content-type':    'application/json',
  'origin':          'https://intelx.io',
  'referer':         'https://intelx.io/',
  'user-agent':      'Mozilla/5.0',
  'x-key':           API_KEY,
};

function request(options, body) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, res => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(data) }); }
        catch { resolve({ status: res.statusCode, body: data }); }
      });
    });
    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

/**
 * Search IntelX for an email and return the records array.
 * @param {string} email
 * @returns {Promise<object[]>}
 */
async function intelxSearch(email) {
  // Step 1 — initiate search
  const searchRes = await request({
    hostname: HOST,
    path:     '/intelligent/search',
    method:   'POST',
    headers:  BASE_HEADERS,
  }, {
    term:        email,
    lookuplevel: 0,
    maxresults:  10000,
    timeout:     0,
    datefrom:    '',
    dateto:      '',
    sort:        2,
    media:       0,
    terminate:   [],
  });

  if (searchRes.status !== 200 || !searchRes.body.id) {
    throw new Error(`IntelX search initiation failed (${searchRes.status})`);
  }

  const searchId = searchRes.body.id;

  // Step 2 — wait briefly then fetch results (mirrors main.py)
  await sleep(2500);

  const resultRes = await request({
    hostname: HOST,
    path:     `/intelligent/search/result?id=${searchId}&limit=10000&statistics=1&previewlines=100`,
    method:   'GET',
    headers:  BASE_HEADERS,
  });

  if (resultRes.status !== 200) {
    throw new Error(`IntelX result fetch failed (${resultRes.status})`);
  }

  const records = resultRes.body.records || [];
  return records;
}

module.exports = { intelxSearch };
