from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sqlite3
import json
import os
import math
import requests
from typing import Any
from PIL import Image
from fastapi.staticfiles import StaticFiles
from model import predict_career
DB_NAME = "career_recommendation.db"
OUTPUT_DIR = "generated_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(title="Career Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/generated_outputs", StaticFiles(directory="generated_outputs"), name="generated_outputs")
def get_conn():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


class Student(BaseModel):
    branch: str
    year: int
    cgpa: float
    interest_id: int
    skill_ratings: list[int] = Field(default_factory=list)
    months: int = 6


class RatingInput(BaseModel):
    user_id: int
    career_id: int
    rating: int = Field(ge=1, le=5)
    feedback: str = ""


RESOURCE_LIBRARY = {
    "Programming": {
        "free": ["freeCodeCamp Python / JavaScript courses", "Harvard CS50"],
        "paid": ["Udemy Python Bootcamp", "Coursera Programming Specialization"],
        "youtube": ["CodeWithHarry", "Apna College"]
    },
    "Data Analysis": {
        "free": ["Kaggle Learn: Python and Pandas", "Google Data Analytics sample resources"],
        "paid": ["Coursera Google Data Analytics", "DataCamp tracks"],
        "youtube": ["Krish Naik", "CampusX"]
    },
    "Machine Learning": {
        "free": ["Andrew Ng ML (audit)", "Google ML Crash Course"],
        "paid": ["Coursera Machine Learning Specialization", "Udemy ML practical courses"],
        "youtube": ["Krish Naik", "Sentdex"]
    },
    "Cybersecurity": {
        "free": ["TryHackMe free rooms", "Cisco cybersecurity introduction"],
        "paid": ["Coursera Cybersecurity certificates", "Udemy ethical hacking courses"],
        "youtube": ["NetworkChuck", "HackerSploit"]
    },
    "Cloud Computing": {
        "free": ["AWS Skill Builder free courses", "Microsoft Learn Azure fundamentals"],
        "paid": ["A Cloud Guru", "Coursera cloud tracks"],
        "youtube": ["TechWorld with Nana", "freeCodeCamp cloud playlists"]
    },
    "UI/UX Design": {
        "free": ["Google UX Design basics", "Figma community tutorials"],
        "paid": ["Coursera Google UX Design", "Interaction Design Foundation"],
        "youtube": ["DesignCourse", "Jesse Showalter"]
    },
    "Product Strategy": {
        "free": ["Product School blogs", "Lenny's newsletter samples"],
        "paid": ["Reforge programs", "Coursera product management tracks"],
        "youtube": ["PM School", "Shreyas Doshi talks"]
    },
    "Legal Reasoning": {
        "free": ["Bar and Bench articles", "Legal Eagle introductions"],
        "paid": ["LawSikho courses", "online LLB prep modules"],
        "youtube": ["LegalEdge", "Study IQ law content"]
    },
    "Biotechnology": {
        "free": ["NPTEL biotech courses", "MIT OpenCourseWare biology"],
        "paid": ["Coursera biotech specializations", "edX life sciences tracks"],
        "youtube": ["Shomu's Biology", "NPTEL official"]
    },
    "Sustainability": {
        "free": ["UNEP learning resources", "NPTEL sustainable engineering"],
        "paid": ["Coursera sustainability specializations", "edX climate courses"],
        "youtube": ["Our Changing Climate", "NPTEL official"]
    },
    "Research": {
        "free": ["Google Scholar tutorials", "OpenLearn research methods"],
        "paid": ["Coursera research methods", "edX data/research tracks"],
        "youtube": ["NPTEL research lectures", "Research method channels"]
    }
}


