# Fresher Deployment Agent (FDA) — System Memory

## 🧠 Purpose

FDA is an **advisory agent** that analyzes workforce distribution across projects/accounts and identifies:

* Pyramid imbalances
* Fresher deployment opportunities
* Training recommendations

It DOES NOT modify any system or approve deployments.

---

## 🎯 Target Pyramid (FIXED)

* Junior: **79%**
* Mid-level: **20%**
* Senior: **1%**

Do NOT change these unless explicitly instructed.

---

## 📥 Inputs

### Primary Source

* RIS data (Excel)

### Required Fields

* Employee ID
* Grade
* Project ID / Account Name
* Assignment Status
* Start / End Dates

### Optional Fields

* Skills (Primary, Secondary)
* Technology
* Role
* Location

---

## 🔁 Core Processing Flow

1. **Load Data**

   * RIS Excel
   * Grade mapping CSV

2. **Validate**

   * Reject null Employee ID / Project ID
   * Handle invalid dates
   * Log unmapped grades

3. **Map Grades**

   * Use `grade_band_map.csv`
   * Map → Junior / Mid / Senior
   * NEVER hardcode mapping

4. **Filter Active Records**

   * Based on confirmed rules (KT dependent)

5. **Aggregate**

   * Group by Project / Account
   * Compute:

     * Total headcount
     * Junior / Mid / Senior counts
     * Percentages

6. **Compare with Target**

   * Compute gaps:

     * Junior Gap = 79 - Actual
     * Mid Gap = 20 - Actual
     * Senior Gap = 1 - Actual

7. **Apply Rules (R1–R4)**

---

## ⚙️ Business Rules

### R1 — Low Junior Ratio (HIGH)

Trigger:

* Junior % < 79

Output:

* Flag
* Compute Junior Gap

---

### R2 — High Fresher Intake (MEDIUM)

Trigger:

* Too many juniors relative to team size or intake velocity

Output:

* Flag imbalance

---

### R3 — Deployment Opportunity (HIGH, Hybrid)

Trigger:

* R1 is true AND
* Project has entry-level compatible roles/skills

Output:

* Deployment Opportunity = YES/NO
* (Optional) Deployment Readiness Score

---

### R4 — Training Suggestion (MEDIUM, Hybrid)

Trigger:

* Project flagged in R3

Output:

* Extract dominant skills
* Suggest training themes

---

## 📤 Outputs

### 1. Pyramid Report (Excel)

Per project/account:

* Headcount
* Ratios
* Gaps
* Flags
* Health Status

---

### 2. Suggestions Report (Excel)

Per deployment candidate:

* Deployment flag
* Suggested fresher count
* Skills context
* Training suggestions
* (Optional) Score

---

## 🚫 HARD CONSTRAINTS (CRITICAL)

* Read-only system (NO writes to RIS)
* No external LLM/API calls with raw data
* All AI logic must run locally
* Grade mapping must be configurable (CSV)
* No hardcoded mappings
* Must handle missing/unmapped data gracefully
* Input format must NOT be altered

Violation = disqualification

---

## 🧩 AI Usage Policy

### Rule-Based (Mandatory Core)

* R1, R2 → pure logic

### Hybrid (Optional)

* R3 → smarter matching / scoring
* R4 → skill clustering / recommendations

AI is NOT required for core functionality.

---

## 🏗️ Tech Stack (MANDATORY)

* Python (3.9+)
* Pandas / NumPy
* PostgreSQL (storage, logs, outputs)
* SQLAlchemy / psycopg2

### If AI used:

* LangGraph / LangChain
* Model: **gpt-5-mini ONLY**

---

## 📊 System Nature

* Batch processing agent
* Data pipeline + rule engine
* Advisory outputs only
* No real-time inference required

---

## ⚠️ Configurable Decisions (KT Required)

* Grade → Band mapping
* Unit of analysis (Project vs Account)
* Active employee definition
* Thresholds for R2

---

## 📁 Expected Structure (Logical)

* ingestion
* validation
* mapping
* aggregation
* rule_engine
* recommendation_engine
* output_writer
* config_loader

---

## 🧠 Key Principles

* Deterministic > AI
* Explainable outputs
* Config-driven logic
* Fail-safe data handling
* Zero data leakage

---

## ✅ Final Objective

Produce:

1. Accurate pyramid analysis
2. Actionable fresher deployment suggestions
3. Skill-based training recommendations

WITHOUT:

* Modifying any system
* Using external AI APIs
* Breaking constraints
