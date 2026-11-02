# Research Methodology: Data Generation, Feature Engineering & Optimization

This document outlines the end-to-end mathematical, statistical, and architectural methodology implemented in the Smart Panchayat AI platform.

---

## 1. Synthetic Data Generation Architecture

### 1.1 Objective & Philosophical Foundation
To train production-grade machine learning models for local rural governance across 5 Indian states without relying on synthetic randomness. All synthetic records represent mathematically grounded realizations of joint probability distributions observed in official government reports (PAI, Mission Antyodaya, NFHS-5, NITI Aayog MPI, Census 2011, and eGramSwaraj).

### 1.2 Multi-Scale Hierarchical Sampling
1. **Administrative Anchor**:
   Each record is assigned an authentic State, District, Sub-District (Taluk/Block/Mandal), and Gram Panchayat name drawn from real administrative records.
2. **Demographic Distribution**:
   * *Kerala*: Population $\sim \mathcal{N}(\mu=32000, \sigma=8500)$, bounded $[14000, 65000]$; Household size $\sim 4.1$.
   * *Karnataka*: Population $\sim \text{LogNormal}(\mu=\ln(5200), \sigma=0.35)$, bounded $[1800, 14000]$; Household size $\sim 4.6$.
   * *Tamil Nadu*: Population $\sim \text{LogNormal}(\mu=\ln(4100), \sigma=0.32)$, bounded $[1500, 12000]$; Household size $\sim 3.9$.
   * *Andhra Pradesh*: Population $\sim \text{LogNormal}(\mu=\ln(3800), \sigma=0.30)$, bounded $[1400, 10000]$; Household size $\sim 4.0$.
   * *Maharashtra*: Population $\sim \text{LogNormal}(\mu=\ln(3400), \sigma=0.45)$, bounded $[1200, 15000]$; Household size $\sim 4.8$.

### 1.3 Parametric Conditional Distributions
Features are sampled conditionally to preserve real-world macroeconomic and geographical correlations:
* **Income & Poverty**:
  $$\text{Household Income} = \text{Base}_{\text{state}} \cdot (1 - 0.75 \cdot \text{poverty\_rate}) + \epsilon_{\text{inc}}$$
  where $\epsilon_{\text{inc}} \sim \mathcal{N}(0, \sigma^2)$.
* **Education & Dropouts**:
  Dropout rates increase non-linearly when teacher vacancy and distance to secondary schools exceed threshold barriers.
* **Water Vulnerability**:
  Modeled as an interaction between groundwater extraction stage (over-exploited vs safe) and piped tap water penetration (JJM):
  $$\text{Water Deficit} = (1 - \text{tap\_coverage}) \cdot (0.6 \cdot \text{gw\_scarcity} + 0.4 \cdot \text{summer\_stress})$$

---

## 2. Derived Feature Engineering & Domain Scores

To ensure maximum interpretability and empower gradient boosted trees, raw indicators are transformed into normalized domain scores $\in [0, 1]$, where **$1.0$ represents optimal development / maximum security** and **$0.0$ represents critical deprivation**:

### 2.1 Healthcare Accessibility Score ($S_{\text{health}}$)
$$S_{\text{health}} = 0.25 \cdot \text{PHC\_access} + 0.20 \cdot \text{Doc\_avail} + 0.25 \cdot \text{Mat\_health} + 0.15 \cdot (1 - \text{Stunting}) + 0.15 \cdot \text{Health\_ins}$$

### 2.2 Education Development Score ($S_{\text{edu}}$)
$$S_{\text{edu}} = 0.30 \cdot \text{Literacy} + 0.25 \cdot \text{Enrollment} + 0.25 \cdot (1 - \text{Dropout}) + 0.10 \cdot \text{Teacher\_avail} + 0.10 \cdot \text{Digital\_edu}$$

### 2.3 Water Security Score ($S_{\text{water}}$)
$$S_{\text{water}} = 0.35 \cdot \text{Tap\_coverage} + 0.25 \cdot \text{Perennial\_avail} + 0.20 \cdot (1 - \text{GW\_stress}) + 0.20 \cdot \text{Water\_quality}$$

### 2.4 Infrastructure Gap Score ($G_{\text{infra}}$)
$$G_{\text{infra}} = 1.0 - \left( 0.30 \cdot \text{Paved\_roads} + 0.25 \cdot \text{Electricity} + 0.20 \cdot \text{Streetlights} + 0.15 \cdot \text{Internet} + 0.10 \cdot \text{Pucca\_house} \right)$$
*(Note: Higher value indicates higher infrastructure deficit).*

### 2.5 Livelihood Opportunity Score ($S_{\text{live}}$)
$$S_{\text{live}} = 0.30 \cdot (1 - \text{Poverty\_rate}) + 0.25 \cdot \text{Employment\_rate} + 0.20 \cdot \text{SHG\_coverage} + 0.25 \cdot \text{Wage\_diversity}$$