# =========================
# PHASE 1: DATA RETRIEVAL
# =========================
def fetch_career_bundle(cur, career_id: int, selected_interest_id: int | None = None):
    cur.execute("""
        SELECT career_id, career_name, description, avg_salary
        FROM CAREERS
        WHERE career_id = ?
    """, (career_id,))
    career_row = cur.fetchone()

    if not career_row:
        return None

    cur.execute("""
        SELECT sub.subject_id, sub.subject_name
        FROM CAREER_SUBJECTS cs
        JOIN SUBJECTS sub ON cs.subject_id = sub.subject_id
        WHERE cs.career_id = ?
        ORDER BY sub.subject_id
    """, (career_id,))
    subjects = [{"id": r["subject_id"], "name": r["subject_name"]} for r in cur.fetchall()]

    cur.execute("""
        SELECT s.skill_id, s.skill_name
        FROM CAREER_SKILLS cs
        JOIN SKILLS s ON cs.skill_id = s.skill_id
        WHERE cs.career_id = ?
        ORDER BY s.skill_id
    """, (career_id,))
    skills = [{"id": r["skill_id"], "name": r["skill_name"]} for r in cur.fetchall()]

    cur.execute("""
        SELECT i.interest_id, i.interest_name
        FROM CAREER_INTERESTS ci
        JOIN INTERESTS i ON ci.interest_id = i.interest_id
        WHERE ci.career_id = ?
        ORDER BY i.interest_id
    """, (career_id,))
    interests = [{"id": r["interest_id"], "name": r["interest_name"]} for r in cur.fetchall()]

    cur.execute("""
        SELECT course_name, platform, link, level, duration
        FROM COURSES
        WHERE career_id = ?
        ORDER BY course_id
    """, (career_id,))
    courses = [
        {
            "name": r["course_name"],
            "platform": r["platform"],
            "link": r["link"],
            "level": r["level"],
            "duration": r["duration"]
        }
        for r in cur.fetchall()
    ]

    interest_ids = {item["id"] for item in interests}
    interest_match = selected_interest_id in interest_ids if selected_interest_id is not None else False

    return {
        "career_id": career_row["career_id"],
        "career_name": career_row["career_name"],
        "description": career_row["description"],
        "avg_salary": career_row["avg_salary"],
        "subjects_required": subjects,
        "skills_required": skills,
        "career_interests": interests,
        "courses": courses,
        "interest_match": interest_match
    }


# =========================
# PHASE 2: FEATURE/LEVEL LOGIC
# =========================
def classify_level(skill_ratings: list[int]) -> str:
    if not skill_ratings:
        return "Beginner"

    avg = sum(skill_ratings) / len(skill_ratings)

    if avg >= 4.0:
        return "Advanced"
    if avg >= 2.5:
        return "Intermediate"
    return "Beginner"


# =========================
# PHASE 3: SKILL GAP ANALYSIS
# =========================
def compute_skill_diagnosis(skill_names: list[str], ratings: list[int]):
    skill_gap = []
    strong_skills = []
    weak_skills = []

    for idx, skill_name in enumerate(skill_names):
        rating = ratings[idx] if idx < len(ratings) else 3
        if rating >= 4:
            level = "Advanced"
            strong_skills.append(skill_name)
        elif rating >= 3:
            level = "Intermediate"
        else:
            level = "Beginner"

        if rating <= 2:
            weak_skills.append(skill_name)

        skill_gap.append({
            "skill": skill_name,
            "rating": rating,
            "level": level
        })

    return skill_gap, strong_skills, weak_skills


# =========================
# PHASE 4: RESOURCE MATCHING
# =========================
def lookup_course_resources(skills: list[str]):
    resources = []
    seen = set()

    for skill in skills:
        if skill in RESOURCE_LIBRARY and skill not in seen:
            seen.add(skill)
            resources.append({
                "skill": skill,
                "free": RESOURCE_LIBRARY[skill]["free"],
                "paid": RESOURCE_LIBRARY[skill]["paid"],
                "youtube": RESOURCE_LIBRARY[skill]["youtube"]
            })

    return resources


