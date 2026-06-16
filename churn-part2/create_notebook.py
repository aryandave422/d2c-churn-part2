import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []
def md(s): return nbf.v4.new_markdown_cell(s)
def code(s): return nbf.v4.new_code_cell(s)

cells.append(md("# Part 2 – RFM Segmentation & Retention Strategy\n## D2C Customer Churn Intelligence Capstone\n**Snapshot Date:** June 30, 2024"))
cells.append(code("""import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.ticker as mticker
import seaborn as sns, warnings, os
warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="Set2")
os.makedirs("outputs", exist_ok=True)
print("Libraries loaded.")"""))

cells.append(md("## 1. Load Data"))
cells.append(code("""SNAPSHOT_DATE = pd.Timestamp("2024-06-30")
customers = pd.read_csv("data/customers.csv", parse_dates=["join_date"])
orders    = pd.read_csv("data/orders.csv",    parse_dates=["order_date"])
tickets   = pd.read_csv("data/support_tickets.csv", parse_dates=["ticket_date"])
events    = pd.read_csv("data/web_app_events.csv",  parse_dates=["event_date"])
campaigns = pd.read_csv("data/campaigns.csv", parse_dates=["campaign_date"])
churn     = pd.read_csv("data/churn_labels.csv")
orders = orders.drop_duplicates(subset=["order_id"])
orders = orders[orders.order_date <= SNAPSHOT_DATE]
print("Data loaded and cleaned.")"""))

cells.append(md("## 2. RFM Feature Creation"))
cells.append(code("""rfm = orders.groupby("customer_id").agg(
    recency   = ("order_date", lambda x: (SNAPSHOT_DATE - x.max()).days),
    frequency = ("order_id", "count"),
    monetary  = ("amount", "sum")
).reset_index()

all_custs = customers[["customer_id","membership_tier","age"]].copy()
rfm = all_custs.merge(rfm, on="customer_id", how="left")
rfm[["recency","frequency","monetary"]] = rfm[["recency","frequency","monetary"]].fillna({"recency":999,"frequency":0,"monetary":0})
rfm["recency"] = rfm["recency"].astype(int)
rfm["monetary"] = rfm["monetary"].round(2)

rfm["R"] = pd.qcut(rfm["recency"], q=4, labels=[4,3,2,1]).astype(int)
rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"), q=4, labels=[1,2,3,4]).astype(int)
rfm["M"] = pd.qcut(rfm["monetary"].rank(method="first"),  q=4, labels=[1,2,3,4]).astype(int)
rfm["RFM_Total"] = rfm[["R","F","M"]].sum(axis=1)
rfm[["customer_id","recency","frequency","monetary","R","F","M","RFM_Total"]].head(10)"""))

cells.append(md("## 3. Additional Behavioural Signals"))
cells.append(code("""ticket_agg = tickets[tickets.ticket_date<=SNAPSHOT_DATE].groupby("customer_id").agg(
    ticket_count=("ticket_id","count"), unresolved_tickets=("resolved",lambda x:(~x).sum()),
    avg_satisfaction=("satisfaction_score","mean")).reset_index()

return_agg = orders.groupby("customer_id").agg(
    return_rate=("returned","mean"), discount_usage=("discount_applied",lambda x:(x>0).mean())).reset_index()

session_agg = events[events.event_date<=SNAPSHOT_DATE].groupby("customer_id").agg(
    total_sessions=("event_id","count"),
    days_since_session=("event_date",lambda x:(SNAPSHOT_DATE-x.max()).days)).reset_index()

camp_agg = campaigns[campaigns.campaign_date<=SNAPSHOT_DATE].groupby("customer_id").agg(
    camp_open_rate=("opened","mean"), camp_conversion=("converted","mean")).reset_index()

for df in [ticket_agg, return_agg, session_agg, camp_agg]:
    rfm = rfm.merge(df, on="customer_id", how="left")

rfm[["ticket_count","unresolved_tickets","total_sessions"]] = rfm[["ticket_count","unresolved_tickets","total_sessions"]].fillna(0)
rfm[["return_rate","discount_usage","camp_open_rate","camp_conversion"]] = rfm[["return_rate","discount_usage","camp_open_rate","camp_conversion"]].fillna(0)
rfm["days_since_session"] = rfm["days_since_session"].fillna(999)
print("All signals merged. Shape:", rfm.shape)"""))

