/**
 * GrowPath AI - Frontend Core Script
 * Comprehensive handling for Resume Upload, ATS Analysis, JD Match,
 * Live Jobs, AI Bullet Optimizer, and Interview Prep.
 */

// Global State
const GrowPath = {
  activeTab: "overview",
  resumeData: null,
  atsAnalysis: null,
  extractedSkills: [],
  targetRole: "Software Engineer"
};

// =====================================================================
// Sample Resume Data for Quick Testing
// =====================================================================
const SAMPLE_RESUME_TEXT = `Alex Johnson
alex.johnson.dev@gmail.com | +1 (555) 234-5678 | linkedin.com/in/alexjohnson-dev | github.com/alexjohnson-dev
San Francisco, CA

PROFESSIONAL SUMMARY
Results-driven Full Stack Software Engineer with 3+ years of experience designing, developing, and deploying scalable web applications and distributed backend microservices. Proven track record in Python, TypeScript, React, and cloud architectures.

TECHNICAL SKILLS
• Programming Languages: Python, JavaScript, TypeScript, Go, SQL, C++
• Frontend: React.js, Next.js, HTML5, CSS3, Tailwind CSS, Redux Toolkit
• Backend & APIs: FastAPI, Node.js, Express.js, Django, RESTful APIs, GraphQL
• Databases & Caching: PostgreSQL, MongoDB, Redis, SQLite
• Cloud & DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes, CI/CD (GitHub Actions), Linux, Nginx
• Tools & Methodologies: Git, GitHub, Postman, Jest, PyTest, Agile/Scrum

PROFESSIONAL EXPERIENCE
Senior Full Stack Developer | Apex Tech Solutions (2022 - Present)
• Architected and deployed scalable RESTful APIs using FastAPI and PostgreSQL, reducing query latency by 45% across 250,000+ daily requests.
• Spearheaded the frontend migration of core client portal to Next.js and Tailwind CSS, increasing page speed by 38% and user retention by 22%.
• Engineered an automated CI/CD pipeline using GitHub Actions and Docker, cutting deployment cycle times from 4 hours to 12 minutes.
• Mentored 4 junior developers in TypeScript best practices and conducted bi-weekly code reviews.

Software Engineer | CloudScale Innovations (2020 - 2022)
• Developed high-throughput microservices using Node.js and Redis cache, handling over 50,000 concurrent user sessions.
• Implemented OAuth2 and JWT role-based authentication, enhancing platform security and resolving 100% of audit vulnerabilities.
• Collaborated in an Agile Scrum team of 8 engineers, consistently delivering sprint milestones on schedule.

FEATURED PROJECTS
• AI Smart Recruiter: Built an end-to-end resume parser and matching platform utilizing Python, PyTorch, and React.js with 94% parsing accuracy.
• Distributed Task Queue: Created a high-performance distributed task scheduler in Go and Redis with sub-5ms task dispatch latency.

EDUCATION
Bachelor of Science in Computer Science | University of California, Berkeley (2016 - 2020)
• Honors: Dean's Honor List (3 semesters) | GPA: 3.8/4.0

CERTIFICATIONS & AWARDS
• AWS Certified Solutions Architect – Associate (2023)
• 1st Place Winner - Bay Area Hackathon 2022`;

const SAMPLE_JOB_DESCRIPTIONS = {
  fullstack: `Senior Full Stack Developer
Location: Remote / Hybrid
Experience: 3+ years

Job Responsibilities:
• Build, scale, and maintain modern web applications using React.js, Next.js, and TypeScript.
• Design robust backend microservices and RESTful APIs using Python, FastAPI, or Node.js.
• Work with relational databases like PostgreSQL and in-memory caches like Redis.
• Deploy and containerize applications with Docker, Kubernetes, and AWS cloud infrastructure.
• Champion CI/CD automation, code quality, and mentor junior engineers.

Requirements & Qualifications:
• 3+ years of professional full-stack development experience.
• Strong proficiency in React, TypeScript, Python, and SQL.
• Hands-on experience with Docker, AWS (EC2, S3), and Git.
• Excellent communication, problem-solving, and agile collaboration skills.`,

  ai_ml: `AI / Machine Learning Engineer
Location: San Francisco, CA / Remote
Experience: 2+ years

Role Overview:
We are seeking an innovative AI/ML Engineer to build intelligent data pipelines, train machine learning models, and deploy generative AI applications.

Responsibilities:
• Train, fine-tune, and evaluate deep learning models using PyTorch, TensorFlow, and Hugging Face.
• Build scalable inference APIs using Python, FastAPI, and Docker.
• Implement NLP and Large Language Model (LLM) pipelines with LangChain and vector databases.
• Analyze large datasets using Pandas, NumPy, and SQL.

Required Skills:
• Strong Python programming and computer science fundamentals.
• Hands-on experience with PyTorch or TensorFlow and Scikit-Learn.
• Experience with REST APIs, Docker, and AWS.`,

  backend: `Backend Software Engineer (Python / Go)
Location: New York, NY / Remote

Responsibilities:
• Architect high-performance distributed backend services in Python (FastAPI/Django) and Go.
• Optimize PostgreSQL database queries, schemas, and Redis caching layers.
• Build fault-tolerant microservices, message queues, and real-time WebSocket endpoints.
• Implement unit and integration tests with PyTest to maintain 90%+ code coverage.

Requirements:
• Strong backend experience with Python, Go, and PostgreSQL.
• Deep understanding of concurrency, data structures, and system design.
• Proficiency with Docker, Linux, Git, and CI/CD pipelines.`
};

// =====================================================================
// Initialize Page
// =====================================================================
document.addEventListener("DOMContentLoaded", () => {
  setupDragAndDrop();
  checkStoredSession();
});

function checkStoredSession() {
  const storedResume = localStorage.getItem("growpath_resume_text") || localStorage.getItem("resume_text");
  if (storedResume) {
    const resumeBox = document.getElementById("resumeTextBox");
    if (resumeBox) resumeBox.value = storedResume;
  }
}

// =====================================================================
// Drag and Drop & File Upload
// =====================================================================
function setupDragAndDrop() {
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("resumeInput");

  if (!dropZone || !fileInput) return;

  ["dragenter", "dragover"].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.add("border-orange-500", "bg-orange-500/10");
    }, false);
  });

  ["dragleave", "drop"].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove("border-orange-500", "bg-orange-500/10");
    }, false);
  });

  dropZone.addEventListener("drop", (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      fileInput.files = files;
      handleFileSelected(files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });
}

function handleFileSelected(file) {
  const nameEl = document.getElementById("selectedFileName");
  if (nameEl) {
    const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
    nameEl.innerHTML = `📄 <strong>${file.name}</strong> (${sizeMb} MB) — Ready to analyze`;
    nameEl.classList.remove("hidden");
  }
}

// =====================================================================
// Quick Load Sample Resume
// =====================================================================
function loadSampleResume() {
  // Store sample text
  localStorage.setItem("growpath_resume_text", SAMPLE_RESUME_TEXT);
  localStorage.setItem("resume_text", SAMPLE_RESUME_TEXT);

  // Trigger quick analysis directly via mock or API
  showUploadLoading("Loading sample candidate resume (Alex Johnson)...");

  // Create a Blob from sample text to upload as .txt
  const blob = new Blob([SAMPLE_RESUME_TEXT], { type: "text/plain" });
  const file = new File([blob], "Alex_Johnson_Resume.txt", { type: "text/plain" });

  const formData = new FormData();
  formData.append("file", file);

  fetch("/api/upload_and_parse", { method: "POST", body: formData })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        saveAnalysisData(data);
        renderUploadResults(data);
      } else {
        showUploadError(data.error || "Failed to parse sample resume.");
      }
    })
    .catch(err => {
      console.error(err);
      showUploadError("Network error while processing sample resume.");
    });
}