# =========================
# PHASE 5: ROADMAP PLANNING
# =========================
def build_monthly_roadmap(
    career_name: str,
    level: str,
    months: int,
    weak_skills: list[str],
    strong_skills: list[str],
    subject_names: list[str],
    resource_items: list[dict[str, Any]]
):
    months = max(1, int(months))
    phase_1 = max(1, math.ceil(months * 0.3))
    phase_2 = max(1, math.ceil(months * 0.4))
    phase_3 = max(1, months - phase_1 - phase_2)

    if phase_1 + phase_2 + phase_3 > months:
        phase_3 = max(1, months - phase_1 - phase_2)

    roadmap = []
    roadmap.append(f"Career target: {career_name}")
    roadmap.append(f"Current level: {level}")
    roadmap.append(f"Preparation duration: {months} months")
    roadmap.append("")
    roadmap.append("Phase 1: Foundation")
    roadmap.append(f"Duration: {phase_1} month(s)")
    roadmap.append("- Build basics in the required subjects and tools.")
    roadmap.append(f"- Focus weak skills: {', '.join(weak_skills) if weak_skills else 'None'}")
    roadmap.append(f"- Subjects to revise: {', '.join(subject_names) if subject_names else 'None'}")
    roadmap.append("")

    roadmap.append("Phase 2: Skill building")
    roadmap.append(f"Duration: {phase_2} month(s)")
    roadmap.append("- Practice with small projects and mini tasks.")
    roadmap.append("- Strengthen applied problem solving.")
    if strong_skills:
        roadmap.append(f"- Use strong skills as leverage: {', '.join(strong_skills)}")
    roadmap.append("")

    roadmap.append("Phase 3: Portfolio and validation")
    roadmap.append(f"Duration: {phase_3} month(s)")
    roadmap.append("- Build one portfolio-grade project.")
    roadmap.append("- Prepare resume and LinkedIn/GitHub proof.")
    roadmap.append("- Do mock interviews or a practical assessment.")
    roadmap.append("")

    roadmap.append("Suggested resources")
    if resource_items:
        for item in resource_items:
            roadmap.append(f"- {item['skill']}:")
            roadmap.append(f"  Free: {item['free'][0] if item['free'] else 'N/A'}")
            roadmap.append(f"  Paid: {item['paid'][0] if item['paid'] else 'N/A'}")
            roadmap.append(f"  YouTube: {item['youtube'][0] if item['youtube'] else 'N/A'}")
    else:
        roadmap.append("- No matching resource library found. Add this skill to RESOURCE_LIBRARY.")

    roadmap.append("")
    roadmap.append("Final checkpoint")
    roadmap.append("- Can you explain the career, solve a small problem, and show a project?")
    return "\n".join(roadmap)


# =========================
# PHASE 6: LLM COURSE GENERATION
# =========================
def generate_courses_llm(career: str, skills: list[str], level: str):
    prompt = f"""
You are an expert AI career mentor.

Career: {career}
Level: {level}
Skills: {", ".join(skills)}

Suggest 6 HIGH QUALITY courses:
- 2 YouTube
- 2 Coursera
- 2 Udemy

Return STRICT JSON only:
[
  {{
    "name": "...",
    "platform": "...",
    "link": "...",
    "level": "Beginner|Intermediate|Advanced",
    "reason": "..."
  }}
]

Rules:
- Prefer real, widely used courses
- Keep links valid
- Do not include markdown
- Do not include extra text
"""

    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False},
            timeout=60
        )
        raw = res.json().get("response", "[]").strip()
        return json.loads(raw)
    except Exception:
        return []


# =========================
# PHASE 7: STEGANOGRAPHY
# =========================
def create_cover_image(path: str, width: int = 1024, height: int = 1024):
    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    image.save(path, format="PNG")


def _to_bits(data: bytes):
    for byte in data:
        for i in range(7, -1, -1):
            yield (byte >> i) & 1


