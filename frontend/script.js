async function uploadResume() {
  const input = document.getElementById("resumeInput");
  const file = input.files[0];
  const resultList = document.getElementById("resultList");
  const jobsContainer = document.getElementById("jobsContainer"); // optional grid

  if (!file) return alert("⚠️ Please select a resume file first!");

  const formData = new FormData();
  formData.append("file", file);

  // UX message
  resultList.innerHTML = `<li>⏳ Analyzing your resume, please wait...</li>`;

  // clear jobs grid if present
  if (jobsContainer) jobsContainer.innerHTML = "";

  try {
    const res = await fetch("/recommend_jobs", { method: "POST", body: formData });
    if (!res.ok) throw new Error(`Server returned ${res.status}`);
    const data = await res.json();


    localStorage.setItem("resume_text", data.resume_text);
    // reset results area
    resultList.innerHTML = "";

    const extracted_skills = data.extracted_skills || [];
    const recommended_jobs =
      data.model_output?.job_roles ||
      data.model_output?.suggested_roles ||
      data.model_output?.recommended_roles ||
      data.model_output?.job_recommendations ||
      data.model_output?.recommended_job_roles ||
      data.model_output?.suggested_job_roles ||
      []; // fallback

    const live_jobs = data.live_jobs || [];

    // Show Extracted Skills
    const skillItem = document.createElement("li");
    skillItem.innerHTML = `<strong>🧠 Extracted Skills:</strong> ${extracted_skills.length ? '' : 'No skills detected'}`;
    if (extracted_skills.length) {
      const span = document.createElement("span");
      span.textContent = extracted_skills.join(", ");
      skillItem.appendChild(span);
    }
    resultList.appendChild(skillItem);

    // Show Recommended Jobs header in resultList (small summary)
    const jobHeader = document.createElement("li");
    jobHeader.innerHTML = `<strong>💼 Recommended Jobs:</strong>`;
    resultList.appendChild(jobHeader);

    // Helper to create a card element (returns DOM node)
    function createJobCard(job) {
     const card = document.createElement("div");
  card.className = "p-6 glass rounded-2xl shadow hover:shadow-xl transition flex flex-col justify-between";


      // Title (string or object)
      const title = document.createElement("h3");
      title.className = "text-lg font-semibold text-orange-600 mb-2";
      title.textContent = job.title || job.name || job.job_title || (typeof job === "string" ? job : "Untitled Role");
      card.appendChild(title);

      // Company/location/extra info
      const meta = document.createElement("p");
      meta.className = "text-gray-300 text-sm  mb-4";
      const parts = [];
      if (job.company) parts.push(job.company);
      if (job.location) parts.push(job.location);
      if (job.salary) parts.push(job.salary);
      meta.textContent = parts.join(" • ") || "";
      card.appendChild(meta);

      // Match score if available
      const score = job.score ?? job.match_score ?? job.match ?? null;
      if (score !== null && score !== undefined) {
        const scoreEl = document.createElement("p");
        scoreEl.className = " text-sm  mb-4";
        scoreEl.innerHTML = `<strong>Match:</strong> ${Math.round(Number(score))}%`;
        card.appendChild(scoreEl);
      }

      // Buttons / link
      const btnWrap = document.createElement("div");
      btnWrap.className = "mt-auto";

      if (job.link) {
        const a = document.createElement("a");
        a.href = job.link;
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        a.className = "pointer-events-auto inline-block bg-orange-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-orange-600";
        a.textContent = "View Job";
        btnWrap.appendChild(a);
      } else {
        const btn = document.createElement("button");
              btn.type = "button";
              btn.className = "explore-job-btn inline-block bg-orange-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-orange-600";
              btn.textContent = "Explore Similar";
              btn.dataset.title = job.title;



 ///////////////////////////////////
        btn.addEventListener("click", ()=>{
          console.log("here")
        })

        // optional: attach click to search or show details
        btnWrap.appendChild(btn);
      }

      card.appendChild(btnWrap);
      return card;
    }

    // If live_jobs exist, prefer them and add to grid / resultList
    if (live_jobs.length > 0) {
      // Add a concise line in resultList
      const liveHeader = document.createElement("li");
      liveHeader.innerHTML = `<em>🔴 Live job listings found (${live_jobs.length})</em>`;
      resultList.appendChild(liveHeader);

      if (jobsContainer) {
        live_jobs.forEach(j => {
          // normalize if server returns primitive
          const jobObj = (typeof j === "string") ? { title: j } : j;
          jobsContainer.appendChild(createJobCard(jobObj));
        });
      } else {
        // fallback to listing links in resultList
        live_jobs.forEach(j => {
          const li = document.createElement("li");
          if (typeof j === "string") {
            li.textContent = `• ${j}`;
          } else {
            const a = document.createElement("a");
            a.href = j.link || "#";
            a.target = "_blank";
            a.rel = "noopener noreferrer";
            a.textContent = j.title || j.name || "Job";
            li.appendChild(a);
            const meta = document.createTextNode(` — ${j.company || "Unknown Company"} (${j.location || "Remote"})${j.salary ? ` • ${j.salary}` : ""}`);
            li.appendChild(meta);
          }
          resultList.appendChild(li);
        });
      }

    } else if (recommended_jobs.length > 0) {
      // No live jobs, show recommended roles
      const recHeader = document.createElement("li");
      recHeader.innerHTML = `<em>🟠 Role suggestions (${recommended_jobs.length})</em>`;
      resultList.appendChild(recHeader);

      if (jobsContainer) {
        recommended_jobs.forEach(j => {
          // recommended_jobs may be strings or objects
          const jobObj = (typeof j === "string") ? { title: j } : j;
          jobsContainer.appendChild(createJobCard(jobObj));
        });
      } else {
        recommended_jobs.forEach(j => {
          const li = document.createElement("li");
          li.textContent = `• ${typeof j === "string" ? j : (j.title || j.name || JSON.stringify(j))}`;
          resultList.appendChild(li);
        });
      }

    } else {
      const li = document.createElement("li");
      li.textContent = "No job recommendations found.";
      resultList.appendChild(li);
    }

  } catch (err) {
    console.error("Error:", err);
    resultList.innerHTML = `<li>❌ Error analyzing resume. Please try again.</li>`;
    if (jobsContainer) {
      jobsContainer.innerHTML = `<div class="p-6 bg-white rounded-2xl shadow">Unable to load job suggestions.</div>`;
    }
  }
}




