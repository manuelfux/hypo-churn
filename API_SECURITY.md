# API Security Configuration

## Overview
This document describes the security measures implemented for the Hypo-Churn Prediction API, including both application-level and Cloudflare Tunnel-specific configurations.

## Application-Level Security (Implemented ✅)

### 1. Rate Limiting
**Status:** ✅ Implemented with `slowapi`

Rate limits per endpoint (per IP address):
- `GET /` - 30 requests/minute
- `GET /health` - 60 requests/minute
- `GET /model/info` - 30 requests/minute
- `POST /predict` - 10 requests/minute
- `POST /predict/batch` - 5 requests/minute (max 100 customers per request)
- `GET /predict/probability` - 15 requests/minute

**Why:** Prevents DoS attacks and resource exhaustion from single IPs.

### 2. Input Validation
**Status:** ✅ Enhanced with Pydantic validators

- Strict type checking with Pydantic models
- Range validation for all numeric fields
- Whitelist validation for categorical fields (Geography, Gender)
- Maximum value limits for financial fields
- Batch size reduced from 1000 to 100 customers

**Why:** Prevents injection attacks and invalid data processing.

### 3. Error Message Sanitization
**Status:** ✅ Implemented

- Generic error messages returned to clients
- Technical details only logged server-side
- No stack traces exposed to external users
- Specific error types (ValueError, general Exception) handled separately

**Why:** Prevents information disclosure about system internals.

### 4. Security Headers
**Status:** ✅ Implemented via middleware

All responses include:
- `X-Content-Type-Options: nosniff` - Prevents MIME-type sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-XSS-Protection: 1; mode=block` - Enables browser XSS filter
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` - Forces HTTPS
- `Content-Security-Policy: default-src 'self'` - Restricts resource loading

**Why:** Defense-in-depth against common web attacks.

### 5. CORS Configuration
**Status:** ✅ Configured (needs production adjustment)

Current settings:
```python
allow_origins=["*"]  # TODO: Replace with specific origins
allow_methods=["GET", "POST"]
allow_headers=["*"]
```

**Action Required:** Update `allow_origins` to whitelist specific domains before production deployment.

**Why:** Prevents unauthorized cross-origin requests.

### 6. Request Logging
**Status:** ✅ Implemented

All requests logged with:
- Timestamp
- Client IP address
- Request method and path
- Response status code
- Error types (for failed requests)

**Why:** Audit trail for security monitoring and incident response.

---

## Cloudflare-Specific Security (Recommended Configuration)

### 1. Cloudflare Tunnel Benefits (Already Active ✓)
- ✅ DDoS protection
- ✅ TLS/HTTPS termination
- ✅ Origin server IP masking
- ✅ Automatic certificate management

### 2. Additional Cloudflare Features (Recommended)

#### A. WAF (Web Application Firewall)
**Location:** Cloudflare Dashboard → Security → WAF

Recommended rules:
- Enable OWASP Core Ruleset
- Block known malicious IPs
- Challenge suspicious user agents
- Rate limiting at Cloudflare edge (in addition to app-level)

#### B. Bot Management
**Location:** Cloudflare Dashboard → Security → Bots

Options:
- Block definitively automated traffic
- Challenge likely automated traffic
- Allow verified bots (optional for public API)

#### C. IP Access Rules
**Location:** Cloudflare Dashboard → Security → WAF → Tools

Options:
- Whitelist trusted IP ranges (if applicable)
- Block known malicious ASNs
- Challenge traffic from high-risk countries (optional)

#### D. Rate Limiting (Edge-Level)
**Location:** Cloudflare Dashboard → Security → WAF → Rate limiting rules

Recommended edge limits (stricter than app-level):
- 100 requests per minute per IP (global)
- 500 requests per hour per IP
- Custom rules for prediction endpoints

**Why:** Stops attacks before they reach your server.

#### E. Cache Configuration
**Location:** Cloudflare Dashboard → Caching → Configuration

For this API:
- ❌ Do NOT cache `/predict*` endpoints (dynamic data)
- ✅ Cache `/health` and `/model/info` (static responses)
- ✅ Cache static assets if added later

#### F. SSL/TLS Settings
**Location:** Cloudflare Dashboard → SSL/TLS

