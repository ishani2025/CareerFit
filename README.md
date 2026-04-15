# 🚀 CareerFit — AI Career Intelligence System with Secure Steganographic Reports

## 📌 Overview

CareerFit is a full-stack AI system that predicts optimal career paths based on user inputs such as CGPA, interests, branch, and academic year.

It combines:

* Machine Learning (career prediction)
* Rule-based intelligence (domain alignment)
* LLM integration (course recommendations)
* Steganography (secure report encoding & decoding)

The system generates a **personalized career roadmap** and embeds it inside an image for **secure, tamper-resistant sharing**.

---

## 🧠 Key Features

### 🔹 Hybrid AI Prediction Engine

* Random Forest model + rule-based boosting
* Outputs **Top 3 career paths with confidence scores**
* Avoids unrealistic 100% predictions

### 🔹 Skill Gap Analysis

* Compares user profile with career requirements
* Identifies missing skills

### 🔹 Roadmap Generation

* Beginner → Intermediate → Advanced progression
* Structured learning path

### 🔹 LLM-Based Course Recommendations

* Dynamically fetches courses from:

  * YouTube
  * Coursera
  * Udemy
* Context-aware suggestions

### 🔹 🔐 Secure Report (Core Innovation)

* Converts roadmap into JSON
* Embeds data into image using steganography
* Enables:

  * Secure sharing
  * Tamper resistance
  * Reversible decoding

---

## 🏗️ System Architecture

```text
User Input (Frontend - React)
        ↓
FastAPI Backend
        ↓
ML Model (Prediction Engine)
        ↓
Skill Gap + Roadmap Generator
        ↓
LLM (Course Recommendation)
        ↓
Steganography Encoder
        ↓
Secure Image Output
```

---

## 🛠️ Tech Stack

### Frontend

* React.js
* Axios
* CSS

### Backend

* FastAPI (Python)
* Pydantic
* Uvicorn

### AI/ML

* Scikit-learn (Random Forest)
* Feature engineering + hybrid inference

### Security Layer

* PIL (Python Imaging Library)
* Steganography (LSB encoding)

### LLM Integration

* Local LLM (Ollama / API-based)

---

## 📂 Project Structure

```text
CareerFit/
│
├── backend/
│   ├── main.py
│   ├── model.py
│   ├── database.py
│   └── steganography.py
│
├── frontend/
│   ├── src/
│   └── public/
│
├── .gitignore
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

```bash
git clone https://github.com/ishani2025/CareerFit.git
cd CareerFit
```

---

### 2️⃣ Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

---

### 3️⃣ Frontend Setup

```bash
cd frontend
npm install
npm start
```

---

## 🔐 Secure Report Workflow

### Encode

* Generate career roadmap
* Convert to JSON
* Embed inside image

### Decode

* Upload image
* Extract hidden JSON
* Display report

---

## 📸 Example Use Cases

* 🎓 Student career guidance systems
* 🏥 Secure medical report sharing
* 🪪 Digital identity verification
* 🏢 Enterprise AI insight protection

---

## 🚀 Future Enhancements

* Model training on real datasets (Kaggle integration)
* Explainable AI (feature importance)
* Encryption + checksum validation
* Deployment (Docker + Cloud)
* Multi-user authentication system

---

## 🧠 Key Innovation

> This project integrates AI decision-making with steganographic security, ensuring that generated insights are not only intelligent but also securely transferable and tamper-resistant.

---

## 👩‍💻 Author

**Ishani Ghosh,Vanshika Jaswani,Srija Dey**
B.Tech CSE — VIT Chennai

---

## ⭐ Contribution

Open to improvements, ideas, and collaborations.

---

## 📜 License

MIT License
