/**
 * Standard Response Envelope & Execution Telemetry Middleware (Section 6.3 & 6.6)
 * Injects requestId, measures responseTime in milliseconds, and standardizes envelopes.
 */

const crypto = require('crypto');

module.exports = function responseEnvelope(req, res, next) {
  const startTime = process.hrtime();
  req.requestId = 'req_' + crypto.randomBytes(8).toString('hex');
  res.setHeader('X-Request-Id', req.requestId);

  // Helper method for standard success responses
  res.sendSuccess = function(data, count = null) {
    const diff = process.hrtime(startTime);
    const responseTimeMs = Math.round((diff[0] * 1e3) + (diff[1] / 1e6));

    const recordCount = count !== null ? count : (Array.isArray(data) ? data.length : 1);

    const envelope = {
      success: true,
      count: recordCount,
      data: data,
      meta: {
        requestId: req.requestId,
        responseTime: responseTimeMs,
        rateLimit: req.rateLimitMeta || {
          remaining: 4990,
          limit: 5000,
          reset: new Date(Date.now() + 86400000).toISOString()
        }
      }
    };

    return res.status(200).json(envelope);
  };

  // Helper method for standard error responses
  res.sendError = function(statusCode, errorCode, message, details = null) {
    const diff = process.hrtime(startTime);
    const responseTimeMs = Math.round((diff[0] * 1e3) + (diff[1] / 1e6));

    const envelope = {
      success: false,
      error: {
        code: errorCode,
        message: message
      },
      meta: {
        requestId: req.requestId,
        responseTime: responseTimeMs
      }
    };

    if (details) {
      envelope.error.details = details;
    }

    return res.status(statusCode).json(envelope);
  };

  next();
};