Recommended:
- SSL/TLS encryption mode: **Full (strict)**
- Minimum TLS version: **TLS 1.2**
- Enable **HSTS** (already set in app headers)
- Enable **Authenticated Origin Pulls** (optional)

#### G. Firewall Rules
**Location:** Cloudflare Dashboard → Security → WAF

Example rules:
```
# Block requests without valid User-Agent
(not http.user_agent contains "Mozilla") and (not http.user_agent contains "curl")

# Challenge requests from specific countries (optional)
(ip.geoip.country in {"CN" "RU"})

# Rate limit by URL pattern
(http.request.uri.path matches "/predict")
```

#### H. Access Policies (Optional)
**Location:** Cloudflare Dashboard → Zero Trust → Access

If you want authentication without changing code:
- Create an Access Application for your API
- Require email authentication or service tokens
- Configure allowed users/groups

**Why:** Adds authentication layer without code changes.

---

## Deployment Checklist

Before going live:

### Application
- [ ] Update CORS `allow_origins` to specific domains
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Test all endpoints with rate limiting
- [ ] Verify error messages don't leak sensitive info
- [ ] Enable production logging (consider log aggregation service)

### Cloudflare
- [ ] Enable WAF with OWASP Core Ruleset
- [ ] Configure Bot Management
- [ ] Set up edge rate limiting rules
- [ ] Configure SSL/TLS to "Full (strict)"
- [ ] Set minimum TLS version to 1.2
- [ ] Review and test firewall rules
- [ ] Consider Cloudflare Access for authentication (optional)
- [ ] Set up alerts for traffic anomalies

### Monitoring
- [ ] Set up uptime monitoring
- [ ] Configure alerts for rate limit violations
- [ ] Monitor error rates
- [ ] Track API usage patterns
- [ ] Review logs regularly for suspicious activity

---

## Testing

### Test Rate Limiting
```bash
# Test single endpoint rate limit
for i in {1..12}; do
  curl -X POST https://your-api.com/predict \
    -H "Content-Type: application/json" \
    -d @test_customer.json
  sleep 1
done
# Expected: 429 Too Many Requests after 10 requests
```

### Test Input Validation
```bash
# Test invalid Geography
curl -X POST https://your-api.com/predict \
  -H "Content-Type: application/json" \
  -d '{"Geography": "InvalidCountry", ...}'
# Expected: 422 Unprocessable Entity
```

### Test Security Headers
```bash
curl -I https://your-api.com/health
# Expected headers:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# etc.
```

---

## Security Maintenance

### Regular Tasks
- **Weekly:** Review API access logs for anomalies
- **Monthly:** Update dependencies (`pip list --outdated`)
- **Quarterly:** Review and update rate limits based on usage
- **Annually:** Security audit of entire system

### Incident Response
1. Monitor logs for security events
2. Use Cloudflare Analytics to identify attacks
3. Adjust WAF rules based on threat patterns
4. Document incidents and responses
5. Update security measures accordingly

---

## Additional Recommendations

### Future Enhancements
1. **Authentication** - Add API key or OAuth when needed
2. **Request Signing** - HMAC signatures for sensitive operations
3. **IP Reputation** - Integrate with threat intelligence feeds
4. **Anomaly Detection** - ML-based unusual traffic detection
5. **Encryption at Rest** - Encrypt sensitive model files
6. **Secrets Management** - Use HashiCorp Vault or similar
7. **API Gateway** - Consider Kong, AWS API Gateway, etc.

### Monitoring Tools
- **Cloudflare Analytics** - Built-in traffic analysis
- **Sentry** - Error tracking and monitoring
- **Prometheus + Grafana** - Metrics visualization
- **ELK Stack** - Log aggregation and analysis

---

## Support & Questions

For questions about:
- **Application Security:** Review code in `api/main.py`
- **Cloudflare Configuration:** Check Cloudflare Dashboard documentation
- **Rate Limits:** Adjust decorators in `api/main.py`
- **CORS Settings:** Modify middleware configuration in `api/main.py`

## Version History
- **v1.0** (2025-12-04): Initial security implementation
  - Rate limiting with slowapi
  - Input validation enhancements
  - Security headers
  - Error message sanitization
  - CORS configuration
  - Request logging
