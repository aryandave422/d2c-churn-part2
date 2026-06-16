# Manual Review Cases
## D2C Churn Intelligence — Part 2
These 10 customers present ambiguous retention decisions. Standard segmentation logic alone is insufficient.

---
---

### Case 1: High-value but gone quiet — worth saving

**Customer ID:** `CUST00059`  
**Segment:** At-Risk Customers  
**Recency:** 150 days | **Frequency:** 3 orders | **Monetary:** ₹1,058  
**Tickets:** 1 (Unresolved: 0) | **Return Rate:** 33% | **Discount Usage:** 33%  
**Churned (label):** No  

**Why it's ambiguous:** This customer has spent heavily historically but hasn't ordered in 90+ days. Segment says At-Risk but monetary value is in top quartile. **Decision: Send personalized reactivation with 10% VIP offer. Do NOT put in generic batch campaign. Assign to a dedicated CS follow-up.**

---

### Case 2: New but inactive — early warning

**Customer ID:** `CUST00060`  
**Segment:** At-Risk Customers  
**Recency:** 91 days | **Frequency:** 5 orders | **Monetary:** ₹931  
**Tickets:** 0 (Unresolved: 0) | **Return Rate:** 0% | **Discount Usage:** 60%  
**Churned (label):** No  

**Why it's ambiguous:** Only 2 orders but both were recent. App sessions are extremely low. Could be a one-time buyer or someone who just hasn't found a reason to return. **Decision: Trigger product discovery email sequence. Offer 'Complete your routine' bundle. Monitor for 30 days before escalating.**

---

### Case 3: Discount hunter — risky to incentivize further

**Customer ID:** `CUST00090`  
**Segment:** New Customers  
**Recency:** 25 days | **Frequency:** 2 orders | **Monetary:** ₹83  
**Tickets:** 1 (Unresolved: 0) | **Return Rate:** 0% | **Discount Usage:** 100%  
**Churned (label):** No  

**Why it's ambiguous:** Over 60% of purchases used a discount. Still ordering recently. If we give another discount, we train them further. **Decision: Test a loyalty-points offer instead of cash discount. If conversion drops, accept the loss — margin on this customer is thin.**

---

### Case 4: Complaint-heavy but loyal — CS priority

**Customer ID:** `CUST00106`  
**Segment:** New Customers  
**Recency:** 16 days | **Frequency:** 2 orders | **Monetary:** ₹101  
**Tickets:** 0 (Unresolved: 0) | **Return Rate:** 0% | **Discount Usage:** 50%  
**Churned (label):** No  

**Why it's ambiguous:** 3+ tickets but hasn't churned. This is a resilient customer who still buys despite bad experiences. **Decision: Escalate all open tickets immediately. Assign dedicated CS rep. Send handwritten apology note. Do NOT send marketing until tickets resolved.**

---

### Case 5: Champion but returns often — quality concern

**Customer ID:** `CUST00021`  
**Segment:** Champions  
**Recency:** 0 days | **Frequency:** 14 orders | **Monetary:** ₹1,358  
**Tickets:** 0 (Unresolved: 0) | **Return Rate:** 14% | **Discount Usage:** 64%  
**Churned (label):** No  

**Why it's ambiguous:** Top segment by RFM but 20%+ return rate. This could mean quality dissatisfaction that will eventually cause churn. **Decision: Proactive outreach asking for product feedback. Offer exchange instead of return on next issue. Flag for product team.**

---

### Case 6: High value, dormant, satisfied before

**Customer ID:** `CUST00064`  
**Segment:** Champions  
**Recency:** 9 days | **Frequency:** 11 orders | **Monetary:** ₹1,487  
**Tickets:** 0 (Unresolved: 0) | **Return Rate:** 18% | **Discount Usage:** 73%  
**Churned (label):** No  

**Why it's ambiguous:** Was highly active, went silent. No complaints. Could be life circumstances or found an alternative. **Decision: Win-back email with personal tone ('We noticed you haven't been around'). No generic promo. If no response in 7 days, suppress for 60 days.**

---

### Case 7: New customer, very high first order value

**Customer ID:** `CUST00012`  
**Segment:** Champions  
**Recency:** 17 days | **Frequency:** 6 orders | **Monetary:** ₹634  
**Tickets:** 6 (Unresolved: 1) | **Return Rate:** 17% | **Discount Usage:** 17%  
**Churned (label):** No  

**Why it's ambiguous:** First order was very large (top 20% AOV). Could be a bulk buyer or testing. High potential but uncertain. **Decision: Personal welcome email. Offer onboarding call. Assign to high-value new customer journey. Monitor second-order timing closely.**

---

### Case 8: Active sessions but no orders recently

**Customer ID:** `CUST00037`  
**Segment:** At-Risk Customers  
**Recency:** 233 days | **Frequency:** 7 orders | **Monetary:** ₹680  
**Tickets:** 3 (Unresolved: 1) | **Return Rate:** 0% | **Discount Usage:** 43%  
**Churned (label):** No  

**Why it's ambiguous:** Visiting the app regularly but not converting. Possible cart abandonment loop. **Decision: Trigger cart-abandonment flow. Show recently viewed products. Offer free shipping for next 48 hours. High conversion probability.**

---

### Case 9: Mid-tier customer with low satisfaction score

**Customer ID:** `CUST00101`  
**Segment:** Champions  
**Recency:** 49 days | **Frequency:** 9 orders | **Monetary:** ₹983  
**Tickets:** 1 (Unresolved: 0) | **Return Rate:** 22% | **Discount Usage:** 22%  
**Churned (label):** Yes  

**Why it's ambiguous:** Average satisfaction score of 2/5 on resolved tickets. Still ordering but barely. **Decision: CS outreach asking what went wrong. Do NOT send promotional email. Fix experience first.**

---

### Case 10: Dormant but just opened last campaign email

**Customer ID:** `CUST00113`  
**Segment:** Champions  
**Recency:** 63 days | **Frequency:** 7 orders | **Monetary:** ₹727  
**Tickets:** 0 (Unresolved: 0) | **Return Rate:** 29% | **Discount Usage:** 29%  
**Churned (label):** No  

**Why it's ambiguous:** Dormant for 6 months but opened a campaign in the last week. Recency spike in engagement. **Decision: Strike while the iron is hot — follow up within 24hrs with a targeted offer. This is a recovery signal.**

