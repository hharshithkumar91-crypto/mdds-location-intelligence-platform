/**
 * Core Geographic Hierarchy Endpoints (Section 6.4 & 6.5)
 * Endpoints:
 * - GET /v1/search
 * - GET /v1/states
 * - GET /v1/states/:id/districts
 * - GET /v1/districts/:id/subdistricts
 * - GET /v1/subdistricts/:id/villages
 * - GET /v1/autocomplete
 */

const express = require('express');
const router = express.Router();

// Canonical MDDS In-Memory Dataset (Matches official sample & test data)
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

// Helper: Check state authorization for client
function isStateAuthorized(req, stateName) {
  if (!req.auth || !req.auth.allowedStates || req.auth.allowedStates.includes('ALL')) {
    return true;
  }
  return req.auth.allowedStates.some(s => s.toLowerCase() === (stateName || '').toLowerCase());
}

/**
 * GET /v1/states
 * List all states
 */
router.get('/states', (req, res) => {
  const uniqueStates = [];
  const seen = new Set();

  for (const item of MDDS_DATA) {
    if (!seen.has(item.stateId)) {
      seen.add(item.stateId);
      // Filter by state authorization if applicable
      if (isStateAuthorized(req, item.stateName)) {
        uniqueStates.push({
          id: item.stateId,
          code: item.stateCode,
          name: item.stateName,
          country: 'India'
        });
      }
    }
  }

  return res.sendSuccess(uniqueStates);
});

/**
 * GET /v1/states/:id/districts
 * Districts by state
 */
router.get('/states/:id/districts', (req, res) => {
  const stateId = req.params.id;
  const stateRows = MDDS_DATA.filter(r => r.stateId === stateId || r.stateCode === stateId || r.stateName.toLowerCase() === stateId.toLowerCase());

  if (stateRows.length === 0) {
    return res.sendError(404, 'NOT_FOUND', `State with ID or code '${stateId}' does not exist.`);
  }

  const targetState = stateRows[0].stateName;
  if (!isStateAuthorized(req, targetState)) {
    return res.sendError(403, 'ACCESS_DENIED', `User not authorized for requested state: ${targetState}.`);
  }

  const uniqueDistricts = [];
  const seen = new Set();
  for (const item of stateRows) {
    if (!seen.has(item.districtId)) {
      seen.add(item.districtId);
      uniqueDistricts.push({
        id: item.districtId,
        code: item.districtCode,
        name: item.districtName,
        stateId: item.stateId,
        stateName: item.stateName
      });
    }
  }

  return res.sendSuccess(uniqueDistricts);
});

/**
 * GET /v1/districts/:id/subdistricts
 * Sub-districts by district
 */
router.get('/districts/:id/subdistricts', (req, res) => {
  const districtId = req.params.id;
  const distRows = MDDS_DATA.filter(r => r.districtId === districtId || r.districtCode === districtId || r.districtName.toLowerCase() === districtId.toLowerCase());

  if (distRows.length === 0) {
    return res.sendError(404, 'NOT_FOUND', `District with identifier '${districtId}' does not exist.`);
  }

  if (!isStateAuthorized(req, distRows[0].stateName)) {
    return res.sendError(403, 'ACCESS_DENIED', `User not authorized for requested state: ${distRows[0].stateName}.`);
  }

  const uniqueSubDistricts = [];
  const seen = new Set();
  for (const item of distRows) {
    if (!seen.has(item.subDistrictId)) {
      seen.add(item.subDistrictId);
      uniqueSubDistricts.push({
        id: item.subDistrictId,
        code: item.subDistrictCode,
        name: item.subDistrictName,
        districtId: item.districtId,
        districtName: item.districtName
      });
    }
  }

  return res.sendSuccess(uniqueSubDistricts);
});

/**
 * GET /v1/subdistricts/:id/villages
 * Villages by sub-district with pagination
 */