// =====================================================================
// Main Upload and Analyze
// =====================================================================
async function uploadResume() {
  const input = document.getElementById("resumeInput");
  const file = input ? input.files[0] : null;

  if (!file) {
    alert("⚠️ Please choose a PDF or DOCX resume file first (or click 'Try Sample Resume')!");
    return;
  }

  showUploadLoading(`Analyzing ${file.name}... Extracting skills, structure, and ATS metrics.`);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("/api/upload_and_parse", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      throw new Error(data.error || `Upload failed with status ${response.status}`);
    }

    saveAnalysisData(data);
    renderUploadResults(data);

  } catch (err) {
    console.error("Upload error:", err);
    showUploadError(err.message || "Failed to analyze resume. Please ensure it is a valid PDF or DOCX file.");
  }
}

function showUploadLoading(msg) {
  const statusBox = document.getElementById("uploadStatus");
  const resultCard = document.getElementById("uploadResultsCard");
  const btn = document.getElementById("analyzeBtn");

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="inline-block animate-spin mr-2">⟳</span> Analyzing...`;
  }

  if (statusBox) {
    statusBox.classList.remove("hidden");
    statusBox.innerHTML = `
      <div class="p-4 glass rounded-2xl border border-orange-500/30 flex items-center gap-3">
        <div class="w-6 h-6 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
        <div class="text-sm text-gray-200">${msg}</div>
      </div>
    `;
  }
  if (resultCard) resultCard.classList.add("hidden");
}

function showUploadError(msg) {
  const statusBox = document.getElementById("uploadStatus");
  const btn = document.getElementById("analyzeBtn");

  if (btn) {
    btn.disabled = false;
    btn.innerHTML = `🚀 Analyze Resume`;
  }

  if (statusBox) {
    statusBox.classList.remove("hidden");
    statusBox.innerHTML = `
      <div class="p-4 bg-red-500/20 rounded-2xl border border-red-500/40 text-red-300 text-sm flex items-start gap-3">
        <span class="text-lg">❌</span>
        <div>
          <strong class="block mb-1">Analysis Error:</strong>
          <span>${msg}</span>
        </div>
      </div>
    `;
  }
}

function saveAnalysisData(data) {
  localStorage.setItem("growpath_data", JSON.stringify(data));
  localStorage.setItem("growpath_resume_text", data.parsed_resume.raw_text);
  localStorage.setItem("resume_text", data.parsed_resume.raw_text);
  localStorage.setItem("ats_analysis", JSON.stringify(data.ats_analysis));
  GrowPath.resumeData = data;
}

// =====================================================================
// Render Upload Results on Main Landing Page
// =====================================================================
function renderUploadResults(data) {
  const statusBox = document.getElementById("uploadStatus");
  const resultCard = document.getElementById("uploadResultsCard");
  const btn = document.getElementById("analyzeBtn");

  if (btn) {
    btn.disabled = false;
    btn.innerHTML = `🚀 Analyze Another Resume`;
  }

  if (statusBox) statusBox.classList.add("hidden");
  if (!resultCard) return;

  resultCard.classList.remove("hidden");

  const p = data.parsed_resume;
  const ats = data.ats_analysis;
  const skills = data.extracted_skills;
  const jobs = data.live_jobs || [];
  const roles = data.suggested_roles || [];

  // 1. Candidate Info
  const nameEl = document.getElementById("resCandidateName");
  if (nameEl) nameEl.textContent = p.contact_info.name || "Candidate";

  const emailEl = document.getElementById("resCandidateEmail");
  if (emailEl) emailEl.textContent = p.contact_info.email || "Email not detected";

  const phoneEl = document.getElementById("resCandidatePhone");
  if (phoneEl) phoneEl.textContent = p.contact_info.phone || "Phone not detected";

  const scoreEl = document.getElementById("resOverallScore");
  if (scoreEl) scoreEl.textContent = `${ats.overall_score}/100`;

  const verdictEl = document.getElementById("resVerdict");
  if (verdictEl) verdictEl.textContent = ats.verdict;

  // 2. Score Badge color
  const badgeEl = document.getElementById("resScoreBadge");
  if (badgeEl) {
    badgeEl.className = `px-3 py-1 rounded-full text-xs font-semibold ${
      ats.overall_score >= 80 ? "bg-green-500/20 text-green-300 border border-green-500/30" :
      ats.overall_score >= 60 ? "bg-orange-500/20 text-orange-300 border border-orange-500/30" :
      "bg-red-500/20 text-red-300 border border-red-500/30"
    }`;
    badgeEl.textContent = ats.overall_score >= 80 ? "ATS Ready" : ats.overall_score >= 60 ? "Good Potential" : "Needs Polish";
  }

  // 3. Extracted Skills Pills
  const skillsContainer = document.getElementById("resSkillsContainer");
  if (skillsContainer) {
    skillsContainer.innerHTML = "";
    const allSkills = skills.all_skills || [];
    if (allSkills.length === 0) {
      skillsContainer.innerHTML = `<span class="text-sm text-gray-400">No standardized technical skills detected.</span>`;
    } else {
      allSkills.slice(0, 16).forEach(s => {
        const chip = document.createElement("span");
        chip.className = "px-3 py-1 bg-white/10 hover:bg-orange-500/20 border border-white/10 hover:border-orange-500/40 text-xs rounded-full text-gray-200 transition-colors";
        chip.textContent = s;
        skillsContainer.appendChild(chip);
      });
      if (allSkills.length > 16) {
        const more = document.createElement("span");
        more.className = "px-2 py-1 text-xs text-orange-400 font-medium";
        more.textContent = `+${allSkills.length - 16} more`;
        skillsContainer.appendChild(more);
      }
    }
  }

  // 4. Suggested Roles
  const rolesContainer = document.getElementById("resSuggestedRoles");
  if (rolesContainer) {
    rolesContainer.innerHTML = "";
    roles.slice(0, 4).forEach(r => {
      const title = typeof r === "object" ? r.title : r;
      const match = typeof r === "object" ? r.match_score : 85;
      const pill = document.createElement("div");
      pill.className = "p-3 glass rounded-xl border border-white/10 flex items-center justify-between";
      pill.innerHTML = `
        <div>
          <div class="text-sm font-semibold text-orange-300">${title}</div>
          <div class="text-xs text-gray-400">${typeof r === "object" ? r.rationale : "Strong skill match"}</div>
        </div>
        <span class="text-xs font-bold px-2 py-1 bg-orange-500/20 text-orange-400 rounded-lg">${match}%</span>
      `;
      rolesContainer.appendChild(pill);
    });
  }

  // 5. Live Job Listings on Sidebar
  renderLiveJobsSidebar(jobs);

  // Auto-scroll to results
  resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
}

// Global state for live jobs
let currentJobCountry = "IN";

function renderLiveJobsSidebar(jobs) {
  const container = document.getElementById("jobsContainer");
  if (!container) return;

  container.innerHTML = "";

  if (!jobs || jobs.length === 0) {
    container.innerHTML = `
      <div class="p-5 glass rounded-2xl border border-white/10 text-center">
        <div class="text-gray-400 text-sm mb-2">No live listings retrieved for this filter.</div>
        <button onclick="fetchJobsForCountry('IN')" class="text-xs px-3 py-1.5 bg-orange-500 text-black rounded-lg font-semibold hover:bg-orange-400 transition">
          Search Live India Jobs
        </button>
      </div>
    `;
    return;
  }

  jobs.forEach(job => {
    const card = document.createElement("div");
    card.className = "p-4 glass rounded-2xl border border-white/10 hover:border-orange-500/40 transition-all flex flex-col justify-between";
    card.innerHTML = `
      <div>
        <div class="flex items-start justify-between gap-2 mb-1.5">
          <h4 class="text-xs font-semibold text-orange-400 leading-tight">${job.title}</h4>
          <span class="text-[9px] px-1.5 py-0.5 bg-emerald-500/20 text-emerald-300 rounded border border-emerald-500/30 shrink-0">Verified</span>
        </div>
        <p class="text-xs text-gray-200 font-medium mb-1">${job.company}</p>
        <p class="text-[11px] text-gray-400 mb-2.5">📍 ${job.location || "Remote"} • 💰 ${job.salary || "Competitive"}</p>
      </div>
      <div class="pt-2 border-t border-white/5 flex items-center justify-between">
        <span class="text-[10px] text-gray-400">${job.date_posted || "Recently"}</span>
        <a href="${job.link || job.url}" target="_blank" rel="noopener noreferrer"
           class="px-2.5 py-1 bg-gradient-to-r from-orange-500 to-amber-500 text-black rounded-lg text-[11px] font-bold hover:brightness-110 transition shadow-sm">
          Apply Now ↗
        </a>
      </div>
    `;
    container.appendChild(card);
  });
}

function renderDashboardJobs(jobs) {
  const container = document.getElementById("dashJobsGrid");
  if (!container) return;

  if (!jobs || jobs.length === 0) {
    container.innerHTML = `
      <div class="p-8 glass rounded-2xl border border-white/10 text-center col-span-full">
        <div class="text-gray-400 text-sm mb-2">No live jobs retrieved for this filter.</div>
        <button onclick="fetchJobsForCountry('IN')" class="text-xs px-3 py-1.5 bg-orange-500 text-black rounded-lg font-semibold hover:bg-orange-400 transition">
          Search Live India Jobs
        </button>
      </div>
    `;
    return;
  }

  container.innerHTML = jobs.map(j => `
    <div class="p-5 glass rounded-2xl border border-white/10 hover:border-orange-500/40 transition flex flex-col justify-between">
      <div>
        <div class="flex items-start justify-between gap-2 mb-2">
          <h4 class="text-sm font-bold text-orange-400">${j.title}</h4>
          <span class="text-[10px] px-2 py-0.5 bg-emerald-500/20 text-emerald-300 rounded border border-emerald-500/30">Verified</span>
        </div>
        <p class="text-xs font-semibold text-gray-200 mb-1">${j.company}</p>
        <p class="text-xs text-gray-400 mb-4">📍 ${j.location || "Remote"} • 💰 ${j.salary || "Competitive"}</p>
      </div>
      <div class="pt-3 border-t border-white/5 flex items-center justify-between">
        <span class="text-[11px] text-gray-400">${j.date_posted || "Recently"}</span>
        <a href="${j.link || j.url}" target="_blank" rel="noopener noreferrer" class="px-3 py-1.5 bg-gradient-to-r from-orange-500 to-amber-500 text-black rounded-xl text-xs font-bold hover:brightness-110 transition">
          View & Apply ↗
        </a>
      </div>
    </div>
  `).join("");
}
window.renderDashboardJobs = renderDashboardJobs;

function updateCountryButtonPills(activeCountry) {
  document.querySelectorAll("[data-job-country]").forEach(btn => {
    const c = btn.getAttribute("data-job-country");
    if (c === activeCountry) {
      btn.className = "job-country-pill px-3 py-1.5 rounded-xl bg-orange-500/20 text-orange-300 border border-orange-500/30 text-xs font-semibold transition";
    } else {
      btn.className = "job-country-pill px-3 py-1.5 rounded-xl glass hover:bg-white/10 text-xs text-gray-300 transition";
    }
  });
}

// =====================================================================
// Fetch Jobs by Country / Custom Query Filter
// =====================================================================
async function fetchJobsForCountry(countryCode, customRole = "") {
  currentJobCountry = countryCode || "IN";
  updateCountryButtonPills(currentJobCountry);

  const sidebarContainer = document.getElementById("jobsContainer");
  const dashContainer = document.getElementById("dashJobsGrid");

  const loadingHtml = `<div class="p-6 text-center text-sm text-gray-300 animate-pulse col-span-full">🔍 Fetching verified live openings in ${currentJobCountry.toUpperCase()}...</div>`;
  if (sidebarContainer) sidebarContainer.innerHTML = loadingHtml;
  if (dashContainer) dashContainer.innerHTML = loadingHtml;

  const storedData = localStorage.getItem("growpath_data");
  let skills = [];
  let roles = customRole ? [customRole] : ["Software Engineer"];

  if (storedData && !customRole) {
    try {
      const parsed = JSON.parse(storedData);
      skills = parsed.extracted_skills?.all_skills || [];
      const suggested = (parsed.suggested_roles || []).map(r => typeof r === "object" ? r.title : r);
      if (suggested && suggested.length > 0) {
        roles = suggested;
      }
    } catch (e) {}
  }

  try {
    const res = await fetch("/api/recommend_jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        roles: roles.slice(0, 2),
        skills: skills,
        country_code: currentJobCountry,
        limit: 4
      })
    });
    const data = await res.json();
    if (data.success && data.jobs && data.jobs.length > 0) {
      if (sidebarContainer) renderLiveJobsSidebar(data.jobs);
      if (dashContainer) renderDashboardJobs(data.jobs);
    } else {
      const fallbackMsg = `<div class="p-6 text-center text-xs text-gray-400 col-span-full">No live jobs retrieved for this filter. Try another keyword or location.</div>`;
      if (sidebarContainer) sidebarContainer.innerHTML = fallbackMsg;
      if (dashContainer) dashContainer.innerHTML = fallbackMsg;
    }
  } catch (err) {
    console.error("Job fetch error:", err);
    const errHtml = `<div class="p-6 text-center text-xs text-red-400 col-span-full">Live search service temporarily unavailable. Please try again.</div>`;
    if (sidebarContainer) sidebarContainer.innerHTML = errHtml;
    if (dashContainer) dashContainer.innerHTML = errHtml;
  }
}

function searchCustomJobs() {
  const input = document.getElementById("dashJobSearchInput") || document.getElementById("sidebarJobSearchInput");
  const query = input ? input.value.trim() : "";
  fetchJobsForCountry(currentJobCountry, query || "Software Engineer");
}

// =====================================================================
// Quick Prefill Job Description Templates
// =====================================================================
function fillSampleJD(type) {
  const jdBox = document.getElementById("atsJD") || document.getElementById("dashJDInput");
  if (jdBox && SAMPLE_JOB_DESCRIPTIONS[type]) {
    jdBox.value = SAMPLE_JOB_DESCRIPTIONS[type];
    clearJDFile();
  }
}

// =====================================================================
// Job Description File Upload & Extraction (PDF, DOCX, TXT)
// =====================================================================
document.addEventListener("DOMContentLoaded", () => {
  setupJDDragAndDrop();
});

function getActiveJDElements() {
  const fileInput = document.getElementById("atsJDFileInput") || document.getElementById("dashJDFileInput");
  const dropZone = document.getElementById("atsJDDropZone") || document.getElementById("dashJDDropZone");
  const statusEl = document.getElementById("atsJDFileStatus") || document.getElementById("dashJDFileStatus");
  const loaderEl = document.getElementById("atsJDExtractLoader") || document.getElementById("dashJDExtractLoader");
  const jdInput = document.getElementById("atsJD") || document.getElementById("dashJDInput");

  return { fileInput, dropZone, statusEl, loaderEl, jdInput };
}

function setupJDDragAndDrop() {
  const dropConfigs = [
    { zone: document.getElementById("dashJDDropZone"), input: document.getElementById("dashJDFileInput") },
    { zone: document.getElementById("atsJDDropZone"), input: document.getElementById("atsJDFileInput") }
  ];

  dropConfigs.forEach(({ zone, input }) => {
    if (!zone || !input) return;

    ["dragenter", "dragover"].forEach(name => {
      zone.addEventListener(name, (e) => {
        e.preventDefault();
        e.stopPropagation();
        zone.classList.add("border-orange-500", "bg-orange-500/15");
      }, false);
    });

    ["dragleave", "drop"].forEach(name => {
      zone.addEventListener(name, (e) => {
        e.preventDefault();
        e.stopPropagation();
        zone.classList.remove("border-orange-500", "bg-orange-500/15");
      }, false);
    });

    zone.addEventListener("drop", (e) => {
      const dt = e.dataTransfer;
      const files = dt ? dt.files : null;
      if (files && files.length > 0) {
        input.files = files;
        handleJDFileSelected(files[0]);
      }
    });
  });
}

async function handleJDFileSelected(file) {
  if (!file) return;

  const { fileInput, statusEl, loaderEl, jdInput } = getActiveJDElements();

  // Client-side Validation: File Size (10 MB)
  const maxBytes = 10 * 1024 * 1024;
  if (file.size > maxBytes) {
    showJDFileError("Job Description file is too large. Please upload a file smaller than 10 MB.");
    return;
  }

  // Client-side Validation: Empty File
  if (file.size === 0) {
    showJDFileError("The selected file is empty (0 bytes). Please upload a valid document.");
    return;
  }

  // Client-side Validation: File Extension
  const validExtensions = [".pdf", ".docx", ".doc", ".txt"];
  const fileNameLower = file.name.toLowerCase();
  const isValidExt = validExtensions.some(ext => fileNameLower.endsWith(ext));
  if (!isValidExt) {
    showJDFileError("Unsupported file format. Please upload a PDF, DOCX, or TXT file.");
    return;
  }

  const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
  const inputId = fileInput ? fileInput.id : (document.getElementById("atsJDFileInput") ? "atsJDFileInput" : "dashJDFileInput");

  // Show Loading State
  if (statusEl) {
    statusEl.classList.remove("hidden");
    statusEl.innerHTML = `
      <div class="p-3 glass rounded-xl border border-orange-500/30 flex items-center justify-between gap-2">
        <div class="flex items-center gap-2 text-xs text-orange-300">
          <div class="w-4 h-4 border-2 border-orange-500 border-t-transparent rounded-full animate-spin shrink-0"></div>
          <span>Extracting text from <strong>${escapeJsString(file.name)}</strong>...</span>
        </div>
        <span class="text-[10px] text-gray-400">${sizeMb} MB</span>
      </div>
    `;
  }
  if (loaderEl) loaderEl.classList.remove("hidden");

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/upload_jd", {
      method: "POST",
      body: formData
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      throw new Error(data.error || "Failed to extract text from Job Description.");
    }

    // Populate textarea with extracted plain text
    if (jdInput) {
      jdInput.value = data.text;
    }

    // Show Success Badge with Replace & Clear options
    if (statusEl) {
      statusEl.classList.remove("hidden");
      statusEl.innerHTML = `
        <div class="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center justify-between gap-2">
          <div class="flex items-center gap-2 overflow-hidden">
            <span class="text-emerald-400 font-bold shrink-0">✓</span>
            <span class="text-xs text-gray-200 font-semibold truncate" title="${escapeJsString(data.filename)}">${escapeJsString(data.filename)}</span>
            <span class="text-[10px] text-emerald-300/80 bg-emerald-500/20 px-1.5 py-0.5 rounded shrink-0">${data.file_type} • ${sizeMb} MB</span>
          </div>
          <div class="flex items-center gap-1.5 shrink-0">
            <button type="button" onclick="document.getElementById('${inputId}').click()" class="text-[11px] px-2.5 py-1 glass hover:bg-white/10 text-orange-300 font-semibold rounded-lg border border-orange-500/30 transition cursor-pointer">
              Replace File
            </button>
            <button type="button" onclick="clearJDFile()" class="text-xs px-2 py-1 text-gray-400 hover:text-rose-400 transition cursor-pointer" title="Clear file">
              ✕
            </button>
          </div>
        </div>
      `;

      // Soft note if extracted text is unusually short
      if (data.text && data.text.trim().length < 40) {
        statusEl.innerHTML += `
          <div class="mt-1.5 text-[11px] text-amber-300 bg-amber-500/10 p-2 rounded-lg border border-amber-500/20">
            ⚠️ The extracted text appears very short (${data.word_count || 0} words). You can edit or add more requirements in the box below before analyzing.
          </div>
        `;
      }
    }

  } catch (err) {
    console.error("[GrowPath] JD Upload error:", err);
    showJDFileError(err.message || "Failed to extract text from file. Please try another file or paste the Job Description manually.");
  } finally {
    if (loaderEl) loaderEl.classList.add("hidden");
  }
}

function showJDFileError(msg) {
  const { statusEl, loaderEl } = getActiveJDElements();
  if (loaderEl) loaderEl.classList.add("hidden");

  if (statusEl) {
    statusEl.classList.remove("hidden");
    statusEl.innerHTML = `
      <div class="p-3 bg-red-500/15 border border-red-500/30 rounded-xl flex items-start justify-between gap-2 text-xs text-red-300">
        <div class="flex items-start gap-2">
          <span class="shrink-0 mt-0.5">❌</span>
          <div class="leading-relaxed">
            <strong class="block mb-0.5">Upload Error:</strong>
            <span>${msg}</span>
          </div>
        </div>
        <button type="button" onclick="clearJDFile()" class="text-xs text-gray-400 hover:text-white shrink-0 p-1 cursor-pointer">✕</button>
      </div>
    `;
  } else {
    alert(`❌ ${msg}`);
  }
}

function clearJDFile() {
  const { fileInput, statusEl, loaderEl } = getActiveJDElements();

  if (fileInput) fileInput.value = "";
  if (statusEl) {
    statusEl.innerHTML = "";
    statusEl.classList.add("hidden");
  }
  if (loaderEl) loaderEl.classList.add("hidden");
}

// =====================================================================
// Job Description Matching & Skill Gap Analysis
// =====================================================================
async function analyzeJobMatch() {
  const resumeBox = document.getElementById("dashResumeInput") || document.getElementById("resumeTextBox");
  const jdBox = document.getElementById("dashJDInput") || document.getElementById("atsJD");
  const resultDiv = document.getElementById("dashJDMatchResult") || document.getElementById("atsResult");
  const analyzeBtn = document.getElementById("dashJDAnalyzeBtn") || document.querySelector("button[onclick='analyzeJobMatch()']");

  let resumeText = resumeBox ? resumeBox.value.trim() : "";
  if (!resumeText) {
    const stored = localStorage.getItem("growpath_resume_text") || localStorage.getItem("resume_text") || window.SAMPLE_RESUME_TEXT || "";
    if (stored) {
      resumeText = stored.trim();
      if (resumeBox) resumeBox.value = resumeText;
    }
  }

  const jobDesc = jdBox ? jdBox.value.trim() : "";

  // Validation: No Resume Text
  if (!resumeText) {
    if (resultDiv) {
      resultDiv.classList.remove("hidden");
      resultDiv.innerHTML = `
        <div class="p-8 text-center glass rounded-3xl border border-amber-500/30 space-y-3">
          <div class="w-12 h-12 rounded-2xl bg-amber-500/20 text-amber-300 flex items-center justify-center mx-auto text-xl">📄</div>
          <h4 class="text-base font-bold text-amber-300">No Resume Available</h4>
          <p class="text-xs text-gray-300 max-w-md mx-auto leading-relaxed">
            Upload and analyze your resume first, or paste your resume text into the <strong>Resume Context</strong> box above to compare it with a target job description.
          </p>
          <div class="pt-2 flex justify-center gap-3">
            <a href="/" class="px-5 py-2.5 bg-gradient-to-r from-orange-500 to-amber-500 text-black font-bold text-xs rounded-xl hover:brightness-110 transition shadow">
              Upload Resume →
            </a>
          </div>
        </div>
      `;
    } else {
      alert("⚠️ Upload and analyze a resume first to compare it with a job description.");
    }
    return;
  }

  // Validation: No Job Description
  if (!jobDesc) {
    if (resultDiv) {
      resultDiv.classList.remove("hidden");
      resultDiv.innerHTML = `
        <div class="p-6 text-center glass rounded-2xl border border-orange-500/30 space-y-2">
          <h4 class="text-sm font-bold text-orange-300">Target Job Description Required</h4>
          <p class="text-xs text-gray-300">Please paste a target Job Description in the box above or choose one of the preset templates (Full Stack, AI / ML, Backend).</p>
        </div>
      `;
    } else {
      alert("⚠️ Please paste a Job Description to match against.");
    }
    return;
  }

  // Loading State
  let originalBtnHtml = "";
  if (analyzeBtn) {
    analyzeBtn.disabled = true;
    originalBtnHtml = analyzeBtn.innerHTML;
    analyzeBtn.innerHTML = `<span class="inline-block w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin mr-2"></span> Analyzing Job Match...`;
  }

  if (resultDiv) {
    resultDiv.classList.remove("hidden");
    resultDiv.innerHTML = `
      <div class="p-8 text-center glass rounded-3xl border border-orange-500/30 flex flex-col items-center justify-center gap-3">
        <div class="w-8 h-8 border-3 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
        <div class="text-sm font-bold text-orange-300">Analyzing your resume against this job description...</div>
        <div class="text-xs text-gray-400">Comparing technical skill taxonomy, evaluating keyword overlap, and prioritizing skill gaps.</div>
      </div>
    `;
  }

  // Skills payload if available
  let skills = [];
  try {
    const storedData = localStorage.getItem("growpath_data");
    if (storedData) {
      const parsed = JSON.parse(storedData);
      if (parsed.extracted_skills && Array.isArray(parsed.extracted_skills.all_skills)) {
        skills = parsed.extracted_skills.all_skills;
      }
    }
  } catch (e) {}

  try {
    const res = await fetch("/api/match_job", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_text: resumeText,
        job_description: jobDesc,
        skills: skills
      })
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      throw new Error(data.error || "Unable to analyze this job description. Please try again.");
    }

    renderJobMatchResults(data.match_result, resultDiv);

  } catch (err) {
    console.error("[GrowPath] Match Job error:", err);
    if (resultDiv) {
      resultDiv.classList.remove("hidden");
      resultDiv.innerHTML = `
        <div class="p-6 bg-red-500/20 border border-red-500/40 rounded-2xl text-red-300 text-sm space-y-1">
          <div class="font-bold flex items-center gap-2"><span>❌</span> Unable to analyze this job description.</div>
          <p class="text-xs text-red-200">${err.message || 'Please check your inputs and try again.'}</p>
        </div>
      `;
    }
  } finally {
    if (analyzeBtn) {
      analyzeBtn.disabled = false;
      if (originalBtnHtml) {
        analyzeBtn.innerHTML = originalBtnHtml;
      } else {
        analyzeBtn.innerHTML = `<span>⚡</span> Analyze Job Match`;
      }
    }
  }
}

function renderJobMatchResults(match, container) {
  if (!container) return;

  const score = match.match_score || 0;
  const isHigh = score >= 80;
  const isMed = score >= 60;

  const scoreColor = isHigh ? "text-emerald-400" : isMed ? "text-amber-400" : "text-rose-400";
  const badgeBg = isHigh ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" : isMed ? "bg-amber-500/20 text-amber-300 border-amber-500/30" : "bg-rose-500/20 text-rose-300 border-rose-500/30";
  const badgeText = isHigh ? "Strong Match" : isMed ? "Moderate Match" : "Low Match";

  const bd = match.breakdown || {};
  const skillsScore = bd.skills_match ?? 75;
  const expScore = bd.experience_match ?? 70;
  const projScore = bd.projects_match ?? 75;
  const kwScore = bd.keywords_match ?? 70;

  const metrics = match.metrics || {};
  const matchedSkills = match.matched_skills || [];
  const missingSkills = match.missing_skills || [];
  const matchedKeywords = match.matched_keywords || [];
  const missingKeywords = match.missing_keywords || [];
  const gaps = match.prioritized_gaps || { high_priority: [], medium_priority: [], low_priority: [] };
  const highGaps = gaps.high_priority || [];
  const medGaps = gaps.medium_priority || [];
  const lowGaps = gaps.low_priority || [];
  const tips = match.tailoring_tips || [];

  container.innerHTML = `
    <div class="mt-8 pt-8 border-t border-white/10 space-y-8 animate-fadeIn">
      
      <!-- 1. Overall Match Hero Banner -->
      <div class="glass-strong rounded-3xl p-6 sm:p-8 border border-white/10 shadow-2xl relative overflow-hidden">
        <div class="absolute top-0 right-0 w-96 h-96 bg-orange-500/5 rounded-full blur-3xl pointer-events-none"></div>

        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div class="space-y-2">
            <div class="flex items-center gap-3">
              <span class="text-xs uppercase tracking-widest text-orange-400 font-bold">Overall Job Match</span>
              <span class="px-2.5 py-0.5 rounded-full text-xs font-bold border ${badgeBg}">${badgeText}</span>
            </div>
            <div class="flex items-baseline gap-3">
              <span class="text-5xl sm:text-6xl font-black ${scoreColor}">${score}%</span>
              <span class="text-sm sm:text-base text-gray-300 font-medium">Alignment Score</span>
            </div>
            <p class="text-xs sm:text-sm text-gray-400 max-w-xl leading-relaxed">${match.fit_level || 'Analysis complete.'}</p>
          </div>

          <!-- Quick Metrics Stat Pills -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full lg:w-auto">
            <div class="p-3.5 glass rounded-2xl border border-white/5 text-center">
              <div class="text-xs text-gray-400 font-medium">Total Required</div>
              <div class="text-xl font-bold text-white mt-0.5">${metrics.total_jd_skills_required ?? (matchedSkills.length + missingSkills.length)}</div>
            </div>
            <div class="p-3.5 glass rounded-2xl border border-emerald-500/20 text-center">
              <div class="text-xs text-emerald-400 font-medium">Matched Skills</div>
              <div class="text-xl font-bold text-emerald-300 mt-0.5">${metrics.matched_skills_count ?? matchedSkills.length}</div>
            </div>
            <div class="p-3.5 glass rounded-2xl border border-rose-500/20 text-center">
              <div class="text-xs text-rose-400 font-medium">Missing Skills</div>
              <div class="text-xl font-bold text-rose-300 mt-0.5">${metrics.missing_skills_count ?? missingSkills.length}</div>
            </div>
            <div class="p-3.5 glass rounded-2xl border border-amber-500/20 text-center">
              <div class="text-xs text-amber-400 font-medium">Keyword Rate</div>
              <div class="text-xl font-bold text-amber-300 mt-0.5">${kwScore}%</div>
            </div>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="mt-6">
          <div class="w-full bg-white/5 h-3 rounded-full overflow-hidden border border-white/10">
            <div class="h-full bg-gradient-to-r from-orange-500 via-amber-400 to-emerald-400 rounded-full transition-all duration-1000" style="width: ${score}%;"></div>
          </div>
        </div>
      </div>

      <!-- 2. 4-Category Match Breakdown -->
      <div class="glass-strong rounded-3xl p-6 sm:p-8 border border-white/10 shadow-2xl space-y-5">
        <h4 class="text-base font-bold text-white flex items-center justify-between">
          <span class="flex items-center gap-2"><span>📊</span> Match Breakdown Analysis</span>
          <span class="text-xs text-gray-400 font-normal">Deterministic Sub-Scores</span>
        </h4>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <!-- Skills Match -->
          <div class="p-4 glass rounded-2xl border border-white/5 space-y-2">
            <div class="flex items-center justify-between text-xs font-semibold">
              <span class="text-gray-300 flex items-center gap-1.5"><span>🛠</span> Skills Match</span>
              <span class="text-emerald-400 font-bold">${skillsScore}%</span>
            </div>
            <div class="w-full bg-white/5 h-2 rounded-full overflow-hidden">
              <div class="bg-emerald-400 h-full rounded-full transition-all duration-700" style="width: ${skillsScore}%;"></div>
            </div>
          </div>

          <!-- Experience Match -->
          <div class="p-4 glass rounded-2xl border border-white/5 space-y-2">
            <div class="flex items-center justify-between text-xs font-semibold">
              <span class="text-gray-300 flex items-center gap-1.5"><span>💼</span> Experience Match</span>
              <span class="text-sky-400 font-bold">${expScore}%</span>
            </div>
            <div class="w-full bg-white/5 h-2 rounded-full overflow-hidden">
              <div class="bg-sky-400 h-full rounded-full transition-all duration-700" style="width: ${expScore}%;"></div>
            </div>
          </div>

          <!-- Project Match -->
          <div class="p-4 glass rounded-2xl border border-white/5 space-y-2">
            <div class="flex items-center justify-between text-xs font-semibold">
              <span class="text-gray-300 flex items-center gap-1.5"><span>🚀</span> Project Match</span>
              <span class="text-pink-400 font-bold">${projScore}%</span>
            </div>
            <div class="w-full bg-white/5 h-2 rounded-full overflow-hidden">
              <div class="bg-pink-400 h-full rounded-full transition-all duration-700" style="width: ${projScore}%;"></div>
            </div>
          </div>

          <!-- Keyword Match -->
          <div class="p-4 glass rounded-2xl border border-white/5 space-y-2">
            <div class="flex items-center justify-between text-xs font-semibold">
              <span class="text-gray-300 flex items-center gap-1.5"><span>🔍</span> Keyword Match</span>
              <span class="text-amber-400 font-bold">${kwScore}%</span>
            </div>
            <div class="w-full bg-white/5 h-2 rounded-full overflow-hidden">
              <div class="bg-amber-400 h-full rounded-full transition-all duration-700" style="width: ${kwScore}%;"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. Dual Column: Matched Skills & Skill Gap Breakdown -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        <!-- Matched Skills Column -->
        <div class="glass-strong rounded-3xl p-6 sm:p-7 border border-white/10 shadow-2xl space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-white/10">
            <h4 class="text-sm font-bold text-emerald-400 flex items-center gap-2">
              <span class="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs">✓</span>
              Matched Skills (${matchedSkills.length})
            </h4>
            <span class="text-[11px] text-gray-400">Found in resume</span>
          </div>

          <p class="text-xs text-gray-400">Skills present in your resume that directly satisfy job opening requirements.</p>

          <div class="flex flex-wrap gap-2 pt-1">
            ${
              matchedSkills.length > 0
                ? matchedSkills.map(s => `
                  <span class="px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold rounded-xl flex items-center gap-1.5 shadow-sm">
                    <span class="text-emerald-400 font-bold">✓</span> ${s}
                  </span>
                `).join("")
                : `<div class="p-4 glass rounded-xl text-xs text-gray-400 w-full text-center">No direct skill matches detected.</div>`
            }
          </div>
        </div>

        <!-- Skill Gap Column with Priorities -->
        <div class="glass-strong rounded-3xl p-6 sm:p-7 border border-white/10 shadow-2xl space-y-4">
          <div class="flex items-center justify-between pb-3 border-b border-white/10">
            <h4 class="text-sm font-bold text-rose-400 flex items-center gap-2">
              <span class="w-5 h-5 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center text-xs">✗</span>
              Skill Gap Breakdown (${missingSkills.length})
            </h4>
            <span class="text-[11px] text-gray-400">Required by role</span>
          </div>

          <p class="text-xs text-gray-400">Key competencies requested in the job description but not detected in your resume.</p>

          ${
            missingSkills.length === 0
              ? `
                <div class="p-6 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl text-center space-y-1">
                  <div class="text-emerald-300 font-bold text-sm">🎉 Perfect Skill Alignment!</div>
                  <div class="text-xs text-emerald-400/80">All extracted technical skills from the job description are represented in your resume.</div>
                </div>
              `
              : `
                <div class="space-y-3.5 pt-1">
                  <!-- High Priority -->
                  ${highGaps.length > 0 ? `
                    <div class="p-3.5 glass rounded-2xl border border-rose-500/20 space-y-2">
                      <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-rose-300 flex items-center gap-1.5">
                          <span>🔴</span> High Priority (Core Role Requirements)
                        </span>
                        <span class="text-[10px] text-rose-400 font-mono font-bold">${highGaps.length}</span>
                      </div>
                      <div class="flex flex-wrap gap-1.5">
                        ${highGaps.map(s => `
                          <span class="px-2.5 py-1 bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs font-medium rounded-lg flex items-center gap-1">
                            <span>✗</span> ${s}
                          </span>
                        `).join("")}
                      </div>
                    </div>
                  ` : ''}

                  <!-- Medium Priority -->
                  ${medGaps.length > 0 ? `
                    <div class="p-3.5 glass rounded-2xl border border-amber-500/20 space-y-2">
                      <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-amber-300 flex items-center gap-1.5">
                          <span>🟡</span> Medium Priority (Important Tech & Tools)
                        </span>
                        <span class="text-[10px] text-amber-400 font-mono font-bold">${medGaps.length}</span>
                      </div>
                      <div class="flex flex-wrap gap-1.5">
                        ${medGaps.map(s => `
                          <span class="px-2.5 py-1 bg-amber-500/15 border border-amber-500/30 text-amber-300 text-xs font-medium rounded-lg flex items-center gap-1">
                            <span>✗</span> ${s}
                          </span>
                        `).join("")}
                      </div>
                    </div>
                  ` : ''}

                  <!-- Low Priority -->
                  ${lowGaps.length > 0 ? `
                    <div class="p-3.5 glass rounded-2xl border border-blue-500/20 space-y-2">
                      <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-blue-300 flex items-center gap-1.5">
                          <span>🟢</span> Low Priority (Secondary / Nice-to-Have)
                        </span>
                        <span class="text-[10px] text-blue-400 font-mono font-bold">${lowGaps.length}</span>
                      </div>
                      <div class="flex flex-wrap gap-1.5">
                        ${lowGaps.map(s => `
                          <span class="px-2.5 py-1 bg-blue-500/15 border border-blue-500/30 text-blue-300 text-xs font-medium rounded-lg flex items-center gap-1">
                            <span>✗</span> ${s}
                          </span>
                        `).join("")}
                      </div>
                    </div>
                  ` : ''}
                </div>
              `
          }
        </div>
      </div>

      <!-- 4. Missing Keywords Section -->
      <div class="glass-strong rounded-3xl p-6 sm:p-7 border border-white/10 shadow-2xl space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-white/10">
          <div>
            <h4 class="text-sm font-bold text-white flex items-center gap-2">
              <span>🔑</span> Important Missing Keywords (${missingKeywords.length})
            </h4>
            <p class="text-xs text-gray-400 mt-0.5">High-frequency terminology appearing in the Job Description but absent from your resume.</p>
          </div>
          <span class="text-[11px] text-orange-400 font-semibold shrink-0">ATS Keyword Match</span>
        </div>

        <div class="flex flex-wrap gap-2 pt-1">
          ${
            missingKeywords.length > 0
              ? missingKeywords.map(kw => `
                <span class="px-3 py-1 bg-black/40 border border-white/15 hover:border-orange-500/40 text-gray-200 text-xs font-mono rounded-xl transition">
                  ${kw}
                </span>
              `).join("")
              : `<div class="text-xs text-emerald-400">Great job! No major high-frequency job description keywords are missing.</div>`
          }
        </div>
        <p class="text-[11px] text-gray-400 italic">
          Tip: Naturally weave these domain terms into your project descriptions and responsibilities where accurate.
        </p>
      </div>

      <!-- 5. Actionable Recommendations -->
      <div class="glass-strong rounded-3xl p-6 sm:p-8 border border-white/10 shadow-2xl space-y-5">
        <div class="flex items-center justify-between pb-3 border-b border-white/10">
          <h4 class="text-base font-bold text-white flex items-center gap-2">
            <span>💡</span> How to Improve Your Match & Tailor Your Resume
          </h4>
          <span class="text-xs text-orange-400 font-semibold">Personalized Guidance</span>
        </div>

        <div class="space-y-3">
          ${
            tips.length > 0
              ? tips.map((tip, idx) => `
                <div class="p-4 bg-orange-500/10 border border-orange-500/20 rounded-2xl flex items-start gap-3.5">
                  <span class="text-xs font-extrabold px-2.5 py-1 bg-orange-500/20 text-orange-300 rounded-lg shrink-0 mt-0.5">${idx + 1}</span>
                  <div class="text-xs sm:text-sm text-gray-200 leading-relaxed font-medium">${tip}</div>
                </div>
              `).join("")
              : `
                <div class="p-4 glass rounded-xl text-xs text-gray-300">
                  Align your experience bullet points with the primary responsibilities in the job posting to ensure optimal ATS ranking.
                </div>
              `
          }
        </div>

        <!-- Ethical Guideline Disclaimer -->
        <div class="p-3.5 glass rounded-xl border border-white/5 flex items-center gap-2 text-[11px] text-gray-400">
          <span class="text-amber-400">⚠️</span>
          <span><strong>Important:</strong> Add skills and keywords only if you have actually used them. Never falsify experience on your resume.</span>
        </div>
      </div>

      <!-- 6. Interactive Next Step Buttons -->
      <div class="flex flex-wrap items-center gap-3 pt-2">
        ${
          missingSkills.length > 0
            ? `
              <button onclick="generateLearningRoadmapForMissing(${JSON.stringify(missingSkills).replace(/"/g, '&quot;')})"
                      class="px-6 py-3.5 bg-gradient-to-r from-orange-500 to-amber-500 text-black font-extrabold text-xs rounded-xl hover:brightness-110 transition shadow-lg flex items-center gap-2 cursor-pointer">
                <span>🚀</span> Generate 4-Week Skill Roadmap
              </button>
            `
            : ''
        }
        <button onclick="if(typeof switchDashTab==='function') switchDashTab('interview'); else window.location.href='/dashboard#interview';"
                class="px-6 py-3.5 glass border border-orange-400/40 text-orange-300 font-bold text-xs rounded-xl hover:bg-orange-500/10 transition flex items-center gap-2 cursor-pointer">
          <span>🎙</span> Prepare Tailored Interview Questions →
        </button>
      </div>

    </div>
  `;
}

// =====================================================================
// AI Bullet Optimizer (STAR Method)
// =====================================================================
async function optimizeBulletPoint() {
  const inputEl = document.getElementById("bulletInput");
  const roleEl = document.getElementById("bulletTargetRole");
  const resultBox = document.getElementById("bulletResultBox");

  const bullet = inputEl ? inputEl.value.trim() : "";
  const role = roleEl ? roleEl.value.trim() : "Software Engineer";

  if (!bullet) {
    alert("⚠️ Please enter a bullet point or project description to rewrite.");
    return;
  }

  if (resultBox) {
    resultBox.classList.remove("hidden");
    resultBox.innerHTML = `
      <div class="p-6 text-center text-sm text-orange-400 flex items-center justify-center gap-3">
        <div class="w-5 h-5 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
        <span>Optimizing with STAR framework, action verbs, and impact metrics...</span>
      </div>
    `;
  }

  try {
    const res = await fetch("/api/improve_bullet", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bullet_text: bullet, target_role: role })
    });

    const data = await res.json();
    if (!data.success) {
      throw new Error(data.error || "Failed to optimize bullet point.");
    }

    renderBulletRewrites(data.improvement, resultBox);

  } catch (err) {
    if (resultBox) {
      resultBox.innerHTML = `
        <div class="p-4 bg-red-500/20 border border-red-500/40 rounded-xl text-red-300 text-sm">
          ❌ ${err.message}
        </div>
      `;
    }
  }
}

function renderBulletRewrites(imp, container) {
  if (!container) return;

  const options = imp.improved_options || [];

  container.innerHTML = `
    <div class="space-y-4">
      <div class="flex items-center justify-between pb-2 border-b border-white/10">
        <span class="text-xs font-bold text-orange-400 uppercase tracking-wider">✨ Optimized Bullet Variations</span>
        <span class="text-[11px] text-gray-400">${imp.key_changes || "Enhanced with STAR framework"}</span>
      </div>

      <div class="space-y-3">
        ${options.map((opt, idx) => `
          <div class="p-4 glass rounded-2xl border border-white/10 hover:border-orange-500/40 transition group relative">
            <div class="flex items-center justify-between mb-1.5">
              <span class="text-[11px] font-bold px-2 py-0.5 bg-orange-500/20 text-orange-300 rounded">${opt.style}</span>
              <button onclick="copyToClipboard('${escapeJsString(opt.text)}', this)" class="text-xs text-gray-400 hover:text-white px-2 py-1 rounded bg-white/5 hover:bg-white/10 transition">
                📋 Copy
              </button>
            </div>
            <p class="text-sm text-gray-200 leading-relaxed font-sans">${opt.text}</p>
          </div>
        `).join("")}
      </div>

      <div class="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-xs text-emerald-300 flex items-center gap-2">
        <span>💡</span>
        <span><strong>Power verb added:</strong> ${imp.action_verb_used || "Direct action"} | <strong>Impact metric:</strong> ${imp.quantifiable_metric_added || "Quantified outcome"}</span>
      </div>
    </div>
  `;
}

// =====================================================================
// AI Interview Prep Generator
// =====================================================================
async function generateInterviewPrep() {
  const resumeText = localStorage.getItem("growpath_resume_text") || localStorage.getItem("resume_text");
  const roleInput = document.getElementById("interviewRoleInput");
  const container = document.getElementById("interviewQuestionsContainer");

  const targetRole = roleInput ? roleInput.value.trim() : "Full Stack Developer";

  if (!resumeText) {
    alert("⚠️ Please upload a resume first.");
    return;
  }

  if (container) {
    container.innerHTML = `
      <div class="p-8 text-center text-sm text-orange-400 glass rounded-3xl flex flex-col items-center justify-center gap-3">
        <div class="w-8 h-8 border-3 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
        <span>Generating custom Technical, Behavioral (STAR), and Project Deep-Dive questions for <strong>${targetRole}</strong>...</span>
      </div>
    `;
  }

  try {
    const res = await fetch("/api/interview_prep", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_text: resumeText,
        target_role: targetRole,
        skills: []
      })
    });

    const data = await res.json();
    if (!data.success) throw new Error(data.error || "Failed to generate interview prep.");

    renderInterviewPrep(data.prep, container);

  } catch (err) {
    if (container) {
      container.innerHTML = `
        <div class="p-6 bg-red-500/20 border border-red-500/40 rounded-2xl text-red-300 text-sm">
          ❌ AI Interview Prep is temporarily unavailable. Please try again.
        </div>
      `;
    }
  }
}

function renderInterviewPrep(prep, container) {
  if (!container) return;

  const tech = prep.technical_questions || prep.technical || [];
  const proj = prep.project_deep_dive_questions || prep.project_questions || prep.project || [];
  const behav = prep.behavioral_questions || prep.behavioral || [];
  const hr = prep.hr_questions || prep.hr || [];

  container.innerHTML = `
    <div class="space-y-8">
      <!-- Section 1: Technical Questions -->
      ${tech.length > 0 ? `
      <div>
        <h4 class="text-lg font-bold text-orange-400 mb-4 flex items-center gap-2">
          <span>💻</span> Technical & Architecture Questions
        </h4>
        <div class="space-y-4">
          ${tech.map((q, idx) => `
            <div class="p-5 glass rounded-2xl border border-white/10 space-y-3">
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-start gap-3">
                  <span class="w-6 h-6 rounded-full bg-orange-500/20 text-orange-400 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">${idx+1}</span>
                  <h5 class="text-sm font-semibold text-gray-100">${q.question}</h5>
                </div>
                ${q.difficulty ? `<span class="text-[10px] px-2 py-0.5 rounded bg-white/10 text-gray-300 font-medium">${q.difficulty}</span>` : ''}
              </div>
              ${q.ideal_concepts ? `
              <div class="text-xs text-amber-300/80 bg-amber-500/10 p-2.5 rounded-xl border border-amber-500/20">
                <strong>Key Concepts to Mention:</strong> ${q.ideal_concepts}
              </div>` : ''}
              ${q.sample_answer ? `
              <details class="text-xs text-gray-300 cursor-pointer">
                <summary class="text-orange-400 hover:text-orange-300 font-medium py-1">View Sample Model Answer ▾</summary>
                <p class="mt-2 p-3 bg-white/5 rounded-xl leading-relaxed text-gray-200">${q.sample_answer}</p>
              </details>` : ''}
            </div>
          `).join("")}
        </div>
      </div>` : ''}

      <!-- Section 2: Project Deep-Dive Questions -->
      ${proj.length > 0 ? `
      <div>
        <h4 class="text-lg font-bold text-cyan-400 mb-4 flex items-center gap-2">
          <span>🔨</span> Project Deep-Dive Probes
        </h4>
        <div class="space-y-4">
          ${proj.map((q, idx) => `
            <div class="p-5 glass rounded-2xl border border-white/10 space-y-3">
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-start gap-3">
                  <span class="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">${idx+1}</span>
                  <h5 class="text-sm font-semibold text-gray-100">${q.question}</h5>
                </div>
                ${q.difficulty ? `<span class="text-[10px] px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 font-medium">${q.difficulty}</span>` : ''}
              </div>
              ${q.tips || q.trap_to_avoid ? `
              <div class="text-xs text-cyan-300/80 bg-cyan-500/10 p-2.5 rounded-xl border border-cyan-500/20">
                <strong>Architecture Focus & Tips:</strong> ${q.tips || q.trap_to_avoid}
              </div>` : ''}
              ${q.sample_answer ? `
              <details class="text-xs text-gray-300 cursor-pointer">
                <summary class="text-cyan-400 hover:text-cyan-300 font-medium py-1">View Suggested Answer Structure ▾</summary>
                <p class="mt-2 p-3 bg-white/5 rounded-xl leading-relaxed text-gray-200">${q.sample_answer}</p>
              </details>` : ''}
            </div>
          `).join("")}
        </div>
      </div>` : ''}

      <!-- Section 3: Behavioral STAR Questions -->
      ${behav.length > 0 ? `
      <div>
        <h4 class="text-lg font-bold text-pink-400 mb-4 flex items-center gap-2">
          <span>🤝</span> Behavioral Scenarios (STAR Method)
        </h4>
        <div class="space-y-4">
          ${behav.map((q, idx) => `
            <div class="p-5 glass rounded-2xl border border-white/10 space-y-3">
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-start gap-3">
                  <span class="w-6 h-6 rounded-full bg-pink-500/20 text-pink-400 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">${idx+1}</span>
                  <h5 class="text-sm font-semibold text-gray-100">${q.question}</h5>
                </div>
                ${q.difficulty ? `<span class="text-[10px] px-2 py-0.5 rounded bg-pink-500/10 text-pink-300 font-medium">${q.difficulty}</span>` : ''}
              </div>
              ${q.star_framework ? `
              <div class="text-xs text-pink-300/80 bg-pink-500/10 p-2.5 rounded-xl border border-pink-500/20">
                <strong>STAR Focus:</strong> ${q.star_framework}
              </div>` : ''}
              ${q.sample_answer ? `
              <details class="text-xs text-gray-300 cursor-pointer">
                <summary class="text-pink-400 hover:text-pink-300 font-medium py-1">View Suggested Answer Structure ▾</summary>
                <p class="mt-2 p-3 bg-white/5 rounded-xl leading-relaxed text-gray-200">${q.sample_answer}</p>
              </details>` : ''}
            </div>
          `).join("")}
        </div>
      </div>` : ''}

      <!-- Section 4: HR & Role Culture Questions -->
      ${hr.length > 0 ? `
      <div>
        <h4 class="text-lg font-bold text-emerald-400 mb-4 flex items-center gap-2">
          <span>🎯</span> Role Motivation & HR Questions
        </h4>
        <div class="space-y-4">
          ${hr.map((q, idx) => `
            <div class="p-5 glass rounded-2xl border border-white/10 space-y-3">
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-start gap-3">
                  <span class="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">${idx+1}</span>
                  <h5 class="text-sm font-semibold text-gray-100">${q.question}</h5>
                </div>
                ${q.difficulty ? `<span class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 font-medium">${q.difficulty}</span>` : ''}
              </div>
              ${q.key_talking_point ? `
              <div class="text-xs text-emerald-300/80 bg-emerald-500/10 p-2.5 rounded-xl border border-emerald-500/20">
                <strong>Key Talking Point:</strong> ${q.key_talking_point}
              </div>` : ''}
              ${q.sample_answer ? `
              <details class="text-xs text-gray-300 cursor-pointer">
                <summary class="text-emerald-400 hover:text-emerald-300 font-medium py-1">View Sample Talking Points ▾</summary>
                <p class="mt-2 p-3 bg-white/5 rounded-xl leading-relaxed text-gray-200">${q.sample_answer}</p>
              </details>` : ''}
            </div>
          `).join("")}
        </div>
      </div>` : ''}
    </div>
  `;
}

// =====================================================================
// AI Learning Roadmap for Missing Skills
// =====================================================================
async function generateLearningRoadmapForMissing(missingSkills) {
  if (!missingSkills || missingSkills.length === 0) {
    alert("No missing skills to build a roadmap for!");
    return;
  }

  const modal = document.getElementById("roadmapModal");
  const modalContent = document.getElementById("roadmapModalContent");

  if (modal) modal.classList.remove("hidden");
  if (modalContent) {
    modalContent.innerHTML = `
      <div class="p-8 text-center text-sm text-orange-400 flex flex-col items-center justify-center gap-3">
        <div class="w-8 h-8 border-3 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
        <span>Designing 4-Week Accelerated Roadmap to master: <strong>${missingSkills.slice(0, 4).join(", ")}</strong>...</span>
      </div>
    `;
  }

  try {
    const res = await fetch("/api/learning_roadmap", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        missing_skills: missingSkills,
        target_role: "Target Career Position"
      })
    });

    const data = await res.json();
    if (!data.success) throw new Error(data.error || "Failed to generate roadmap.");

    renderRoadmapModal(data.roadmap, modalContent);

  } catch (err) {
    if (modalContent) {
      modalContent.innerHTML = `
        <div class="p-6 bg-red-500/20 border border-red-500/40 rounded-2xl text-red-300 text-sm">
          ❌ Roadmap Error: ${err.message}
        </div>
      `;
    }
  }
}

function renderRoadmapModal(roadmap, container) {
  if (!container) return;

  const weeks = roadmap.weeks || [];

  container.innerHTML = `
    <div class="space-y-6">
      <div class="flex items-center justify-between pb-4 border-b border-white/10">
        <div>
          <h3 class="text-xl font-bold text-orange-400">4-Week Accelerated Skill Roadmap</h3>
          <p class="text-xs text-gray-400">Master missing skills with hands-on portfolio projects</p>
        </div>
        <button onclick="document.getElementById('roadmapModal').classList.add('hidden')" class="text-gray-400 hover:text-white text-lg">✕</button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        ${weeks.map(w => `
          <div class="p-4 glass rounded-2xl border border-white/10 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold px-2 py-0.5 bg-orange-500/20 text-orange-300 rounded">Week ${w.week_number || ""}</span>
              <span class="text-xs text-gray-400">${w.title || ""}</span>
            </div>
            <div class="text-xs text-gray-300">
              <strong>Focus:</strong> ${w.focus_skills || ""}
            </div>
            <div class="p-2.5 bg-white/5 rounded-xl text-xs text-amber-200">
              <strong>🔨 Mini Project:</strong> ${w.hands_on_project || ""}
            </div>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}

// =====================================================================
// Helpers
// =====================================================================
function copyToClipboard(text, btnElement) {
  navigator.clipboard.writeText(text).then(() => {
    const orig = btnElement.innerHTML;
    btnElement.innerHTML = "✅ Copied!";
    setTimeout(() => { btnElement.innerHTML = orig; }, 1500);
  });
}

function escapeJsString(str) {
  return (str || "").replace(/'/g, "\\'").replace(/"/g, "&quot;").replace(/\n/g, " ");
}
