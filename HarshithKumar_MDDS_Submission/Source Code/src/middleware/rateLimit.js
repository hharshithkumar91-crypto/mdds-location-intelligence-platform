/**
 * Rate Limiting Middleware (Section 10.4 & 11.1)
 * Enforces per-API key daily quotas and burst rates.
 * Injects standard X-RateLimit-* headers and handles HTTP 429 RATE_LIMITED.
 */

// Tier Limits Matrix (Section 10.4)
const PLAN_LIMITS = {
  FREE: { daily: 5000, burstPerMin: 100 },
  PREMIUM: { daily: 50000, burstPerMin: 500 },
  PRO: { daily: 300000, burstPerMin: 2000 },
  UNLIMITED: { daily: 1000000, burstPerMin: 5000 }
};

// In-memory sliding window store (Upstash Redis fallback)
const usageStore = new Map();

module.exports = function rateLimiter(req, res, next) {
  const apiKey = req.auth ? req.auth.apiKey : 'anonymous';
  const planType = (req.auth && req.auth.planType) || 'FREE';
  const isDemo = req.auth && req.auth.isDemo;

  const limits = isDemo 
    ? { daily: 100, burstPerMin: 30 } // Demo key limit: 100 daily (Section 13.4)
    : (PLAN_LIMITS[planType] || PLAN_LIMITS.FREE);

  const now = Date.now();
  const todayKey = `${apiKey}:${new Date().toISOString().slice(0, 10)}`;

  let record = usageStore.get(todayKey);
  if (!record) {
    record = {
      count: 0,
      burstWindowStart: now,
      burstCount: 0
    };
    usageStore.set(todayKey, record);
  }

  // 1. Check Burst Limit (per minute)
  if (now - record.burstWindowStart > 60000) {
    record.burstWindowStart = now;
    record.burstCount = 0;
  }
  record.burstCount++;

  if (record.burstCount > limits.burstPerMin) {
    res.setHeader('Retry-After', '60');
    return res.sendError(429, 'RATE_LIMITED', 'Burst rate limit exceeded. Please throttle requests to ' + limits.burstPerMin + ' req/min.');
  }

  // 2. Check Daily Quota
  record.count++;
  const remaining = Math.max(0, limits.daily - record.count);
  const resetEpoch = Math.floor((new Date().setUTCHours(24, 0, 0, 0)) / 1000);

  // Set standard headers (Section 10.4)
  res.setHeader('X-RateLimit-Limit', limits.daily);
  res.setHeader('X-RateLimit-Remaining', remaining);
  res.setHeader('X-RateLimit-Reset', resetEpoch);

  req.rateLimitMeta = {
    remaining: remaining,
    limit: limits.daily,
    reset: new Date(resetEpoch * 1000).toISOString()
  };

  if (record.count > limits.daily) {
    return res.sendError(429, 'RATE_LIMITED', 'Daily quota exceeded. Current plan: ' + planType + ' (' + limits.daily + ' req/day).');
  }

  next();
};