def encode_payload_to_image(payload: dict, output_path: str, cover_path: str | None = None):
    if cover_path and os.path.exists(cover_path):
        img = Image.open(cover_path).convert("RGB")
    else:
        cover_path = os.path.join(OUTPUT_DIR, "cover.png")
        create_cover_image(cover_path)
        img = Image.open(cover_path).convert("RGB")

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    length_prefix = len(data).to_bytes(4, byteorder="big")
    full_bytes = length_prefix + data
    bits = list(_to_bits(full_bytes))

    pixels = list(img.getdata())
    capacity = len(pixels) * 3
    if len(bits) > capacity:
        raise ValueError("Payload too large for the selected image.")

    new_pixels = []
    bit_idx = 0

    for r, g, b in pixels:
        rgb = [r, g, b]
        for ch in range(3):
            if bit_idx < len(bits):
                rgb[ch] = (rgb[ch] & 0xFE) | bits[bit_idx]
                bit_idx += 1
        new_pixels.append(tuple(rgb))

    encoded = Image.new(img.mode, img.size)
    encoded.putdata(new_pixels)
    encoded.save(output_path, format="PNG")
    return output_path


def decode_payload_from_image(image_path: str):
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())

    bits = []
    for r, g, b in pixels:
        bits.extend([r & 1, g & 1, b & 1])

    bytes_out = bytearray()
    for i in range(0, len(bits), 8):
        chunk = bits[i:i + 8]
        if len(chunk) < 8:
            break
        byte = 0
        for bit in chunk:
            byte = (byte << 1) | bit
        bytes_out.append(byte)

    if len(bytes_out) < 4:
        raise ValueError("Invalid steganography payload.")

    data_len = int.from_bytes(bytes_out[:4], byteorder="big")
    payload_bytes = bytes_out[4:4 + data_len]
    return json.loads(payload_bytes.decode("utf-8"))


# =========================
# API: META
# =========================
@app.get("/meta")
def get_meta():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT interest_id, interest_name FROM INTERESTS ORDER BY interest_id")
    interests = [{"id": row["interest_id"], "name": row["interest_name"]} for row in cur.fetchall()]

    cur.execute("SELECT skill_id, skill_name FROM SKILLS ORDER BY skill_id")
    skills = [{"id": row["skill_id"], "name": row["skill_name"]} for row in cur.fetchall()]

    cur.execute("SELECT career_id, career_name FROM CAREERS ORDER BY career_id")
    careers = [{"id": row["career_id"], "name": row["career_name"]} for row in cur.fetchall()]

    conn.close()

    return {
        "interests": interests,
        "skills": skills,
        "careers": careers,
        "branches": [
            "Computer Science",
            "Electronics",
            "Mechanical",
            "Civil",
            "Commerce",
            "Arts",
            "Science"
        ]
    }


# =========================
# API: PREDICT
# =========================
@app.post("/predict")
def predict(student: Student):
    top3_ids, confidences = predict_career(student)

    conn = get_conn()
    cur = conn.cursor()

    results = []

    for cid, conf in zip(top3_ids, confidences):
        bundle = fetch_career_bundle(cur, cid, student.interest_id)
        if not bundle:
            continue

        results.append({
            "career_id": bundle["career_id"],
            "career_name": bundle["career_name"],
            "description": bundle["description"],
            "confidence": conf,
            "avg_salary": bundle["avg_salary"],
            "subjects_required": [x["name"] for x in bundle["subjects_required"]],
            "skills_required": [x["name"] for x in bundle["skills_required"]],
            "career_interests": bundle["career_interests"],
            "courses": bundle["courses"],
            "interest_match": bundle["interest_match"]
        })

    conn.close()
    return {"recommendations": results}


# =========================
# API: CAREER DETAILS
# =========================
@app.post("/career-details")
def career_details(data: dict):
    career_id = data["career_id"]

    conn = get_conn()
    cur = conn.cursor()
    bundle = fetch_career_bundle(cur, career_id)
    conn.close()

    if not bundle:
        return {"error": "Career not found"}

    return bundle


