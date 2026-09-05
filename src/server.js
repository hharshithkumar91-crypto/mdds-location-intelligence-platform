/**
 * High-Performance Zero-Dependency Node.js API Gateway (Sections 6, 10, 11)
 * Built with native Node.js HTTP & Crypto modules:
 * - Zero npm install required (runs instantly in any environment)
 * - Sub-10ms response latency
 * - Full Section 6.3 & 6.5 response envelopes and autocomplete schemas
 * - Standard Section 6.6 error codes (400, 401, 403, 404, 429)
 * - Section 10.3 security headers & Section 10.4 rate limiting
 */

const http = require('http');
const url = require('url');
const crypto = require('crypto');

const PORT = process.env.PORT || 3000;
const DEMO_KEY = 'demo_public_key_for_presentations';
const PROD_KEY = 'ak_a1b2c3d4e5f67890abcdef12345678';

// Canonical MDDS In-Memory Dataset
const MDDS_DATA = [
  {
    stateId: 'st_27', stateCode: '27', stateName: 'Maharashtra',
    districtId: 'dt_497', districtCode: '497', districtName: 'Nandurbar',
    subDistrictId: 'sdt_03950', subDistrictCode: '03950', subDistrictName: 'Akkalkuwa',
    villageId: 'vil_525002', villageCode: '525002', villageName: 'Manibeli'
  },
  {
    stateId: 'st_27', stateCode: '27', stateName: 'Maharashtra',
    districtId: 'dt_497', districtCode: '497', districtName: 'Nandurbar',
    subDistrictId: 'sdt_03950', subDistrictCode: '03950', subDistrictName: 'Akkalkuwa',
    villageId: 'vil_525003', villageCode: '525003', villageName: 'Dhankhedi'
  },
  {
    stateId: 'st_27', stateCode: '27', stateName: 'Maharashtra',
    districtId: 'dt_497', districtCode: '497', districtName: 'Nandurbar',
    subDistrictId: 'sdt_03950', subDistrictCode: '03950', subDistrictName: 'Akkalkuwa',
    villageId: 'vil_525004', villageCode: '525004', villageName: 'Chimalkhadi'
  },
  {
    stateId: 'st_27', stateCode: '27', stateName: 'Maharashtra',
    districtId: 'dt_497', districtCode: '497', districtName: 'Nandurbar',
    subDistrictId: 'sdt_03950', subDistrictCode: '03950', subDistrictName: 'Akkalkuwa',
    villageId: 'vil_525005', villageCode: '525005', villageName: 'Sinduri'
  },
  {
    stateId: 'st_27', stateCode: '27', stateName: 'Maharashtra',
    districtId: 'dt_497', districtCode: '497', districtName: 'Nandurbar',
    subDistrictId: 'sdt_03950', subDistrictCode: '03950', subDistrictName: 'Akkalkuwa',
    villageId: 'vil_525006', villageCode: '525006', villageName: 'Rojkund'
  },
  {
    stateId: 'st_24', stateCode: '24', stateName: 'Gujarat',
    districtId: 'dt_446', districtCode: '446', districtName: 'Surat',
    subDistrictId: 'sdt_03912', subDistrictCode: '03912', subDistrictName: 'Chorasi',
    villageId: 'vil_515001', villageCode: '515001', villageName: 'Magdalla'
  },
  {
    stateId: 'st_24', stateCode: '24', stateName: 'Gujarat',
    districtId: 'dt_446', districtCode: '446', districtName: 'Surat',
    subDistrictId: 'sdt_03912', subDistrictCode: '03912', subDistrictName: 'Chorasi',
    villageId: 'vil_515002', villageCode: '515002', villageName: 'Dumas'
  }
];

// In-Memory Usage Store for Rate Limiting
const rateLimitStore = new Map();

function sendResponse(req, res, statusCode, body, startTime) {
  const diff = process.hrtime(startTime);
  const responseTimeMs = Math.max(1, Math.round((diff[0] * 1e3) + (diff[1] / 1e6)));

  // Security Headers (Section 10.3)
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  res.setHeader('Content-Security-Policy', "default-src 'self'");

  // CORS Headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-API-Key, X-API-Secret');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');

  res.statusCode = statusCode;

  if (body && body.meta) {
    body.meta.responseTime = responseTimeMs;
  }

  res.end(JSON.stringify(body, null, 2));
}

function sendError(req, res, statusCode, code, message, startTime) {
  const reqId = req.requestId || ('req_' + crypto.randomBytes(6).toString('hex'));
  sendResponse(req, res, statusCode, {
    success: false,
    error: { code, message },
    meta: { requestId: reqId, responseTime: 0 }
  }, startTime);
}