### 2.6 Financial Utilization Score ($S_{\text{fin}}$)
$$S_{\text{fin}} = 0.50 \cdot \text{Project\_completion\_rate} + 0.30 \cdot \left( \frac{\text{Actual\_exp}}{\text{Allocated\_budget}} \right) + 0.20 \cdot \text{OSR\_ratio}$$

### 2.7 Composite Overall Panchayat Development Score (OPDS)
$$OPDS = 0.20 \cdot S_{\text{health}} + 0.20 \cdot S_{\text{edu}} + 0.20 \cdot S_{\text{water}} + 0.15 \cdot (1 - G_{\text{infra}}) + 0.15 \cdot S_{\text{live}} + 0.10 \cdot S_{\text{fin}}$$

---

## 3. Machine Learning Target Formulations

### 3.1 Task 1: Priority Sector Multi-Class Classification
Identifies the primary sector requiring immediate capital intervention.
$$\text{Priority Sector} = \arg\max_{c \in \mathcal{C}} \left( \text{Deficit}_c \times \text{Vulnerability Weight}_c \right)$$
Where $\mathcal{C} = \{\text{Water \& Sanitation, Healthcare, Education, Infrastructure, Agriculture \& Livelihood, Social Welfare}\}$.
* Rule: If $S_{\text{water}} < 0.40$ and Drought/GW Stress $> 0.65 \implies$ *Water & Sanitation*.
* Rule: If $S_{\text{health}} < 0.45$ and Maternal/Stunting Deficit $> 0.60 \implies$ *Healthcare*.
* Rule: If $S_{\text{edu}} < 0.50$ and Dropout Rate $> 0.10 \implies$ *Education*.
* Rule: If $G_{\text{infra}} > 0.55 \implies$ *Infrastructure*.
* Rule: If Poverty $> 0.18$ or Unemployment $> 0.12 \implies$ *Agriculture & Livelihood*.

### 3.2 Task 2: Development Gap Categorization (Ordinal 5-Class)
Stratifies Panchayats based on OPDS:
* **Critical**: $OPDS < 0.40$ (immediate central intervention required)
* **High Priority**: $0.40 \le OPDS < 0.55$
* **Moderate**: $0.55 \le OPDS < 0.70$
* **Good**: $0.70 \le OPDS < 0.82$
* **Well Developed**: $OPDS \ge 0.82$

### 3.3 Task 3: Budget Requirement Regression
Predicts total estimated capital outlay (in ₹ Lakhs) necessary to close identified deficits:
$$\text{Budget Req} = \text{Base Cost} \times \text{Population}^{0.65} \times (1.0 - OPDS)^{1.4} \times \text{Terrain Factor}$$

### 3.4 Task 4: Panchayat Clustering (K-Means)
Unsupervised clustering grouping Panchayats into distinct operational archetypes:
1. *Agrarian High-Vulnerability Arid Clusters*
2. *Peri-Urban Industrializing High-Density Clusters*
3. *Fragile Mountain / Coastal Eco-Sensitive Clusters*
4. *Well-Funded High Human Capital Clusters*

### 3.5 Task 5: Anomaly Detection (Isolation Forest)
Identifies outliers exhibiting contradictory indicators (e.g., high budget expenditure with zero infrastructure growth, or high poverty with low unemployment).

---

## 4. Linear Programming Budget Optimization Model

### 4.1 Mathematical Formulation
Let $B$ be the total available budget in ₹ Lakhs for the Gram Panchayat.
Let $x_i$ be the allocation to sector $i \in \{1, \dots, N\}$.

$$\text{Maximize } Z = \sum_{i=1}^N w_i \cdot x_i$$
Where $w_i = \text{Priority Weight}_i \times \text{Deficit Score}_i \times \left( \frac{\text{Population}}{10000} \right)^{0.3}$.

**Subject to Constraints**:
1. **Budget Conservation**:
   $$\sum_{i=1}^N x_i \le B$$
2. **Statutory Floor (Minimum Civic Amenities)**:
   $$x_i \ge m_i \cdot B \quad \forall i \in \{1, \dots, N\}$$
   (e.g., Drinking Water $\ge 15\%$, Sanitation $\ge 10\%$, Healthcare $\ge 10\%$, Education $\ge 10\%$).
3. **Absorptive Capacity Ceiling**:
   $$x_i \le c_i \cdot B \quad \forall i \in \{1, \dots, N\}$$
   (e.g., No single sector may consume $> 45\%$ of total uncommitted plan funds).
4. **Estimated Deficit Cap**:
   $$x_i \le \text{Estimated Requirement}_i$$
   (Prevents over-allocation beyond actual structural need).

This LP is solved deterministically using HiGHS / Simplex via `scipy.optimize.linprog`.

---

## 5. Validation & Leakage Prevention Protocol
* **Group-Aware Splitting**: Train/Test splits (80/20) are partitioned with stratification on `priority_sector` and grouping by Sub-District (`block_taluk_mandal`). This guarantees that no wards or villages from the same contiguous local cluster exist in both training and test sets.
* **Strict Preprocessing Pipeline**: All scalers, imputers, and encoders are fit *strictly* on the training split, and only applied to the test split during evaluation.