# =========================
# API: ROADMAP + COURSES + STEGO
# =========================
@app.post("/generate-roadmap")
def generate_roadmap_endpoint(data: dict):
    conn = get_conn()
    cur = conn.cursor()

    career_id = data["career_id"]
    ratings = data.get("skill_ratings", [])
    months = int(data.get("months", 6))
    branch = data.get("branch", "Computer Science")
    year = int(data.get("year", 1))
    cgpa = float(data.get("cgpa", 0.0))
    interest_id = data.get("interest_id")

    cur.execute("SELECT interest_name FROM INTERESTS WHERE interest_id = ?", (interest_id,))
    interest_row = cur.fetchone()
    interest_name = interest_row["interest_name"] if interest_row else "Unknown"

    bundle = fetch_career_bundle(cur, career_id, interest_id)
    if not bundle:
        conn.close()
        return {"error": "Career not found"}

    skill_names = [s["name"] for s in bundle["skills_required"]]
    subject_names = [s["name"] for s in bundle["subjects_required"]]

    # Phase 3
    skill_gap, strong_skills, weak_skills = compute_skill_diagnosis(skill_names, ratings)
    level = classify_level(ratings)

    # Phase 4
    resource_items = lookup_course_resources(weak_skills if weak_skills else skill_names)
    # Skill gap score
    gap_score = sum([5 - r for r in ratings]) if ratings else 0
    if gap_score <= 5:
        readiness = "High (Industry Ready)"
    elif gap_score <= 10:
        readiness = "Moderate (Needs Improvement)"
    else:
        readiness = "Low (Foundation Required)"
    # Phase 5
    roadmap = build_monthly_roadmap(
        career_name=bundle["career_name"],
        level=level,
        months=months,
        weak_skills=weak_skills,
        strong_skills=strong_skills,
        subject_names=subject_names,
        resource_items=resource_items
    )

    # Phase 6
    llm_courses = generate_courses_llm(
        career=bundle["career_name"],
        skills=weak_skills if weak_skills else skill_names,
        level=level
    )

    merged_courses = bundle["courses"] + llm_courses

    # Phase 7
    payload = {
    "career": bundle["career_name"],
    "level": level,
    "months": months,
    "cgpa": cgpa,
    "branch": branch,
    "interest": interest_name,
    "gap_score": gap_score,
    "weak_skills": weak_skills,
    "strong_skills": strong_skills
}

    stego_path = os.path.join(OUTPUT_DIR, f"secure_report_{career_id}.png")
    encode_payload_to_image(payload, stego_path)

    conn.close()

    return {
        "career": bundle["career_name"],
        "level": level,
        "skill_gap": skill_gap,
        "weak_skills": weak_skills,
        "strong_skills": strong_skills,
        "roadmap": roadmap,
        "months": months,
        "avg_salary": bundle["avg_salary"],
        "skill_count": len(skill_names),
        "course_count": len(merged_courses),
        "subjects_required": subject_names,
        "readiness": readiness,
        "gap_score": gap_score,
        "career_interests": [i["name"] for i in bundle["career_interests"]],
        "courses": merged_courses,
        "courses_db": bundle["courses"],
        "courses_llm": llm_courses,
        "resource_recommendations": resource_items,
        "stego_image": stego_path,
        "why_this": f"""
Recommended because:
- Branch: {branch}
- Year: {year}
- CGPA: {cgpa}
- Interest: {interest_name}
- Strong skills: {', '.join(strong_skills) if strong_skills else 'None'}
""".strip(),
        "why_not": "Other careers were less suitable due to weaker skill alignment or weaker interest overlap."
    }


# =========================
# API: RATING FEEDBACK
# =========================
@app.post("/rate")
def rate_career(data: RatingInput):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO RATINGS (user_id, career_id, rating, feedback)
        VALUES (?, ?, ?, ?)
    """, (data.user_id, data.career_id, data.rating, data.feedback))

    conn.commit()
    conn.close()
    return {"message": "Rating saved successfully"}


# =========================
# API: STEGO DECODE
# =========================
@app.post("/stego/decode")
async def decode_stego(file: UploadFile = File(...)):
    temp_path = os.path.join(OUTPUT_DIR, f"upload_{file.filename}")
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        payload = decode_payload_from_image(temp_path)
        return {"status": "success", "payload": payload}
    except Exception as e:
        return {"status": "error", "detail": str(e)}