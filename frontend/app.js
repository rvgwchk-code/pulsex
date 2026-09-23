const API = "http://localhost:8000";
let verificationId = "";
const $ = (id) => document.getElementById(id);

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, { headers: { "Content-Type": "application/json", ...(options.headers || {}) }, ...options });
  if (!response.ok) throw new Error((await response.json()).detail || "Something went wrong");
  return response.json();
}

function renderCompanies(companies) {
  $("result-count").textContent = `${companies.length} companies`;
  $("company-list").innerHTML = companies.map((company) => `<button class="company-card" data-company="${company.id}"><h3>${company.name}</h3><p>${company.domain}</p></button>`).join("");
  $("review-company").innerHTML = companies.map((company) => `<option value="${company.id}">${company.name}</option>`).join("");
  document.querySelectorAll("[data-company]").forEach((card) => card.addEventListener("click", () => showCompany(card.dataset.company)));
}

async function loadCompanies(query = "") { renderCompanies(await request(`/companies?query=${encodeURIComponent(query)}`)); }
async function showCompany(id) {
  const [company, reviews] = await Promise.all([request(`/companies/${id}`), request(`/companies/${id}/reviews`)]);
  $("company-detail").hidden = false;
  $("company-detail").innerHTML = `<p class="eyebrow">Company page</p><h2>${company.name}</h2><div class="detail-meta"><span>${company.review_count} approved reviews</span><span>${company.average_rating ?? "-"} average rating</span><span>${company.verified_review_count} verified</span></div><div class="review-list">${reviews.length ? reviews.map((review) => `<article class="review"><div class="review-header"><span>${"★".repeat(review.rating)}${"☆".repeat(5 - review.rating)}</span><small>${review.role} · ${review.location} · ${review.tenure_range}</small></div><p><strong>Pros:</strong> ${review.pros}</p><p><strong>Cons:</strong> ${review.cons}</p><p><strong>Advice:</strong> ${review.advice}</p></article>`).join("") : "<p>No approved reviews yet. Be the first verified voice.</p>"}</div>`;
  $("company-detail").scrollIntoView({ behavior: "smooth", block: "start" });
}

$("search-form").addEventListener("submit", (event) => { event.preventDefault(); loadCompanies($("company-query").value); });
$("verify-button").addEventListener("click", async () => { try { const result = await request(`/companies/${$("review-company").value}/verification`, { method: "POST", body: JSON.stringify({ method: "test-mode" }) }); verificationId = result.id; $("review-fields").hidden = false; $("form-status").textContent = "Verified for this prototype. Your identity will not appear publicly."; } catch (error) { $("form-status").textContent = error.message; } });
$("review-form").addEventListener("submit", async (event) => { event.preventDefault(); try { await request(`/companies/${$("review-company").value}/reviews`, { method: "POST", body: JSON.stringify({ verification_id: verificationId, rating: Number($("rating").value), role: $("role").value, location: $("location").value, tenure_range: $("tenure").value, pros: $("pros").value, cons: $("cons").value, advice: $("advice").value }) }); $("form-status").textContent = "Submitted for moderation. Thank you for adding signal."; event.target.reset(); $("review-fields").hidden = true; } catch (error) { $("form-status").textContent = error.message; } });
loadCompanies().catch((error) => { $("result-count").textContent = "API offline"; $("company-list").innerHTML = `<p>${error.message}. Start FastAPI on port 8000 to explore PulseX.</p>`; });