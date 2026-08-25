const API_URL = "http://127.0.0.1:8000/api/search";

const form = document.getElementById("search-form");
const industryInput = document.getElementById("industry");
const locationInput = document.getElementById("location");
const searchButton = document.getElementById("search-button");
const statusEl = document.getElementById("status");
const resultsBody = document.getElementById("results-body");

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", isError);
}
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const industry = industryInput.value.trim();
  const location = locationInput.value.trim();
  
  if (!industry || !location) {
      setStatus("Please fill in both fields.", true);
      return;
  }
  
  setStatus("Searching for leads...", false);
  resultsBody.innerHTML = ""; 
  
  try {
      const response = await fetch(`${API_URL}?industry=${encodeURIComponent(industry)}&location=${encodeURIComponent(location)}`);
      
      if (!response.ok) {
          throw new Error(`Server error: ${response.status}`);
      }
      
      const data = await response.json();
      setStatus(`Found ${data.length || 0} leads successfully.`, false);
      // Next step will render them!
      
  } catch (error) {
      console.error(error);
      setStatus("Could not connect to backend. Is main.py running?", true);
  }



function renderEmpty(message) {
  resultsBody.innerHTML = "";
  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = 4;
  cell.className = "empty";
  cell.textContent = message;
  row.appendChild(cell);
  resultsBody.appendChild(row);
}

function renderLeads(leads) {
  resultsBody.innerHTML = "";

  if (!leads.length) {
    renderEmpty("No customers matched that search.");
    return;
  }

  for (const lead of leads) {
    const row = document.createElement("tr");

    const nameCell = document.createElement("td");
    nameCell.textContent = lead.business_name;

    const websiteCell = document.createElement("td");
    const link = document.createElement("a");
    link.href = lead.website;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = lead.website.replace(/^https?:\/\//, "");
    websiteCell.appendChild(link);

    const phoneCell = document.createElement("td");
    phoneCell.textContent = lead.phone;

    const scriptCell = document.createElement("td");
    scriptCell.className = "script";
    scriptCell.textContent = lead.outreach_script;

    row.append(nameCell, websiteCell, phoneCell, scriptCell);
    resultsBody.appendChild(row);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const industry = industryInput.value.trim();
  const location = locationInput.value.trim();

  if (!industry || !location) {
    setStatus("Industry and location are both required.", true);
    return;
  }

  searchButton.disabled = true;
  setStatus("Finding customers…");

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ industry, location }),
    });

    if (!response.ok) {
      throw new Error(`Search failed (${response.status}).`);
    }

    const payload = await response.json();
    renderLeads(payload.leads || []);
    setStatus(`Found ${payload.lead_count} customers in ${payload.location}.`);
  } catch (error) {
    renderEmpty("Could not load customers. Confirm the API is running on port 8000.");
    setStatus(error.message || "Could not reach the lead engine.", true);
  } finally {
    searchButton.disabled = false;
  }
});
