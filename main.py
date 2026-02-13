import os
import re
import pdfplumber
import docx
import spacy
import pandas as pd
import matplotlib.pyplot as plt

nlp = spacy.load("en_core_web_sm")

#Config
SKILLS_DB = [
    "python", "java", "sql", "machine learning",
    "deep learning", "html", "css", "javascript",
    "react", "node", "c++", "pandas", "numpy"
]

WEIGHTS = {
    "internship": 20,
    "skills": 20,
    "projects": 15,
    "cgpa": 10,
    "achievements": 10,
    "experience": 5,
    "extracurricular": 5,
    "language": 3,
    "online_presence": 3,
    "degree": 3,
    "school_marks": 2
}

MAX_SCORE = 100

#File reading
def extract_text_from_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text

def extract_text_from_docx(path):
    doc = docx.Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

def read_resume(path):
    if path.endswith(".pdf"):
        return extract_text_from_pdf(path)
    elif path.endswith(".docx"):
        return extract_text_from_docx(path)
    return ""

#Cleaning
def clean_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text

#Bias reduction (Novelty)
def remove_sensitive_information(text):

    sensitive_patterns = [
        r"\b(male|female|he|she|him|her)\b",
        r"\b(age\s*\d+)\b",
        r"\b(dob|date of birth)\b.*",
        r"\b(photo|photograph)\b",
        r"\b(religion|caste|married)\b"
    ]

    for pattern in sensitive_patterns:
        text = re.sub(pattern, "", text)

    return text

#CGPA extraction(Novelty)
def extract_raw_cgpa(text):

    match_10 = re.search(r"(\d+\.?\d*)\s*/\s*10", text)
    if match_10:
        return float(match_10.group(1))

    match_4 = re.search(r"(\d+\.?\d*)\s*/\s*4", text)
    if match_4:
        return (float(match_4.group(1)) / 4) * 10

    match_percent = re.search(r"(\d+\.?\d*)\s*%", text)
    if match_percent:
        return float(match_percent.group(1)) / 10

    match_plain = re.search(r"(cgpa|gpa)[^\d]*(\d+\.?\d*)", text)
    if match_plain:
        value = float(match_plain.group(2))
        if value <= 10:
            return value

    return None

#Extraction
def extract_info(text):

    data = {}

    #Skills
    skills_found = []
    for skill in SKILLS_DB:
        if re.search(rf"\b{re.escape(skill)}\b", text):
            skills_found.append(skill)
    data["skills"] = skills_found

    #Experience
    exp_match = re.search(r"(\d+)\+?\s*(years|yrs)", text)
    data["experience"] = int(exp_match.group(1)) if exp_match else 0

    #Internship
    data["internship"] = 1 if re.search(r"\bintern(ship)?\b", text) else 0

    #Projects
    data["projects"] = len(re.findall(r"\bproject\b", text))

    #Achievements
    data["achievements"] = len(re.findall(r"\b(award|achievement|winner)\b", text))

    #Degree
    data["degree"] = 1 if re.search(r"(b\.?tech|m\.?tech|mba|phd)", text) else 0

    #School marks
    data["school_marks"] = 1 if "12th" in text else 0

    # Extra curricular
    data["extracurricular"] = len(re.findall(r"\b(volunteer|club|sports|leader)\b", text))

    #Language
    languages = ["english", "hindi", "spanish", "french", "german"]
    data["language"] = sum(1 for lang in languages if lang in text)

    #Online presence
    data["online_presence"] = 1 if re.search(r"(linkedin\.com|github\.com)", text) else 0

    #CGPA
    data["raw_cgpa"] = extract_raw_cgpa(text)

    return data

#Scoring
def calculate_score(data, normalized_cgpa):

    breakdown = {}

    breakdown["internship"] = WEIGHTS["internship"] if data["internship"] else 0
    breakdown["skills"] = min(len(data["skills"]) * 2, WEIGHTS["skills"])
    breakdown["projects"] = min(data["projects"] * 3, WEIGHTS["projects"])
    breakdown["cgpa"] = normalized_cgpa * WEIGHTS["cgpa"]
    breakdown["achievements"] = min(data["achievements"] * 2, WEIGHTS["achievements"])
    breakdown["experience"] = min(data["experience"] * 2, WEIGHTS["experience"])
    breakdown["extracurricular"] = min(data["extracurricular"], WEIGHTS["extracurricular"])
    breakdown["language"] = min(data["language"], WEIGHTS["language"])
    breakdown["online_presence"] = WEIGHTS["online_presence"] if data["online_presence"] else 0
    breakdown["degree"] = WEIGHTS["degree"] if data["degree"] else 0
    breakdown["school_marks"] = WEIGHTS["school_marks"] if data["school_marks"] else 0

    total = sum(breakdown.values())
    total = (total / sum(WEIGHTS.values())) * MAX_SCORE

    return round(total, 2), breakdown

#Main pipeline

def main():

    folder_path = input("Enter resume folder path: ")
    results = []

    #First pass:extract data
    for file in os.listdir(folder_path):

        path = os.path.join(folder_path, file)
        text = read_resume(path)

        if not text:
            continue

        text = clean_text(text)
        text = remove_sensitive_information(text)

        data = extract_info(text)

        results.append({
            "resume": file,
            "data": data
        })

    #CGPA dataset normalization
    raw_cgpas = [r["data"]["raw_cgpa"] for r in results if r["data"]["raw_cgpa"] is not None]

    min_cgpa = min(raw_cgpas) if raw_cgpas else 0
    max_cgpa = max(raw_cgpas) if raw_cgpas else 10

    #Second pass:scoring
    final_results = []

    for r in results:

        cgpa = r["data"]["raw_cgpa"]

        if cgpa is not None and max_cgpa != min_cgpa:
            normalized_cgpa = (cgpa - min_cgpa) / (max_cgpa - min_cgpa)
        else:
            normalized_cgpa = 0

        score, breakdown = calculate_score(r["data"], normalized_cgpa)

        final_results.append({
            "resume": r["resume"],
            "score": score,
            "breakdown": breakdown
        })

    df = pd.DataFrame(final_results)
    df = df.sort_values(by="score", ascending=False).reset_index(drop=True)
    df["rank"] = range(1, len(df) + 1)

    print("\nTOP 25 RANKED RESUMES\n")
    print(df[["resume", "score", "rank"]].head(25))

    #Visualisation
    top25 = df.head(25)
    plt.figure(figsize=(12, 8))
    plt.barh(top25["resume"], top25["score"], color="skyblue")
    plt.xlabel("Score")
    plt.ylabel("Resume")
    plt.title("Top 25 Resume Rankings")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
    
if __name__ == "__main__":
    main()
