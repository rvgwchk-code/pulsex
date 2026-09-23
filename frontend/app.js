const API = window.PULSEX_API_URL || "";
let verificationId = "";
let accessToken = localStorage.getItem("pulsex_access_token") || "";
const $ = (id) => document.getElementById(id);

const demoCompanies = [
  { id: "company-pulsex", name: "PulseX Labs", domain: "pulsex.example", status: "approved" },
  { id: "company-northstar", name: "Northstar Systems", domain: "northstar.example", status: "approved" },
];
const demoReviews = {
  "company-pulsex": [{ id: "review-demo", company_id: "company-pulsex", rating: 4, role: "Product designer", location: "Remote", tenure_range: "1-2 years", pros: "Clear product direction and thoughtful peers.", cons: "Priorities can change quickly.", advice: "Ask how product decisions are made day to day.", status: "approved", verified: true, created_at: "2026-01-15T00:00:00Z" }],
  "company-northstar": [],
};

function demoRequest(path, options = {}) {
  if (path.startsWith("/companies?") && options.method !== "POST") {
    const query = new URLSearchParams(path.split("?")[1]).get("query")?.toLowerCase() || "";
    return Promise.resolve(demoCompanies.filter((company) => !query || `${company.name} ${company.domain}`.toLowerCase().includes(query)));
  }
  const companyMatch = path.match(/^\/companies\/([^/]+)$/);
  if (companyMatch) {
    const company = demoCompanies.find((item) => item.id === companyMatch[1]);
    const reviews = demoReviews[companyMatch[1]] || [];
    return Promise.resolve({ ...company, review_count: reviews.length, average_rating: reviews.length ? 4 : null, verified_review_count: reviews.length });
  }
  const reviewsMatch = path.match(/^\/companies\/([^/]+)\/reviews$/);
  if (reviewsMatch && options.method !== "POST") return Promise.resolve(demoReviews[reviewsMatch[1]] || []);
  if (path.endsWith("/verification")) return Promise.resolve({ id: "demo-verification", status: "verified" });
  if (path === "/auth/register" || path === "/auth/login") return Promise.resolve({ access_token: "github-pages-demo", role: "employee", user_id: "demo-user" });
  if (options.method === "POST") return Promise.resolve({ id: "demo-submission", status: "pending" });
  return Promise.reject(new Error("Demo data unavailable"));
}

async function request(path, options = {}) {
  if (!API) return demoRequest(path, options);
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
  const response = await fetch(`${API}${path}`, { ...options, headers });
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
async function authenticate(path) { try { const result = await request(path, { method: "POST", body: JSON.stringify({ email: $("auth-email").value, password: $("auth-password").value }) }); accessToken = result.access_token; localStorage.setItem("pulsex_access_token", accessToken); $("auth-status").textContent = "Signed in. Your public review will not include your account identity."; } catch (error) { $("auth-status").textContent = error.message; } }
$("register-button").addEventListener("click", () => authenticate("/auth/register"));
$("login-button").addEventListener("click", () => authenticate("/auth/login"));
$("verify-button").addEventListener("click", async () => { if (!accessToken) { $("form-status").textContent = "Create an account or sign in first."; return; } try { const result = await request(`/companies/${$("review-company").value}/verification`, { method: "POST", body: JSON.stringify({ method: "test-mode" }) }); verificationId = result.id; $("review-fields").hidden = false; $("form-status").textContent = "Verified for this prototype. Your identity will not appear publicly."; } catch (error) { $("form-status").textContent = error.message; } });
$("review-form").addEventListener("submit", async (event) => { event.preventDefault(); try { await request(`/companies/${$("review-company").value}/reviews`, { method: "POST", body: JSON.stringify({ verification_id: verificationId, rating: Number($("rating").value), role: $("role").value, location: $("location").value, tenure_range: $("tenure").value, pros: $("pros").value, cons: $("cons").value, advice: $("advice").value }) }); $("form-status").textContent = "Submitted for moderation. Thank you for adding signal."; event.target.reset(); $("review-fields").hidden = true; } catch (error) { $("form-status").textContent = error.message; } });
loadCompanies().catch((error) => { $("result-count").textContent = "Unavailable"; $("company-list").innerHTML = `<p>${error.message}</p>`; });