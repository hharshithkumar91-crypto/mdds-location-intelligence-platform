# Phase 2 Demo Video Recording Kit
## Professional 90-Second Walkthrough Guide & Spoken Script

This recording guide shows you how to demonstrate the live **API Gateway**, **Demo Client Auto-Fill**, and the **100% Automated Test Suite**.

---

### 1. Pre-Recording Preparation
Have these 3 windows open on your desktop:
1. **Window 1 (Browser Tab 1):** Open `demo-client/index.html` in Chrome or Edge.
2. **Window 2 (Browser Tab 2):** Your GitHub Repository:
   `https://github.com/hharshithkumar91-crypto/mdds-location-intelligence-platform`
3. **Window 3 (Terminal / PowerShell):** At `c:\Users\Devil\OneDrive\Desktop\capstone` with this command ready:
   ```powershell
   python scripts/test_phase2_apis.py
   ```

---

### 2. Spoken Script with Timestamps (Word-for-Word)

```
[0:00 - 0:15] INTRO & REPOSITORY OVERVIEW
(Display GitHub Repository on screen)

"Hello evaluators. This is Harshith Kumar presenting the Phase 2 deliverables for our 
Bold Analytics Capstone: the MDDS Administrative Hierarchy Platform, built with my 
teammates Riyan Pathan and Geetha.

In Phase 2, we have implemented the full REST API Gateway, multi-tenant rate limiting, 
standardized response envelopes, and our reference B2B Demo Client application."
```

```
[0:15 - 0:45] LIVE DEMO CLIENT: REAL-TIME AUTOCOMPLETE & AUTO-FILL
(Switch to Window 1: demo-client/index.html)

"Here is our B2B Reference Client application, representing Section 13 of the specification. 
It integrates directly with our /v1/autocomplete API using our public presentation demo key.

Watch as I type 'Mani' in the Village field:
[Type 'Mani']

The typeahead endpoint instantly queries the API and returns standardized dropdown options. 
When I select 'Manibeli':
[Click 'Manibeli']

Notice that all administrative hierarchy fields auto-populate in real time:
- Sub-District auto-fills to 'Akkalkuwa'
- District auto-fills to 'Nandurbar'
- State auto-fills to 'Maharashtra'
- Country auto-fills to 'India'

This eliminates manual address errors for enterprise B2B customers."
```

```
[0:45 - 1:15] LIVE AUTOMATED API TEST SUITE
(Switch to Window 3: Terminal and press Enter on python scripts/test_phase2_apis.py)

"Now, let's run our Phase 2 automated test suite live to verify full specification compliance.

[Hit Enter]

As you can see:
1. The API Gateway initializes on port 3001 with sub-millisecond response times.
2. The standard response envelope is validated—delivering requestId, responseTime, and rateLimit quota.
3. Our 5-tier drill-down successfully resolves State, District, SubDistrict, and Village.
4. The Section 6.5 autocomplete schema is verified.
5. And all Section 6.6 HTTP error codes—400 INVALID_QUERY, 401 INVALID_API_KEY, 403 ACCESS_DENIED, 
   and 404 NOT_FOUND—are rigorously tested and passed with 100% success."
```

```
[1:15 - 1:30] CONCLUSION & MILESTONE ACCEPTANCE
(Switch to Phase 2 PowerPoint or Whitepaper)

"Our API Gateway enforces rate limiting across Free, Premium, Pro, and Unlimited tiers, and 
all responses include hardened HTTP security headers. 

Phase 2 is fully implemented, tested, and ready for production deployment on Vercel. 
Thank you for your evaluation."
```
