<div align="center">

# 🤖 ResumeRank AI
### Automated Resume Extraction, Scoring & Ranking System

[![Hackathon](https://img.shields.io/badge/SAH_Hackathon_2025-ABES_Engineering-blue?style=for-the-badge&logo=trophy)](https://github.com)
[![Problem](https://img.shields.io/badge/Problem_ID-AI--PS--1-orange?style=for-the-badge)](https://github.com)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

> **An AI-powered pipeline that reads, scores, and ranks resumes — bias-free, explainable, and scalable to 25+ candidates in a single run.**

<br/>

![-----](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

</div>

<br/>

## 📌 Table of Contents

- [🎯 Problem Statement](#-problem-statement)
- [💡 Our Solution](#-our-solution)
- [🔄 Pipeline Architecture](#-pipeline-architecture)
- [⚖️ Scoring System](#️-scoring-system)
- [✨ Novel Features](#-novel-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Getting Started](#-getting-started)
- [📊 Sample Output](#-sample-output)
- [📁 Project Structure](#-project-structure)
- [👥 Team](#-team)

<br/>

![-----](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 🎯 Problem Statement

> **Smart ABES Hackathon (SAH) · Problem ID: AI-PS-1**
> *Domain: AI & Talent Acquisition · Hosted by Techknowledge Edusearch*

Organizations receive resumes in **large volumes and diverse formats** (PDF, DOC, DOCX). Manual screening is:

| Problem | Impact |
|---|---|
| ⏱️ Slow & unscalable | Bottlenecks in high-volume hiring |
| 🎲 Inconsistent | Different reviewers score differently |
| 🧍 Bias-prone | Gender, age, caste influence decisions |
| 📉 Non-explainable | Candidates don't know why they were rejected |

### Core Challenge
Design an algorithm that can:
- ✅ Accurately extract structured data from unstructured resumes
- ✅ Quantitatively evaluate resumes with a max score of **100**
- ✅ Rank **25+ candidates** objectively in a single run
- ✅ Handle format variability, ambiguity, and missing information

**Acceptance Threshold:** ≥ 95% extraction accuracy · No system failures · Complete ranking output

<br/>

![-----](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 💡 Our Solution

We built a **5-stage automated pipeline** that converts raw resume files into a ranked leaderboard — with no manual intervention.

```
Raw Resumes (PDF/DOCX)
        │
        ▼
┌───────────────────┐
│  1. File Reading  │  ← pdfplumber + python-docx
└────────┬──────────┘
         │
         ▼
┌───────────────────────────┐
│  2. Clean + Bias Removal  │  ← Strip gender, age, caste, DOB  ★ NOVEL
└────────┬──────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  3. Information Extraction           │  ← Regex + spaCy NLP
│     skills · CGPA · projects ·       │
│     internships · achievements ...   │
└────────┬─────────────────────────────┘
         │
         ▼
┌───────────────────────────────┐
│  4. CGPA Normalization        │  ← /10, /4, % → unified scale  ★ NOVEL
│     Min-Max across dataset    │
└────────┬──────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  5. Weighted Scoring + Rank  │  ← 11 categories · Max 100 pts
│     pandas sort · bar chart  │
└──────────────────────────────┘
         │
         ▼
  📊 Top 25 Ranked Leaderboard
```

<br/>

![-----](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## ⚖️ Scoring System

Scores are calculated using **research-backed weights** across 11 categories, capped to prevent overfitting from verbose resumes.

| # | Category | Weight | Notes |
|---|---|---|---|
| 1 | 🏢 Prior Internships | **20%** | Binary: present or not |
| 2 | 🧠 Skills & Certifications | **20%** | `min(skills × 2, 20)` — capped |
| 3 | 🔨 Projects | **15%** | `min(projects × 3, 15)` — capped |
| 4 | 🎓 College CGPA | **10%** | Min-max normalized across dataset |
| 5 | 🏆 Quantifiable Achievements | **10%** | Keywords: award, winner, achievement |
| 6 | 💼 Work Experience | **5%** | Years extracted via regex |
| 7 | ⚽ Extra-Curricular | **5%** | Volunteer, club, sports, leader |
| 8 | 🗣️ Language Fluency | **3%** | Count of known languages |
| 9 | 🌐 Online Presence | **3%** | LinkedIn / GitHub URLs detected |
| 10 | 🎯 Degree Type | **3%** | B.Tech, M.Tech, MBA, PhD |
| 11 | 📋 School Marks | **2%** | 10th / 12th mentioned |
| | **TOTAL** | **100%** | |

> ⚠️ **Anti-Overfitting:** Every category has a score cap. A 10-page resume with repeated keywords does **not** outscore a concise, quality resume.

<br/>

![-----](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## ✨ Novel Features

### 🔒 1. Bias Removal (Pre-Scoring)
Before any evaluation, sensitive personal identifiers are stripped using regex:

```python
def remove_sensitive_information(text):
    sensitive_patterns = [
        r"\b(male|female|he|she|him|her)\b",   # Gender
        r"\b(age\s*\d+)\b",                     # Age
        r"\b(dob|date of birth)\b.*",            # Date of Birth
        r"\b(photo|photograph)\b",               # Photo reference
        r"\b(religion|caste|married)\b"          # Social identifiers
    ]
    for pattern in sensitive_patterns:
        text = re.sub(pattern, "", text)
    return text
```

### 📐 2. Multi-Format CGPA Normalization
Handles **three different CGPA formats** and normalizes across the entire dataset using Min-Max scaling:

```python
def extract_raw_cgpa(text):
    match_10 = re.search(r"(\d+\.?\d*)\s*/\s*10", text)   # e.g. 8.5/10
    if match_10: return float(match_10.group(1))

    match_4 = re.search(r"(\d+\.?\d*)\s*/\s*4", text)     # e.g. 3.7/4
    if match_4: return (float(match_4.group(1)) / 4) * 10

    match_pct = re.search(r"(\d+\.?\d*)\s*%", text)        # e.g. 85%
    if match_pct: return float(match_pct.group(1)) / 10
```

### 🛡️ 3. Two-Pass Processing
- **Pass 1** — Extract raw data from all resumes
- **Pass 2** — Normalize CGPA *across the full dataset*, then score
- This ensures fair relative comparison rather than absolute grading

<br/>

![-----](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 🛠️ Tech Stack

| Library | Version | Purpose |
|---|---|---|
| `pdfplumber` | latest | PDF text extraction |
| `python-docx` | latest | DOCX parsing |
| `spaCy` | `en_core_web_sm` | NLP processing |
| `pandas` | latest | Ranking & data handling |
| `matplotlib` | latest | Bar chart visualization |
| `re` | stdlib | Regex pattern matching |
| `os` | stdlib | File system traversal |

<br/>

![-----](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/resumerank-ai.git
cd resumerank-ai
```

### 2. Install Dependencies
```bash
pip install pdfplumber python-docx spacy pandas matplotlib
python -m spacy download en_core_web_sm
```

### 3. Add Your Resumes
```bash
mkdir resumes
# Place your .pdf or .docx resume files inside /resumes
```

### 4. Run the Pipeline
```bash
python resume_ranker.py
# When prompted, enter the path to your resume folder:
# Enter resume folder path: ./resumes
```

<br/>

![-----](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 📊 Sample Output

```
TOP 25 RANKED RESUMES

   resume                  score   rank
0  Rahul_Sharma.pdf        87.40   1
1  Priya_Gupta.docx        83.15   2
2  Arjun_Verma.pdf         79.60   3
3  Sneha_Patel.docx        76.20   4
4  Kiran_Mehta.pdf         74.85   5
...
```

A horizontal bar chart is auto-generated showing the Top 25 scores visually.

<br/>

![-----](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 📁 Project Structure

```
resumerank-ai/
│
├── resume_ranker.py       # Main pipeline script
├── README.md              # This file
├── requirements.txt       # Python dependencies
│
└── resumes/               # Place input resumes here
    ├── candidate1.pdf
    ├── candidate2.docx
    └── ...
```

<br/>

![-----](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## 👥 Team

<div align="center">

| Member | Role |
|---|---|
| 👤 Member 1 | Lead Developer & Pipeline Architect |
| 👤 Member 2 | REGEX & Extraction Logic |
| 👤 Member 3 | Scoring Engine & Normalization |
| 👤 Member 4 | Testing, Visualization & Documentation |

*Built with ❤️ at **ABES Engineering College** for **Smart ABES Hackathon 2025***

</div>

<br/>

![-----](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

<div align="center">

**⭐ Star this repo if you found it useful!**

`SAH 2025` · `Problem AI-PS-1` · `ABES Engineering College` · `AI & Talent Acquisition`

</div>