router.get('/subdistricts/:id/villages', (req, res) => {
  const subDistrictId = req.params.id;
  const page = Math.max(1, parseInt(req.query.page) || 1);
  const limit = Math.min(500, Math.max(1, parseInt(req.query.limit) || 25));

  const sdtRows = MDDS_DATA.filter(r => r.subDistrictId === subDistrictId || r.subDistrictCode === subDistrictId || r.subDistrictName.toLowerCase() === subDistrictId.toLowerCase());

  if (sdtRows.length === 0) {
    return res.sendError(404, 'NOT_FOUND', `Sub-district with identifier '${subDistrictId}' does not exist.`);
  }

  if (!isStateAuthorized(req, sdtRows[0].stateName)) {
    return res.sendError(403, 'ACCESS_DENIED', `User not authorized for requested state: ${sdtRows[0].stateName}.`);
  }

  const startIndex = (page - 1) * limit;
  const paginated = sdtRows.slice(startIndex, startIndex + limit).map(v => ({
    id: v.villageId,
    code: v.villageCode,
    name: v.villageName,
    subDistrictId: v.subDistrictId,
    subDistrictName: v.subDistrictName
  }));

  return res.sendSuccess(paginated, sdtRows.length);
});

/**
 * GET /v1/search
 * Search villages by text and hierarchy filters
 */
router.get('/search', (req, res) => {
  const { q, state, district, subDistrict, limit } = req.query;

  if (!q || q.trim().length < 2) {
    return res.sendError(400, 'INVALID_QUERY', 'Search query too short or invalid. Minimum 2 characters required.');
  }

  const query = q.trim().toLowerCase();
  const maxLimit = Math.min(100, Math.max(1, parseInt(limit) || 25));

  const results = MDDS_DATA.filter(item => {
    // Check state authorization
    if (!isStateAuthorized(req, item.stateName)) return false;

    // Filters
    if (state && item.stateName.toLowerCase() !== state.toLowerCase() && item.stateCode !== state) return false;
    if (district && item.districtName.toLowerCase() !== district.toLowerCase() && item.districtCode !== district) return false;
    if (subDistrict && item.subDistrictName.toLowerCase() !== subDistrict.toLowerCase() && item.subDistrictCode !== subDistrict) return false;

    // Search partial match on village name or code
    return item.villageName.toLowerCase().includes(query) || item.villageCode.includes(query);
  }).slice(0, maxLimit).map(v => ({
    id: v.villageId,
    code: v.villageCode,
    name: v.villageName,
    subDistrict: v.subDistrictName,
    district: v.districtName,
    state: v.stateName,
    country: 'India',
    fullAddress: `${v.villageName}, ${v.subDistrictName}, ${v.districtName}, ${v.stateName}, India`
  }));

  return res.sendSuccess(results);
});

/**
 * GET /v1/autocomplete
 * Typeahead suggestions formatted specifically for drop-down menus (Section 6.5)
 */
router.get('/autocomplete', (req, res) => {
  const { q, hierarchyLevel } = req.query;

  if (!q || q.trim().length < 2) {
    return res.sendError(400, 'INVALID_QUERY', 'Search query too short or invalid. Minimum 2 characters required.');
  }

  const query = q.trim().toLowerCase();

  const matches = MDDS_DATA.filter(item => {
    if (!isStateAuthorized(req, item.stateName)) return false;
    return item.villageName.toLowerCase().includes(query) || 
           item.subDistrictName.toLowerCase().includes(query) || 
           item.villageCode.startsWith(query);
  }).slice(0, 15);

  // Format exactly as required by Section 6.5 for UI dropdowns
  const dropdownOptions = matches.map(item => ({
    value: item.villageId,
    label: item.villageName,
    fullAddress: `${item.villageName}, ${item.subDistrictName}, ${item.districtName}, ${item.stateName}, India`,
    hierarchy: {
      village: item.villageName,
      subDistrict: item.subDistrictName,
      district: item.districtName,
      state: item.stateName,
      country: 'India'
    }
  }));

  return res.sendSuccess(dropdownOptions);
});

module.exports = router;