cells.append(md("## 4. Segment Assignment"))
cells.append(code("""def assign_segment(row):
    r, f, m, total = row["R"], row["F"], row["M"], row["RFM_Total"]
    if total >= 10 and r >= 3: return "Champions"
    elif total >= 8 and r >= 3: return "Loyal Customers"
    elif r >= 3 and total >= 7 and row["unresolved_tickets"] > 1: return "High-Value But Unhappy"
    elif r <= 2 and total >= 7: return "At-Risk Customers"
    elif row["discount_usage"] >= 0.5 and f >= 2: return "Discount-Sensitive"
    elif r <= 2 and total <= 5 and row["total_sessions"] < 5: return "Dormant Customers"
    elif row["return_rate"] > 0.25: return "High Returners"
    elif f <= 1 and r >= 3: return "New Customers"
    else: return "Potential Loyalists"

rfm["segment_name"] = rfm.apply(assign_segment, axis=1)
rfm["segment_name"].value_counts()"""))

cells.append(md("## 5. Visualisations"))
cells.append(code("""# Segment size
fig, ax = plt.subplots(figsize=(10,5))
counts = rfm["segment_name"].value_counts()
ax.barh(counts.index, counts.values, color=sns.color_palette("Set2", len(counts)))
ax.set_title("Customer Count per Segment"); ax.set_xlabel("Count")
plt.tight_layout(); plt.savefig("outputs/chart1_segment_counts.png", dpi=120); plt.show()"""))

cells.append(code("""# RFM scatter
fig, ax = plt.subplots(figsize=(9,6))
for seg, grp in rfm.groupby("segment_name"):
    ax.scatter(grp["recency"].clip(upper=400), grp["monetary"].clip(upper=8000), alpha=0.35, label=seg, s=18)
ax.set_xlabel("Recency (days)"); ax.set_ylabel("Monetary Value (Rs)")
ax.set_title("Recency vs Monetary by Segment")
ax.legend(fontsize=7, bbox_to_anchor=(1.01,1))
plt.tight_layout(); plt.savefig("outputs/chart2_rfm_scatter.png", dpi=120); plt.show()"""))

cells.append(code("""# Churn rate per segment
rfm_churn = rfm.merge(churn, on="customer_id", how="left")
seg_churn = rfm_churn.groupby("segment_name")["churned"].mean().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10,5))
ax.bar(seg_churn.index, seg_churn.values, color=sns.color_palette("Reds_r", len(seg_churn)), edgecolor="black")
ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
ax.set_title("Churn Rate per Segment"); plt.xticks(rotation=30, ha="right")
plt.tight_layout(); plt.savefig("outputs/chart4_segment_churn_rate.png", dpi=120); plt.show()"""))

cells.append(code("""# Avg RFM score per segment
seg_rfm = rfm.groupby("segment_name")[["R","F","M"]].mean().round(2)
fig, ax = plt.subplots(figsize=(10,5))
seg_rfm.plot.bar(ax=ax, edgecolor="black")
ax.set_title("Average R, F, M Score per Segment"); ax.set_ylabel("Score (1-4)")
ax.legend(["Recency","Frequency","Monetary"]); plt.xticks(rotation=30, ha="right")
plt.tight_layout(); plt.savefig("outputs/chart3_segment_rfm_scores.png", dpi=120); plt.show()"""))

cells.append(md("## 6. Export Segments"))
cells.append(code("""segments_out = rfm[["customer_id","segment_name","recency","frequency","monetary",
    "R","F","M","RFM_Total","ticket_count","unresolved_tickets","return_rate",
    "discount_usage","total_sessions","days_since_session","membership_tier"]]
segments_out.to_csv("segments.csv", index=False)
print("segments.csv saved:", len(segments_out), "customers")
print("\\nSegment summary:")
rfm_churn.groupby("segment_name").agg(
    count=("customer_id","count"),
    avg_monetary=("monetary","mean"),
    avg_recency=("recency","mean"),
    churn_rate=("churned","mean")
).round(2).sort_values("churn_rate", ascending=False)"""))

nb.cells = cells
with open("rfm_segmentation.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("rfm_segmentation.ipynb written.")
