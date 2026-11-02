# Official Government Data Sources & Benchmarks for Smart Panchayat AI

This document establishes the official empirical foundation, data provenance, and citation register for the Smart Panchayat AI platform covering **Kerala, Karnataka, Tamil Nadu, Andhra Pradesh, and Maharashtra**.

---

## 1. Primary National Frameworks & Portals

### 1.1 Panchayat Advancement Index (PAI)
* **Authoring Body**: Ministry of Panchayati Raj (MoPR), Government of India
* **Publication / Release**: 2023–2024
* **Scope**: Evaluates ~255,000 Gram Panchayats across 9 Localization of Sustainable Development Goals (LSDGs) themes:
  1. *Theme 1: Poverty Free and Enhanced Livelihood Village* (MPI dimensions, MGNREGA person-days, SHG coverage)
  2. *Theme 2: Healthy Village* (PHC access, immunization coverage, institutional deliveries, IMR)
  3. *Theme 3: Child Friendly Village* (Enrolment ratio, secondary school transition, anganwadi infrastructure)
  4. *Theme 4: Water Sufficient Village* (Functional Household Tap Connections - FHTC, groundwater stage)
  5. *Theme 5: Clean and Green Village* (ODF-Plus status, solid & liquid waste management, solar streetlights)
  6. *Theme 6: Village with Self-Sufficient Infrastructure* (Paved road access, digital connectivity, GP Bhawan)
  7. *Theme 7: Socially Secured and Socially Just Village* (Social security pensions, PwD entitlements)
  8. *Theme 8: Village with Good Governance* (Gram Sabha quorum, Citizen Charter implementation, audit reports)
  9. *Theme 9: Engendered Development in Village* (Women Gram Sabha participation, Kudumbashree / NRLM SHGs)
* **Relevance to Platform**: Defines our primary composite scoring architecture, sector priority classification, and target domain indicators.

### 1.2 eGramSwaraj (egramswaraj.gov.in)
* **Authoring Body**: Ministry of Panchayati Raj (MoPR)
* **Data Cycle**: Financial Years 2020-21 through 2024-25
* **Key Indicators Extracted**:
  * Gram Panchayat Development Plan (GPDP) approved activity budgets.
  * Central Finance Commission (XV-FC) Grants: Tied (Sanitation & Water) vs Untied (Basic Civic Needs) allocations.
  * State Finance Commission (SFC) devolution ratios.
  * Own-Source Revenue (OSR) generation capability per household.
  * Expenditure vs Allocation ratios and fund utilization lag (unspent balances).

### 1.3 Mission Antyodaya Survey
* **Authoring Body**: Ministry of Rural Development (MoRD)
* **Survey Years**: 2019-20, 2020-21, 2022-23
* **Coverage**: Micro-data covering 269 parameters across 29 subjects under the Eleventh Schedule of the Constitution:
  * Distance to sub-centre, Primary Health Centre (PHC), and Community Health Centre (CHC).
  * Distance to primary, upper primary, secondary, and senior secondary schools.
  * Availability of all-weather paved roads (PMGSY compliance).
  * Status of piped water supply, public taps, and drainage networks.
  * Availability of banking correspondents, internet kiosks, and digital CSCs.

### 1.4 NITI Aayog Multidimensional Poverty Index (MPI)
* **Reports**: National Multidimensional Poverty Index: Baseline Report (2021) and Progress Review (2023)
* **Methodology**: Alkire-Foster methodology based on 12 indicators across 3 dimensions:
  * *Health*: Nutrition (41.4% weight if deprived), Child & Adolescent Mortality, Maternal Health.
  * *Education*: Years of Schooling, School Attendance.
  * *Standard of Living*: Cooking Fuel, Sanitation, Drinking Water, Electricity, Housing, Assets, Bank Accounts.
* **Empirical State Poverty Rates (Headcount Ratio, 2023 Review)**:
  * **Kerala**: 0.55% (Lowest in India; Ernakulam: 0.10%, Wayanad: 1.30%)
  * **Tamil Nadu**: 2.20% (Dharmapuri: 4.8%, Kanchipuram: 0.9%)
  * **Karnataka**: 7.58% (Yadgir: 25.2%, Bengaluru Rural: 1.8%)
  * **Andhra Pradesh**: 6.06% (Kurnool: 12.1%, Visakhapatnam: 4.2%)
  * **Maharashtra**: 7.81% (Nandurbar: 33.2%, Pune: 2.1%)

