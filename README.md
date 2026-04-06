# Leadway Assurance — Householder Insurance Pricing Engine

A production-ready premium quoting engine for Leadway Assurance's Householder Policy.

## Architecture

```
pricing-engine/
├── api/
│   └── main.py              # FastAPI app — /api/quote, /api/rates, serves frontend
├── engine/
│   ├── __init__.py
│   ├── models.py            # RiskProfile (input), PremiumBreakdown (output)
│   ├── rates.py             # Official rate tables, loadings, discounts
│   └── calculator.py        # 13-step calculation flow
├── frontend/
│   ├── index.html           # Full SPA — Landing, Quote Builder, Results
│   └── leadway-logo.jpeg    # (Place your logo file here)
├── requirements.txt
├── render.yaml              # Render deployment config
└── README.md
```

## Local Setup

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
# Open: http://localhost:8000
```

## Logo Setup

Place your `leadway-logo.jpeg` file in the `frontend/` directory before deploying.  
The app gracefully falls back to text if the logo is missing.

## Deploy to Render

1. Push this repo to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Connect your repo — Render will detect `render.yaml` automatically
4. Click **Deploy**

The `render.yaml` configures:
- Python 3.11.9 runtime
- Build: `pip install -r requirements.txt`
- Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- Root directory: `pricing-engine/`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/quote` | Generate premium quote |
| `GET`  | `/api/rates` | Fetch full rate card |
| `GET`  | `/docs`      | Swagger UI |
| `GET`  | `/redoc`     | ReDoc reference |
| `GET`  | `/`          | Serves frontend SPA |

### Sample Quote Request

```json
POST /api/quote
{
  "segment": "Individual",
  "location": "Lagos",
  "building_age": 8,
  "building_si": 25000000,
  "content_si": 10000000,
  "cover_type": "Gold",
  "duration_months": 12,
  "claims_last_3_years": 1,
  "has_security_system": true,
  "has_fire_extinguisher": true
}
```

## Calculation Flow (13 Steps)

1. Base rate × sum insured per section → section premiums
2. Sum section premiums → Base Premium
3. Apply location factor (Lagos +15%, PH +10%, Abuja +5%, Ibadan -5%, Kaduna -10%)
4. Apply building age loading (0-5yr: 0%, 6-15yr: +5%, 16-30yr: +10%, 30+yr: +20%)
5. Apply claims history loading (0: 0%, 1: +10%, 2: +25%, 3: +50%, 4+: +75%)
6. Subtract security system discount (-5%)
7. Subtract fire extinguisher discount (-3%)
8. Apply volume discount (Individual: 50M+ -3%, 100M+ -5% / Corporate: 100M+ -4%, 500M+ -7%, 1B+ -10%)
9. Apply duration (pro-rata × 1.15 short period loading for <12 months)
10. Apply minimum premium floor (Individual ₦5,000 / Corporate ₦25,000)
11. Calculate commission at 15%
12. Net Premium = Gross − Commission

## Cover Types & Rate Bands

| Tier | Individual | Corporate Band | Inclusions |
|------|-----------|----------------|------------|
| Basic | Fixed rates | Band 1 | Building only |
| Bronze | Fixed rates | Band 1 | Building + Contents |
| Silver | Fixed rates | Band 2 | + Accidental Damage |
| Standard | Fixed rates | Band 2 | Full Building + Contents (POPULAR) |
| Gold | Fixed rates | Band 3 | + All Risks + Personal Accident |
| Platinum | Fixed rates | Band 4 | All coverages + Alt. Accommodation |

## Frontend Pages

**Page 1 — Landing**
- Hero section with CTA
- Product card with coverage tags
- Policy documents (modal + download)
- Stats bar, Why Leadway section
- Rate Card modal overlay

**Page 2 — Quote Builder** (split layout)
- Left: Dark info panel with features & next steps
- Right: Form with segment toggle, 3 steps, live coverage card highlights

**Page 3 — Results** (split layout)
- Left: Dark panel with gross premium + section mini-cards
- Right: Full breakdown — sections, adjustments table, net premium card

## Rate Tables

### Individual Rates
| Coverage | Rate | Applied To |
|----------|------|------------|
| Building | 0.10% | Building SI |
| Contents | 0.20% | Contents SI |
| Accidental Damage | 0.125% | Contents SI |
| All Risks | 2.0% | 10% of Contents SI |
| Personal Accident | 0.185% | Total SI |
| Alt. Accommodation | 0.20% | Building SI |

### Corporate Bands
| Band | Cover Type | Building | Contents |
|------|-----------|----------|----------|
| 1 | Basic/Bronze | 0.125% | 0.300% |
| 2 | Silver/Standard | 0.150% | 0.350% |
| 3 | Gold | 0.175% | 0.450% |
| 4 | Platinum | 0.185% | 0.500% |
