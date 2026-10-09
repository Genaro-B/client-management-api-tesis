# Summary of Changes to Chapter 5 (Results)

## Document Modified
`Docs/Devoluciones + archivo de tesis/Tesis_Final_UTNV2 (1).docx`

## Backup Created
`Docs/Devoluciones + archivo de tesis/Tesis_Final_UTNV2 (1)_BACKUP.docx`

## Changes Made

### 1. Statistical Analysis Added (Section 5.2)
**Location**: After Table 5 (Response Times) - Paragraph 371

**Content Added**:
- Coefficient of variation (CV) analysis for each endpoint:
  - GET /api/v1/clients/{id}: CV = 143.48% (inflated by very low mean of 2.76ms)
  - GET /api/v1/products/: CV = 97.67%
  - GET /api/v1/clients/: CV = 216.48%
  - GET /api/v1/metrics/dashboard: CV = 77.30%
  - POST /api/v1/interactions/: CV = 80.71%

- 95% Confidence Intervals for mean response times:
  - Client detail: 1.36–4.16 ms
  - Product catalog: 3.06–6.38 ms
  - Client list: 1.24–9.44 ms
  - Dashboard: 9.96–17.78 ms
  - Interaction: 9.87–18.01 ms

- Analysis confirming all confidence interval upper bounds remain significantly below the 100ms perceptual threshold (Nielsen, 1993)

### 2. Distribution Analysis Added (Section 5.6)
**Location**: Paragraph 389

**Content Added**:
- Correlation between endpoint complexity and response time
- Fastest endpoint: GET /api/v1/clients/{id} (2.76ms) - simple primary key lookup O(1)
- Slowest endpoints: GET /api/v1/metrics/dashboard (13.87ms) and POST /api/v1/interactions/ (13.94ms)
- Explanation of why POST /api/v1/interactions/ is slowest: combines local DB insert with external Telegram API call
- Validation that even the slowest endpoint remains >7x below the 100ms threshold

### 3. Literature Comparison Added (Section 5.6)
**Location**: Paragraph 388

**Content Added**:
- **Response time comparison**:
  - System: 2.76-13.94 ms
  - Literature benchmarks: 50-200 ms (Richardson, 2018; Newman, 2015)
  - Reduction: 1-2 orders of magnitude
  - Attribution: No intermediate processing layers + embedded SQLite

- **Accuracy comparison**:
  - System: 100% on predefined intent catalog
  - NLP-based systems: 85-95% (Jurafsky y Martin, 2024; Devlin et al., 2019)
  - Caveat: System operates on restricted domain (7 intents with deterministic pattern matching) vs. open domains with hundreds/thousands of categories

## Document Statistics
- **Before**: 595 paragraphs, 13 tables
- **After**: 598 paragraphs, 13 tables
- **Net addition**: 3 paragraphs (~1,200 words)

## Page Count Estimate
Adding 3 paragraphs with approximately 1,200 words should increase the document by approximately 2-3 pages, keeping it well under the 100-page limit (from original 88 pages).

## Formatting
All new paragraphs use the "Normal" style consistent with existing body text in the document.