### 1.5 National Family Health Survey (NFHS-5, 2019-2021)
* **Authoring Body**: Ministry of Health and Family Welfare (MoHFW) / IIPS Mumbai
* **Empirical State Metrics (Rural Populations)**:
  * *Institutional Births*: Kerala 99.8%, TN 99.6%, AP 96.5%, Karnataka 97.0%, Maharashtra 94.7%.
  * *Children Stunted (under 5 years)*: Kerala 23.4%, TN 25.0%, AP 31.2%, Karnataka 35.4%, Maharashtra 35.2%.
  * *Sanitation Facility Access (Improved)*: Kerala 98.7%, TN 73.1%, AP 74.0%, Karnataka 74.4%, Maharashtra 73.2%.
  * *Clean Fuel for Cooking*: Kerala 72.1%, TN 79.4%, AP 70.3%, Karnataka 66.8%, Maharashtra 59.8%.

### 1.6 Jal Jeevan Mission (JJM) / Ministry of Jal Shakti
* **Dashboard Data**: Har Ghar Jal Reporting Portal (2023-2024)
* **Functional Household Tap Connection (FHTC) Rural Coverage**:
  * **Kerala**: ~54% (high dependence on open homestead dug wells ~62% households, though JJM expanding).
  * **Tamil Nadu**: ~82% (strong combined water supply scheme CWSS coverage).
  * **Karnataka**: ~72% (drought-prone northern plateau dependent on multi-village schemes).
  * **Andhra Pradesh**: ~70% (high dependency on borewells and local overhead reservoirs).
  * **Maharashtra**: ~81% (high coverage in Western districts, tanker-fed villages in Marathwada).

### 1.7 Census of India (2011 Primary Census Abstract & Subsequent Projections)
* **Authoring Body**: Office of the Registrar General & Census Commissioner, India
* **Demographic Anchors**:
  * Household sizes: Kerala (4.0–4.2), Tamil Nadu (3.8–4.0), Karnataka (4.5–4.8), Andhra Pradesh (3.8–4.2), Maharashtra (4.6–5.0).
  * Rural Sex Ratio (females per 1000 males): Kerala 1084, Tamil Nadu 993, Andhra Pradesh 996, Karnataka 979, Maharashtra 952.
  * Literacy: Kerala (93.9%), Tamil Nadu (80.1%), Maharashtra (82.3%), Karnataka (75.4%), Andhra Pradesh (67.4%).

---

## 2. State-Specific Administrative & Fiscal Architecture

| State | PR Tier Structure | Devolution Framework | Flagship Development Initiatives |
|---|---|---|---|
| **Kerala** | 3-Tier: 941 Grama Panchayats, 152 Block Panchayats, 14 District Panchayats | Highest fiscal decentralization (~25% of State Plan budget directly transferred to local bodies). People's Plan Model. | Kudumbashree Mission, Haritha Keralam (Water & Waste), Aardram (FHC upgrades), LIFE Mission (Housing). |
| **Karnataka** | 3-Tier: 5,958 Gram Panchayats, 233 Taluk Panchayats, 31 Zilla Panchayats | State Finance Commission (SFC) formula allocation; Panchatantra 2.0 digital governance. | Jal Nirmal Project, e-Swathu, Rajiv Gandhi Rural Housing, Grama DigiVikasana. |
| **Tamil Nadu** | 3-Tier: 12,525 Village Panchayats, 388 Panchayat Unions, 36 District Panchayats | Balanced devolution; high coordination with line departments; active Village Poverty Reduction Committees (VPRC). | Namakku Naame Thittam, Anaithu Grama Anna Marumalarchi Thittam (AGAMT-II), Mahalir Thittam SHGs. |
| **Andhra Pradesh** | 3-Tier: 13,326 Gram Panchayats, 660 Mandal Praja Parishads, 26 Zilla Praja Parishads | Decentralized ward/village secretariat system (*Grama Sachivalayam*) with 10-12 frontline functionaries per ~2,000 population. | YSR Rythu Bharosa Kendras (RBKs), Nadu-Nedu (School & Hospital overhaul), Jagananna Thodu. |
| **Maharashtra** | 3-Tier: 27,896 Gram Panchayats, 351 Panchayat Samitis, 34 Zilla Parishads | Historically powerful Zilla Parishads; strong cooperative sector interplay; significant regional disparity (Konkan vs Vidarbha/Marathwada). | Jalyukt Shivar Abhiyan 2.0, Sant Gadge Baba Gram Swachhata Abhiyan, Mukhyamantri Gram Sadak Yojana. |

---

## 3. Data Integrity & Usage Rules
1. **Source Attribution**: All synthetic generation distributions are calibrated directly to the empirical ranges, medians, and standard deviations recorded in these public reports.
2. **Missing Indicators**: Where Village-level granular statistics are unavailable on public portals without institutional login (e.g., Ward-wise GIS coordinates or private audit notes), distributions are modeled using District-level NFHS-5, Census PCA, and Mission Antyodaya aggregates with appropriate Dirichlet/Gaussian variance.
3. **Synthetic Labeling**: In strict compliance with research ethics, all derived dataset records are explicitly tagged as `is_synthetic = True`, ensuring that no artificial figures are misrepresented as official statutory census returns.
