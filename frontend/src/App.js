import { useEffect, useMemo, useState } from "react";
import "./App.css";

function App() {
  const [step, setStep] = useState("input");

  const [form, setForm] = useState({
    branch: "Computer Science",
    year: 1,
    cgpa: "",
    interest_id: 1
  });

  const [meta, setMeta] = useState({ interests: [], skills: [] });
  const [predictions, setPredictions] = useState([]);
  const [selectedCareer, setSelectedCareer] = useState(null);

  const [skillRatings, setSkillRatings] = useState([]);
  const [months, setMonths] = useState(3);

  const [fullResult, setFullResult] = useState(null);
  const [roadmap, setRoadmap] = useState("");
  const [ratingData, setRatingData] = useState({});

  const [decodedData, setDecodedData] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  // ================= FETCH META =================
  useEffect(() => {
    fetch("http://127.0.0.1:8000/meta")
      .then((res) => res.json())
      .then((data) => setMeta(data));
  }, []);

  const updateForm = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  // ================= PREDICT =================
  const handlePredict = async () => {
    const res = await fetch("http://127.0.0.1:8000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...form,
        cgpa: parseFloat(form.cgpa) || 0,
        skill_ratings: []
      })
    });

    const data = await res.json();
    setPredictions(data.recommendations);
    setStep("careers");
  };

  // ================= SELECT CAREER =================
  const chooseCareer = (career) => {
    setSelectedCareer(career);
    setSkillRatings(Array(career.skills_required.length).fill(3));
    setStep("rate");
  };

  // ================= SKILL RATING =================
  const updateSkillRating = (index, value) => {
    const updated = [...skillRatings];
    updated[index] = parseInt(value);
    setSkillRatings(updated);
  };

  // ================= GENERATE ROADMAP =================
  const handleGenerateRoadmap = async () => {
    const res = await fetch("http://127.0.0.1:8000/generate-roadmap", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        career_id: selectedCareer.career_id,
        branch: form.branch,
        year: form.year,
        cgpa: parseFloat(form.cgpa) || 0,
        interest_id: form.interest_id,
        months: parseInt(months),
        skill_ratings: skillRatings
      })
    });

    const data = await res.json();
    setFullResult(data);
    setRoadmap(data.roadmap);
    setStep("roadmap");
  };

  // ================= DOWNLOAD IMAGE =================
  const downloadImage = async () => {
    const res = await fetch(
      `http://127.0.0.1:8000/${fullResult.stego_image}`
    );
    const blob = await res.blob();

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "secure_report.png";
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  // ================= DECODE =================
  const decodeStego = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);

    const res = await fetch("http://127.0.0.1:8000/stego/decode", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    setDecodedData(data.payload || data);
  };

  // ================= RESET =================
  const resetAll = () => {
    setStep("input");
    setPredictions([]);
    setSelectedCareer(null);
    setFullResult(null);
    setDecodedData(null);
  };

  const selectedSkills = useMemo(
    () => selectedCareer?.skills_required || [],
    [selectedCareer]
  );

  return (
    <div className="container">
      <h2>AI Career Recommendation System</h2>

      {/* ================= STEP 1 ================= */}
      {step === "input" && (
        <>
          <input
            placeholder="CGPA"
            value={form.cgpa}
            onChange={(e) => updateForm("cgpa", e.target.value)}
          />

          <select
            value={form.branch}
            onChange={(e) => updateForm("branch", e.target.value)}
          >
            <option>Computer Science</option>
            <option>Electronics</option>
            <option>Mechanical</option>
            <option>Civil</option>
          </select>

          <select
            value={form.year}
            onChange={(e) => updateForm("year", parseInt(e.target.value))}
          >
            <option value="1">1st Year</option>
            <option value="2">2nd Year</option>
            <option value="3">3rd Year</option>
            <option value="4">4th Year</option>
          </select>

          <select
            value={form.interest_id}
            onChange={(e) =>
              updateForm("interest_id", parseInt(e.target.value))
            }
          >
            {meta.interests.map((i) => (
              <option key={i.id} value={i.id}>
                {i.name}
              </option>
            ))}
          </select>

          <button onClick={handlePredict}>Predict</button>
        </>
      )}

      {/* ================= STEP 2 ================= */}
      {step === "careers" && (
        <>
          {predictions.map((rec, i) => (
            <div key={i} className="card">
              <h3>{rec.career_name}</h3>
              <p>{rec.description}</p>
              <p>Confidence: {rec.confidence}%</p>

              <button onClick={() => chooseCareer(rec)}>Choose</button>
            </div>
          ))}
          <button onClick={resetAll}>Back</button>
        </>
      )}

      {/* ================= STEP 3 ================= */}
      {step === "rate" && (
        <>
          <h3>{selectedCareer.career_name}</h3>

          {selectedSkills.map((skill, i) => (
            <div key={i}>
              {skill}
              <input
                type="range"
                min="1"
                max="5"
                value={skillRatings[i]}
                onChange={(e) => updateSkillRating(i, e.target.value)}
              />
            </div>
          ))}

          <input
            type="number"
            value={months}
            onChange={(e) => setMonths(e.target.value)}
          />

          <button onClick={handleGenerateRoadmap}>
            Generate Roadmap
          </button>
        </>
      )}

      {/* ================= STEP 4 ================= */}
      {step === "roadmap" && fullResult && (
        <>
          <h3>{fullResult.career}</h3>
          <h4>Level: {fullResult.level}</h4>
          <h4>Readiness: {fullResult.readiness}</h4>

          <pre>{roadmap}</pre>

          {/* COURSES */}
          <h4>Courses</h4>
          <ul>
            {fullResult.courses?.map((c, i) => (
              <li key={i}>
                <a href={c.link} target="_blank" rel="noreferrer">
                  {c.name}
                </a>{" "}
                ({c.platform})
              </li>
            ))}
          </ul>

          {/* STEGO IMAGE */}
          <h4>🔒 Secure Report</h4>
          <img
            src={`http://127.0.0.1:8000/${fullResult.stego_image}`}
            width="300"
            alt="stego"
          />

          <button onClick={downloadImage}>
            Download Secure Report
          </button>

          {/* DECODE */}
          <h4>Decode Secure Image</h4>

          <input
            type="file"
            accept="image/png"
            onChange={(e) => setSelectedFile(e.target.files[0])}
          />

          <button onClick={decodeStego}>Decode</button>

          {decodedData && (
            <div>
              <h3>Decoded Data</h3>
              <p><b>Career:</b> {decodedData.career}</p>
              <p><b>Level:</b> {decodedData.level}</p>
              <p><b>Months:</b> {decodedData.months}</p>
              <p>
                <b>Weak Skills:</b>{" "}
                {decodedData.weak_skills?.join(", ")}
              </p>
            </div>
          )}

          <button onClick={resetAll}>Restart</button>
        </>
      )}
    </div>
  );
}
export default App;