const server = http.createServer((req, res) => {
  const startTime = process.hrtime();
  req.requestId = 'req_' + crypto.randomBytes(6).toString('hex');
  res.setHeader('X-Request-Id', req.requestId);

  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname.replace(/\/+$/, '') || '/';
  const query = parsedUrl.query;

  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-API-Key, X-API-Secret');
    res.statusCode = 204;
    return res.end();
  }

  // Public Health & Root routes
  if (pathname === '/' || pathname === '/v1/health') {
    return sendResponse(req, res, 200, {
      success: true,
      service: 'MDDS Location Intelligence API',
      status: 'HEALTHY',
      version: '1.0.0',
      meta: { requestId: req.requestId, responseTime: 0 }
    }, startTime);
  }

  // 1. Authentication Layer (Section 6.2 & 10.1)
  const apiKey = req.headers['x-api-key'] || query.apiKey;
  if (!apiKey) {
    return sendError(req, res, 401, 'INVALID_API_KEY', 'API key missing in X-API-Key header or query parameter.', startTime);
  }

  const isDemo = (apiKey === DEMO_KEY);
  const isProd = (apiKey === PROD_KEY) || /^ak_[a-f0-9]{32}$/i.test(apiKey);

  if (!isDemo && !isProd) {
    return sendError(req, res, 401, 'INVALID_API_KEY', 'API key format is invalid. Expected format: ak_[32 hex characters].', startTime);
  }

  // 2. Rate Limiting Layer (Section 10.4)
  const dailyLimit = isDemo ? 100 : 5000;
  const todayKey = `${apiKey}:${new Date().toISOString().slice(0, 10)}`;
  let usage = rateLimitStore.get(todayKey) || { count: 0 };
  usage.count++;
  rateLimitStore.set(todayKey, usage);

  const remaining = Math.max(0, dailyLimit - usage.count);
  const resetEpoch = Math.floor((new Date().setUTCHours(24, 0, 0, 0)) / 1000);

  res.setHeader('X-RateLimit-Limit', dailyLimit);
  res.setHeader('X-RateLimit-Remaining', remaining);
  res.setHeader('X-RateLimit-Reset', resetEpoch);

  const rateLimitMeta = {
    remaining: remaining,
    limit: dailyLimit,
    reset: new Date(resetEpoch * 1000).toISOString()
  };

  if (usage.count > dailyLimit) {
    return sendError(req, res, 429, 'RATE_LIMITED', 'Daily quota exceeded.', startTime);
  }

  // State authorization scoping
  const allowedStates = isDemo ? ['Maharashtra'] : ['ALL'];
  function isStateAuth(stateName) {
    if (allowedStates.includes('ALL')) return true;
    return allowedStates.some(s => s.toLowerCase() === (stateName || '').toLowerCase());
  }

  // -------------------------------------------------------------
  // API Endpoints Routing (Section 6.4)
  // -------------------------------------------------------------

  // GET /v1/states
  if (pathname === '/v1/states') {
    const states = [];
    const seen = new Set();
    for (const r of MDDS_DATA) {
      if (!seen.has(r.stateId) && isStateAuth(r.stateName)) {
        seen.add(r.stateId);
        states.push({ id: r.stateId, code: r.stateCode, name: r.stateName, country: 'India' });
      }
    }
    return sendResponse(req, res, 200, {
      success: true, count: states.length, data: states,
      meta: { requestId: req.requestId, responseTime: 0, rateLimit: rateLimitMeta }
    }, startTime);
  }

  // GET /v1/states/:id/districts
  const matchStateDistricts = pathname.match(/^\/v1\/states\/([^/]+)\/districts$/);
  if (matchStateDistricts) {
    const stateId = matchStateDistricts[1];
    const rows = MDDS_DATA.filter(r => r.stateId === stateId || r.stateCode === stateId || r.stateName.toLowerCase() === stateId.toLowerCase());
    if (rows.length === 0) {
      return sendError(req, res, 404, 'NOT_FOUND', `State with ID or code '${stateId}' does not exist.`, startTime);
    }
    if (!isStateAuth(rows[0].stateName)) {
      return sendError(req, res, 403, 'ACCESS_DENIED', `User not authorized for requested state: ${rows[0].stateName}.`, startTime);
    }
    const districts = [];
    const seen = new Set();
    for (const r of rows) {
      if (!seen.has(r.districtId)) {
        seen.add(r.districtId);
        districts.push({ id: r.districtId, code: r.districtCode, name: r.districtName, stateId: r.stateId, stateName: r.stateName });
      }
    }
    return sendResponse(req, res, 200, {
      success: true, count: districts.length, data: districts,
      meta: { requestId: req.requestId, responseTime: 0, rateLimit: rateLimitMeta }
    }, startTime);
  }

  // GET /v1/districts/:id/subdistricts
  const matchDistSubdistricts = pathname.match(/^\/v1\/districts\/([^/]+)\/subdistricts$/);
  if (matchDistSubdistricts) {
    const districtId = matchDistSubdistricts[1];
    const rows = MDDS_DATA.filter(r => r.districtId === districtId || r.districtCode === districtId || r.districtName.toLowerCase() === districtId.toLowerCase());
    if (rows.length === 0) {
      return sendError(req, res, 404, 'NOT_FOUND', `District with identifier '${districtId}' does not exist.`, startTime);
    }
    if (!isStateAuth(rows[0].stateName)) {
      return sendError(req, res, 403, 'ACCESS_DENIED', `User not authorized for requested state: ${rows[0].stateName}.`, startTime);
    }
    const subdistricts = [];
    const seen = new Set();
    for (const r of rows) {
      if (!seen.has(r.subDistrictId)) {
        seen.add(r.subDistrictId);
        subdistricts.push({ id: r.subDistrictId, code: r.subDistrictCode, name: r.subDistrictName, districtId: r.districtId, districtName: r.districtName });
      }
    }
    return sendResponse(req, res, 200, {
      success: true, count: subdistricts.length, data: subdistricts,
      meta: { requestId: req.requestId, responseTime: 0, rateLimit: rateLimitMeta }
    }, startTime);
  }

  // GET /v1/subdistricts/:id/villages
  const matchSubdistVillages = pathname.match(/^\/v1\/subdistricts\/([^/]+)\/villages$/);
  if (matchSubdistVillages) {
    const sdtId = matchSubdistVillages[1];
    const rows = MDDS_DATA.filter(r => r.subDistrictId === sdtId || r.subDistrictCode === sdtId || r.subDistrictName.toLowerCase() === sdtId.toLowerCase());
    if (rows.length === 0) {
      return sendError(req, res, 404, 'NOT_FOUND', `Sub-district with identifier '${sdtId}' does not exist.`, startTime);
    }
    if (!isStateAuth(rows[0].stateName)) {
      return sendError(req, res, 403, 'ACCESS_DENIED', `User not authorized for requested state: ${rows[0].stateName}.`, startTime);
    }
    const page = Math.max(1, parseInt(query.page) || 1);
    const limit = Math.min(500, Math.max(1, parseInt(query.limit) || 25));
    const start = (page - 1) * limit;
    const paginated = rows.slice(start, start + limit).map(v => ({
      id: v.villageId, code: v.villageCode, name: v.villageName, subDistrictId: v.subDistrictId, subDistrictName: v.subDistrictName
    }));
    return sendResponse(req, res, 200, {
      success: true, count: paginated.length, data: paginated,
      meta: { requestId: req.requestId, responseTime: 0, rateLimit: rateLimitMeta }
    }, startTime);
  }

  // GET /v1/search
  if (pathname === '/v1/search') {
    const q = query.q ? String(query.q).trim() : '';
    if (q.length < 2) {
      return sendError(req, res, 400, 'INVALID_QUERY', 'Search query too short or invalid. Minimum 2 characters required.', startTime);
    }
    const qLower = q.toLowerCase();
    const limit = Math.min(100, Math.max(1, parseInt(query.limit) || 25));

    const matches = MDDS_DATA.filter(r => {
      if (!isStateAuth(r.stateName)) return false;
      if (query.state && r.stateName.toLowerCase() !== query.state.toLowerCase()) return false;
      return r.villageName.toLowerCase().includes(qLower) || r.villageCode.includes(q);
    }).slice(0, limit).map(v => ({
      id: v.villageId, code: v.villageCode, name: v.villageName,
      subDistrict: v.subDistrictName, district: v.districtName, state: v.stateName, country: 'India',
      fullAddress: `${v.villageName}, ${v.subDistrictName}, ${v.districtName}, ${v.stateName}, India`
    }));

    return sendResponse(req, res, 200, {
      success: true, count: matches.length, data: matches,
      meta: { requestId: req.requestId, responseTime: 0, rateLimit: rateLimitMeta }
    }, startTime);
  }

  // GET /v1/autocomplete (Section 6.5 Dropdown Format)
  if (pathname === '/v1/autocomplete') {
    const q = query.q ? String(query.q).trim() : '';
    if (q.length < 2) {
      return sendError(req, res, 400, 'INVALID_QUERY', 'Search query too short or invalid. Minimum 2 characters required.', startTime);
    }
    const qLower = q.toLowerCase();
    const matches = MDDS_DATA.filter(r => {
      if (!isStateAuth(r.stateName)) return false;
      return r.villageName.toLowerCase().includes(qLower) || r.subDistrictName.toLowerCase().includes(qLower) || r.villageCode.startsWith(q);
    }).slice(0, 15);

    // Exact Section 6.5 Schema
    const options = matches.map(r => ({
      value: r.villageId,
      label: r.villageName,
      fullAddress: `${r.villageName}, ${r.subDistrictName}, ${r.districtName}, ${r.stateName}, India`,
      hierarchy: {
        village: r.villageName,
        subDistrict: r.subDistrictName,
        district: r.districtName,
        state: r.stateName,
        country: 'India'
      }
    }));

    return sendResponse(req, res, 200, {
      success: true, count: options.length, data: options,
      meta: { requestId: req.requestId, responseTime: 0, rateLimit: rateLimitMeta }
    }, startTime);
  }

  // 404 Fallback
  return sendError(req, res, 404, 'NOT_FOUND', `Endpoint '${req.method} ${pathname}' does not exist.`, startTime);
});

if (!process.env.VERCEL) {
  server.listen(PORT, () => {
    console.log(`[INFO] MDDS API Gateway online at http://localhost:${PORT}/v1/`);
  });
}

module.exports = server;
