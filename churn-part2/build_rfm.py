import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import warnings, os
warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="Set2")
os.makedirs("outputs", exist_ok=True)

SNAPSHOT_DATE = pd.Timestamp("2024-06-30")

customers = pd.read_csv("data/customers.csv", parse_dates=["join_date"])
orders    = pd.read_csv("data/orders.csv",    parse_dates=["order_date"])
tickets   = pd.read_csv("data/support_tickets.csv", parse_dates=["ticket_date"])
events    = pd.read_csv("data/web_app_events.csv",  parse_dates=["event_date"])
campaigns = pd.read_csv("data/campaigns.csv", parse_dates=["campaign_date"])
churn     = pd.read_csv("data/churn_labels.csv")

# Clean
orders = orders.drop_duplicates(subset=["order_id"])
orders = orders[orders.order_date <= SNAPSHOT_DATE]

# ── RFM ───────────────────────────────────────────────────────────────────────
rfm = orders.groupby("customer_id").agg(
    recency   = ("order_date", lambda x: (SNAPSHOT_DATE - x.max()).days),
    frequency = ("order_id", "count"),
    monetary  = ("amount", "sum")
).reset_index()
rfm["monetary"] = rfm["monetary"].round(2)

# All customers (include those with no orders)
all_custs = customers[["customer_id","membership_tier","age"]].copy()
rfm = all_custs.merge(rfm, on="customer_id", how="left")
rfm[["recency","frequency","monetary"]] = rfm[["recency","frequency","monetary"]].fillna(
    {"recency": 999, "frequency": 0, "monetary": 0})
rfm["recency"] = rfm["recency"].astype(int)

# Scoring (1-4, higher=better)
rfm["R"] = pd.qcut(rfm["recency"],  q=4, labels=[4,3,2,1]).astype(int)
rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"), q=4, labels=[1,2,3,4]).astype(int)
rfm["M"] = pd.qcut(rfm["monetary"].rank(method="first"),  q=4, labels=[1,2,3,4]).astype(int)
rfm["RFM_Score"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)
rfm["RFM_Total"] = rfm[["R","F","M"]].sum(axis=1)

# ── Additional signals ────────────────────────────────────────────────────────
ticket_agg = tickets[tickets.ticket_date <= SNAPSHOT_DATE].groupby("customer_id").agg(
    ticket_count=("ticket_id","count"),
    unresolved_tickets=("resolved", lambda x: (~x).sum()),
    avg_satisfaction=("satisfaction_score","mean")
).reset_index()

return_agg = orders.groupby("customer_id").agg(
    return_rate=("returned","mean"),
    discount_usage=("discount_applied", lambda x: (x>0).mean())
).reset_index()

session_agg = events[events.event_date <= SNAPSHOT_DATE].groupby("customer_id").agg(
    total_sessions=("event_id","count"),
    days_since_session=("event_date", lambda x: (SNAPSHOT_DATE - x.max()).days)
).reset_index()

camp_agg = campaigns[campaigns.campaign_date <= SNAPSHOT_DATE].groupby("customer_id").agg(
    camp_open_rate=("opened","mean"),
    camp_conversion=("converted","mean")
).reset_index()

rfm = rfm.merge(ticket_agg, on="customer_id", how="left")
rfm = rfm.merge(return_agg, on="customer_id", how="left")
rfm = rfm.merge(session_agg, on="customer_id", how="left")
rfm = rfm.merge(camp_agg, on="customer_id", how="left")
rfm[["ticket_count","unresolved_tickets"]] = rfm[["ticket_count","unresolved_tickets"]].fillna(0)
rfm[["return_rate","discount_usage"]] = rfm[["return_rate","discount_usage"]].fillna(0)
rfm["total_sessions"] = rfm["total_sessions"].fillna(0)
rfm["days_since_session"] = rfm["days_since_session"].fillna(999)
rfm[["camp_open_rate","camp_conversion"]] = rfm[["camp_open_rate","camp_conversion"]].fillna(0)

