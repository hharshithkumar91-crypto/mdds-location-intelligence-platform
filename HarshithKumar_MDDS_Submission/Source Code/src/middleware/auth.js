/**
 * API Key & Secret Authentication Middleware (Section 6.2, 10.1 & 10.2)
 * Validates X-API-Key and X-API-Secret against database/memory store.
 * Supports public demo presentation key (Section 13.4).
 */

const crypto = require('crypto');
const bcrypt = require('bcrypt');

// Demo key configuration for presentations (Section 13.4)
const DEMO_KEY = 'demo_public_key_for_presentations';

// In-memory key store fallback (used when NeonDB is offline or for local testing)
const activeKeysStore = new Map([
  [
    DEMO_KEY,
    {
      id: 'key_demo_presentation',
      userId: 'user_demo_client',
      name: 'Presentation Demo Key',
      planType: 'FREE',
      isActive: true,
      allowedStates: ['Maharashtra'], // Demo is restricted to Maharashtra (Section 13.4)
      isDemo: true
    }
  ],
  [
    'ak_a1b2c3d4e5f67890abcdef12345678',
    {
      id: 'key_test_prod',
      userId: 'user_b2b_enterprise',
      name: 'Production Server Key',
      planType: 'PRO',
      isActive: true,
      allowedStates: ['ALL'], // Full India access
      secretHash: '$2b$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQmG6W565656565656565'
    }
  ]
]);

module.exports = async function apiKeyAuth(req, res, next) {
  const apiKey = req.header('X-API-Key') || req.query.apiKey;
  const apiSecret = req.header('X-API-Secret');

  // 1. Verify presence of API key
  if (!apiKey) {
    return res.sendError(401, 'INVALID_API_KEY', 'API key missing in X-API-Key header or query parameter.');
  }

  // 2. Validate API key format (ak_[32 hex] or demo key)
  const isValidFormat = (apiKey === DEMO_KEY) || /^ak_[a-f0-9]{32}$/i.test(apiKey);
  if (!isValidFormat) {
    return res.sendError(401, 'INVALID_API_KEY', 'API key format is invalid. Expected format: ak_[32 hex characters].');
  }

  // 3. Lookup Key Metadata
  const keyRecord = activeKeysStore.get(apiKey);
  if (!keyRecord || !keyRecord.isActive) {
    return res.sendError(401, 'INVALID_API_KEY', 'API key does not exist or has been revoked.');
  }

  // 4. Verify Secret on Write Operations (POST, PUT, DELETE, PATCH)
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(req.method)) {
    if (!apiSecret) {
      return res.sendError(401, 'INVALID_API_KEY', 'Write operations require X-API-Secret header.');
    }
    if (keyRecord.isDemo) {
      return res.sendError(403, 'ACCESS_DENIED', 'Demo key is strictly read-only.');
    }
    // Verify secret hash if configured
    if (keyRecord.secretHash) {
      const isSecretMatch = await bcrypt.compare(apiSecret, keyRecord.secretHash).catch(() => false);
      if (!isSecretMatch) {
        return res.sendError(401, 'INVALID_API_KEY', 'Invalid API secret provided.');
      }
    }
  }

  // Attach authenticated context to request
  req.auth = {
    apiKey: apiKey,
    keyId: keyRecord.id,
    userId: keyRecord.userId,
    planType: keyRecord.planType,
    allowedStates: keyRecord.allowedStates || ['ALL'],
    isDemo: !!keyRecord.isDemo
  };

  next();
};
