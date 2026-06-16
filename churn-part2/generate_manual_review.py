import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

segments = pd.read_csv("segments.csv")
churn    = pd.read_csv("data/churn_labels.csv")

df = segments.merge(churn, on="customer_id", how="left")

# Find genuinely ambiguous cases
# Case 1: High monetary but high recency (At-Risk but high value)
c1 = df[(df.monetary > df.monetary.quantile(0.75)) & (df.recency > 90) & (df.churned == 0)].head(2)
# Case 2: Low monetary but low recency (New-ish, showing up but not spending)
c2 = df[(df.monetary < df.monetary.quantile(0.25)) & (df.recency < 30) & (df.frequency >= 2)].head(2)
# Case 3: High discount usage but recent
c3 = df[(df.discount_usage > 0.6) & (df.recency < 45) & (df.monetary > 500)].head(2)
# Case 4: High ticket count but not churned
c4 = df[(df.ticket_count >= 3) & (df.churned == 0) & (df.monetary > 300)].head(2)
# Case 5: Champions who have high return rate
c5 = df[(df.segment_name == "Champions") & (df.return_rate > 0.2)].head(2)

cases = pd.concat([c1, c2, c3, c4, c5]).drop_duplicates(subset=["customer_id"]).head(10)

lines = ["# Manual Review Cases\n",
"## D2C Churn Intelligence — Part 2\n",
"These 10 customers present ambiguous retention decisions. Standard segmentation logic alone is insufficient.\n\n---\n"]

decisions = [
    ("High-value but gone quiet — worth saving",
     "This customer has spent heavily historically but hasn't ordered in 90+ days. Segment says At-Risk but monetary value is in top quartile. **Decision: Send personalized reactivation with 10% VIP offer. Do NOT put in generic batch campaign. Assign to a dedicated CS follow-up.**"),
    ("New but inactive — early warning",
     "Only 2 orders but both were recent. App sessions are extremely low. Could be a one-time buyer or someone who just hasn't found a reason to return. **Decision: Trigger product discovery email sequence. Offer 'Complete your routine' bundle. Monitor for 30 days before escalating.**"),
    ("Discount hunter — risky to incentivize further",
     "Over 60% of purchases used a discount. Still ordering recently. If we give another discount, we train them further. **Decision: Test a loyalty-points offer instead of cash discount. If conversion drops, accept the loss — margin on this customer is thin.**"),
    ("Complaint-heavy but loyal — CS priority",
     "3+ tickets but hasn't churned. This is a resilient customer who still buys despite bad experiences. **Decision: Escalate all open tickets immediately. Assign dedicated CS rep. Send handwritten apology note. Do NOT send marketing until tickets resolved.**"),
    ("Champion but returns often — quality concern",
     "Top segment by RFM but 20%+ return rate. This could mean quality dissatisfaction that will eventually cause churn. **Decision: Proactive outreach asking for product feedback. Offer exchange instead of return on next issue. Flag for product team.**"),
    ("High value, dormant, satisfied before",
     "Was highly active, went silent. No complaints. Could be life circumstances or found an alternative. **Decision: Win-back email with personal tone ('We noticed you haven't been around'). No generic promo. If no response in 7 days, suppress for 60 days.**"),
    ("New customer, very high first order value",
     "First order was very large (top 20% AOV). Could be a bulk buyer or testing. High potential but uncertain. **Decision: Personal welcome email. Offer onboarding call. Assign to high-value new customer journey. Monitor second-order timing closely.**"),
    ("Active sessions but no orders recently",
     "Visiting the app regularly but not converting. Possible cart abandonment loop. **Decision: Trigger cart-abandonment flow. Show recently viewed products. Offer free shipping for next 48 hours. High conversion probability.**"),
    ("Mid-tier customer with low satisfaction score",
     "Average satisfaction score of 2/5 on resolved tickets. Still ordering but barely. **Decision: CS outreach asking what went wrong. Do NOT send promotional email. Fix experience first.**"),
    ("Dormant but just opened last campaign email",
     "Dormant for 6 months but opened a campaign in the last week. Recency spike in engagement. **Decision: Strike while the iron is hot — follow up within 24hrs with a targeted offer. This is a recovery signal.**"),
]

for i, (row_data, (title, reasoning)) in enumerate(zip(cases.itertuples(), decisions)):
    lines.append(f"---\n\n### Case {i+1}: {title}\n\n")
    lines.append(f"**Customer ID:** `{row_data.customer_id}`  \n")
    lines.append(f"**Segment:** {row_data.segment_name}  \n")
    lines.append(f"**Recency:** {row_data.recency} days | **Frequency:** {int(row_data.frequency)} orders | **Monetary:** ₹{row_data.monetary:,.0f}  \n")
    lines.append(f"**Tickets:** {int(row_data.ticket_count)} (Unresolved: {int(row_data.unresolved_tickets)}) | **Return Rate:** {row_data.return_rate:.0%} | **Discount Usage:** {row_data.discount_usage:.0%}  \n")
    lines.append(f"**Churned (label):** {'Yes' if row_data.churned else 'No'}  \n\n")
    lines.append(f"**Why it's ambiguous:** {reasoning}\n\n")

with open("manual_review_cases.md", "w") as f:
    f.writelines(lines)
print("manual_review_cases.md written with", len(cases), "cases")