# ── Segmentation ──────────────────────────────────────────────────────────────
def assign_segment(row):
    r, f, m, total = row["R"], row["F"], row["M"], row["RFM_Total"]
    unresolved = row["unresolved_tickets"]
    sessions   = row["total_sessions"]
    ret_rate   = row["return_rate"]
    disc       = row["discount_usage"]
    tier       = row["membership_tier"]

    if total >= 10 and r >= 3:
        return "Champions"
    elif total >= 8 and r >= 3:
        return "Loyal Customers"
    elif r >= 3 and total >= 7 and unresolved > 1:
        return "High-Value But Unhappy"
    elif r <= 2 and total >= 7:
        return "At-Risk Customers"
    elif disc >= 0.5 and f >= 2:
        return "Discount-Sensitive"
    elif r <= 2 and total <= 5 and sessions < 5:
        return "Dormant Customers"
    elif ret_rate > 0.25:
        return "High Returners"
    elif f <= 1 and r >= 3:
        return "New Customers"
    else:
        return "Potential Loyalists"

rfm["segment_name"] = rfm.apply(assign_segment, axis=1)

# ── Export segments.csv ───────────────────────────────────────────────────────
segments_out = rfm[[
    "customer_id","segment_name","recency","frequency","monetary",
    "R","F","M","RFM_Total","ticket_count","unresolved_tickets",
    "return_rate","discount_usage","total_sessions","days_since_session",
    "camp_open_rate","camp_conversion","membership_tier"
]].copy()
segments_out.to_csv("segments.csv", index=False)
print("segments.csv saved:", len(segments_out), "rows")
print("\nSegment distribution:")
print(rfm["segment_name"].value_counts())

# ── Charts ────────────────────────────────────────────────────────────────────
# 1. Segment count
fig, ax = plt.subplots(figsize=(10,5))
seg_counts = rfm["segment_name"].value_counts()
bars = ax.barh(seg_counts.index, seg_counts.values, color=sns.color_palette("Set2", len(seg_counts)))
for bar, val in zip(bars, seg_counts.values):
    ax.text(bar.get_width()+5, bar.get_y()+bar.get_height()/2, str(val), va="center", fontweight="bold")
ax.set_title("Customer Count per Segment")
ax.set_xlabel("Number of Customers")
plt.tight_layout()
plt.savefig("outputs/chart1_segment_counts.png", dpi=120)
plt.close()

# 2. RFM scatter
fig, ax = plt.subplots(figsize=(8,6))
for seg, grp in rfm.groupby("segment_name"):
    ax.scatter(grp["recency"].clip(upper=400), grp["monetary"].clip(upper=8000),
               alpha=0.4, label=seg, s=20)
ax.set_xlabel("Recency (days)"); ax.set_ylabel("Monetary Value (Rs)")
ax.set_title("RFM Scatter: Recency vs Monetary by Segment")
ax.legend(fontsize=7, bbox_to_anchor=(1.01,1))
plt.tight_layout()
plt.savefig("outputs/chart2_rfm_scatter.png", dpi=120)
plt.close()

# 3. Segment avg RFM
seg_rfm = rfm.groupby("segment_name")[["R","F","M"]].mean().round(2)
fig, ax = plt.subplots(figsize=(10,5))
seg_rfm.plot.bar(ax=ax, edgecolor="black")
ax.set_title("Average R, F, M Score per Segment")
ax.set_ylabel("Score (1-4)"); ax.legend(["Recency","Frequency","Monetary"])
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("outputs/chart3_segment_rfm_scores.png", dpi=120)
plt.close()

# 4. Churn rate per segment
rfm_churn = rfm.merge(churn, on="customer_id", how="left")
seg_churn = rfm_churn.groupby("segment_name")["churned"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10,5))
bars = ax.bar(seg_churn.index, seg_churn.values, color=sns.color_palette("Reds_r", len(seg_churn)), edgecolor="black")
import matplotlib.ticker as mticker
ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
ax.set_title("Churn Rate per Segment"); ax.set_ylabel("Churn Rate")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("outputs/chart4_segment_churn_rate.png", dpi=120)
plt.close()

# 5. Monetary boxplot
fig, ax = plt.subplots(figsize=(12,5))
order_segs = rfm.groupby("segment_name")["monetary"].median().sort_values(ascending=False).index
rfm.boxplot(column="monetary", by="segment_name", ax=ax, figsize=(12,5))
ax.set_title("Monetary Value Distribution per Segment"); ax.set_xlabel("")
ax.set_ylabel("Total Spend (Rs)")
plt.suptitle("")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("outputs/chart5_monetary_boxplot.png", dpi=120)
plt.close()

print("All charts saved.")
