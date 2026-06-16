# Part 2 – RFM Segmentation & Retention Strategy

## D2C Customer Churn Intelligence Capstone

---

## Overview

This repository builds customer segments using RFM scoring enriched with behavioural signals (support tickets, return rates, session activity, campaign engagement). Each segment gets a targeted retention action and budget priority.

---

## Repository Structure

```
churn-part2/
├── data/                        # Raw CSV datasets
├── outputs/                     # Generated charts
├── rfm_segmentation.ipynb       # Main segmentation notebook
├── build_rfm.py                 # Script version
├── generate_manual_review.py    # Generates manual_review_cases.md
├── segments.csv                 # Final segment assignments (2000 customers)
├── retention_strategy.md        # Segment-wise retention plan + budget
├── manual_review_cases.md       # 10 ambiguous customer cases with reasoning
├── requirements.txt
└── README.md
```

---

## Setup & Run

```bash
pip install -r requirements.txt

# Generate segments and charts
python build_rfm.py

# Generate manual review cases
python generate_manual_review.py

# OR open notebook
jupyter notebook rfm_segmentation.ipynb
```

---

## Segments Created

| Segment | Count | Priority |
|---------|-------|----------|
| Champions | ~531 | Retain with experience |
| At-Risk Customers | ~350 | HIGH – reactivate urgently |
| Potential Loyalists | ~314 | Grow |
| Loyal Customers | ~251 | Maintain |
| Discount-Sensitive | ~204 | Reduce discount dependency |
| Dormant Customers | ~138 | Win-back or suppress |
| New Customers | ~110 | 2nd purchase conversion |
| High Returners | ~99 | Fix product-fit |
| High-Value But Unhappy | ~3 | Immediate CS escalation |

---

## Non-RFM Signals Used

1. Unresolved ticket count
2. Return rate
3. Days since last app session
4. Campaign open/conversion rate
5. Discount usage rate
