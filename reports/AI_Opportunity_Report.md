# AI Opportunity Report: Cynbit Technologies

Prepared by Diamond Tyagi for the AI/ML Engineer Intern assessment, 31 Oct 2026.

## 1. How I did this research

I used only public information: the pages on cynbit.in (home, products, BitElevate, learning paths, story, contact), Cynbit's public GitHub organisation profile, the Crunchbase profile and the company registration record (MCA data shown on IndiaFilings).

Limits of this research:
- I cannot see Cynbit's internal tools, client work or data. Where I assume something, I say "assumption".
- Numbers like "88% placement" are Cynbit's own claims. I have not verified them.

## 2. Who Cynbit is (what the public pages say)

- **Company:** Cynbit Technologies Private Limited, Jaipur, Rajasthan. Registered on 2 April 2024 (MCA record).
- **Services:** AI agents and workflow automation, LLM integrations, voice agents, web and mobile development, backend, cloud, legacy migration, digital marketing, technical SEO, CRM automation.
- **Own products:**
  - **Cynbit Studio**: learning and career platform with adaptive paths, AI coding missions, AI code evaluation and AI mentor support.
  - **TenantEase**: property, tenant, rent and occupancy management.
  - **Revio**: review and reputation management for multi-location businesses, with AI review sync and an AI response engine.
- **BitElevate:** training and internship programme for engineering students with 16 learning tracks (full stack, AI, ML, data science, cloud, cybersecurity and others). BitElevate 2.0 started its first batch with the University of Rajasthan's Department of Lifelong Learning and Manav Seva Trust.

So Cynbit has three kinds of business: a services business for clients, a set of SaaS products, and a training programme. Each one produces data and repeated work, which is where AI/ML usually helps.

## 3. Opportunities I found

Effort and impact are my own judgement, not measured numbers.

| # | Area | Opportunity | ML / AI technique | Data needed | Effort | Impact |
|---|------|-------------|-------------------|-------------|--------|--------|
| A | Cynbit Studio | Fast, consistent code feedback (tests first) plus detection of learners who are struggling | Rule and test based evaluation, decision tree classifier, LLM only for explanations | Learner attempt logs | Low to medium | High |
| B | Revio | Spot branches whose ratings are dropping and group complaints by topic; quality checks before an AI reply is posted | Sentiment and topic classification, anomaly detection on rating trends | Reviews and ratings | Medium | High |
| C | TenantEase | Predict late rent, sort maintenance requests by urgency, extract details from lease and KYC documents | Classification, text classification, OCR plus LLM extraction | Payment history, request text, documents | Medium to high | High |
| D | BitElevate | Recommend a track for each student and warn early when a student is falling behind | Recommender, classification | Cohort attendance, scores, outcomes | Medium | Medium |
| E | Sales and services | Sort inbound inquiries, retrieve similar past projects, draft a first proposal | Text classification, retrieval (RAG), LLM drafting | Past inquiries and proposals | Medium | Medium to high |
| F | Marketing | Find content gaps for the technical SEO service and draft first versions for review | Keyword clustering, LLM drafting | Search and site data | Low | Medium |

## 4. Which one I chose and why: A, Cynbit Studio Code Coach

1. **It is already part of what Cynbit promises.** The products page lists AI code evaluation and AI mentor support, so this improves a visible feature instead of inventing a new product.
2. **Cost and consistency.** If every submission is sent to an LLM, the cost grows with every learner and two identical answers can get different feedback. Running tests first is free, instant and always the same. The LLM is only needed for the explanation after a failure.
3. **The data comes for free.** Every Run click creates data: attempts, time, tests passed, hints used. That is exactly what a small ML model needs.
4. **It is easy to measure.** Time to feedback, mission completion rate, hints used before passing, and mentor hours saved.
5. **It can grow.** The same pipeline can serve BitElevate students (assumption: they use Studio).

Honest note: I do not know how Studio evaluates code today. My proposal is a layered design that could sit next to, or inside, the existing feature.

## 5. What the proof of concept shows

A Streamlit app where a learner:
- picks one of 4 missions (levels 1 to 3),
- writes Python code and presses Run,
- sees which tests passed or failed and extra tips (for example "loop inside a loop"),
- can open 3 hints, from vague to specific,
- sees an estimate of whether they need extra help, with a suggestion to go easier or harder.

Details of how it works are in the Technical Approach Report.

## 6. Risks and how to handle them

| Risk | Handling |
|------|----------|
| Student code can be harmful when executed | Run in a sandbox: container, no network, memory and time limits. The PoC only uses a separate process with a time limit. |
| ML flags a learner wrongly | The flag only suggests a mission or mentor help. It never blocks or grades anyone. Mentors can see the decision rules. |
| Student data privacy | Collect only what is needed, get consent, follow India's Digital Personal Data Protection Act 2023. |
| Tests miss bad style or hardcoded answers | Add hidden tests, and later an LLM or mentor review for style. |
| Sample data does not match reality | Retrain on real logs before trusting any number. |

## 7. How I would measure success

- Median time from Run to feedback (target: under 2 seconds for test-based feedback).
- Share of learners who finish a mission within a week (before and after).
- Share of flagged learners who really dropped off or asked a mentor (precision), and share of struggling learners that were flagged (recall).
- Mentor hours spent per learner.

## 8. Next steps if Cynbit wants to continue

1. Add event logging to Studio and collect 4 to 6 weeks of real attempts.
2. Define the real label for "struggling" (for example, no completion within 7 days or a mentor request).
3. Retrain, compare with simple baselines, and run a small pilot with one BitElevate batch.
4. Add the LLM explanation layer with strict rules (never reveal the full solution).
