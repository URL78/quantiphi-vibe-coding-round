# GitHub Developer Portfolio — Requirements Specification

**Project:** AI-Powered GitHub Developer Portfolio  
**Document type:** Product and software requirements  
**Status:** MVP specification for implementation by an AI coding agent

## 1. Product vision

Build a web application that accepts a GitHub username and turns the user's public GitHub data into:

1. An interactive developer analytics dashboard.
2. A professional personal-branding portfolio.
3. A job-description compatibility analysis based on the languages used in the user's cached repositories.
4. Repository understanding and interview-preparation assistance powered by DeepWiki MCP.

The application must be a complete, working end-to-end MVP. Prefer simple, understandable implementation over unnecessary infrastructure.

## 2. Scope and priority

### 2.1 Explicit requirements from the Quantiphi problem statement

These requirements are mandatory and must not be omitted or replaced by optional enhancements.

| ID | Requirement | Expected behavior |
|---|---|---|
| QP-01 | Contribution graph | Display a calendar-style heatmap of daily GitHub contributions, with color intensity representing contribution count. |
| QP-02 | Repository cards | Display repositories with star count, fork count, primary language tag, and short description. |
| QP-03 | Profile header | Display profile summary, follower count, total stars, and a Top Languages pie chart. |
| QP-04 | GitHub API integration | Fetch user-specific GitHub data using GitHub REST and/or GraphQL APIs. |
| QP-05 | SQLite caching engine | Cache repository metadata and user settings locally to reduce repeated API calls, improve response time, and help manage API rate limits. |
| QP-06 | Tech Stack Compatibility / Vibe Check | Allow the user to input a job description. The backend must compare keywords in that job description against the languages used in the user's **cached repositories** and generate a **Match Percentage badge at the top of the profile**. |

**Critical interpretation of QP-06:** This is an explicitly required feature. It must be implemented as part of the MVP, not treated as an optional enhancement. The matching evidence is the primary programming-language data stored for the user's cached repositories. Do not claim that a repository uses FastAPI, Docker, PostgreSQL, Redis, etc. merely because its primary language is Python. Technologies other than repository languages may be shown as unverified/not assessed, but must not be counted as matched by this required language-based algorithm.

### 2.2 Additional product features agreed for the MVP

| ID | Feature | Priority | Description |
|---|---|---|---|
| ADD-01 | Professional portfolio presentation | MVP | Present the GitHub profile, statistics, contributions, and selected projects in a polished portfolio view. |
| ADD-02 | Featured repositories | MVP | Let a user select and order repositories to highlight. |
| ADD-03 | Rule-based skill-gap suggestions | MVP / lightweight | Give practical recommendations based on unmatched recognized language requirements. Do not add a separate LLM provider for this. |
| ADD-04 | DeepWiki repository assistant | Additional | Use DeepWiki MCP to retrieve repository documentation and answer questions about a public repository. |
| ADD-05 | DeepWiki interview preparation | Additional | Use repository context to generate technical interview questions and provide answer feedback where supported by DeepWiki's capabilities. |
| ADD-06 | Basic dashboard preferences | Lightweight | Support a light/dark theme and persist appropriate settings. |

### 2.3 Explicitly out of scope for this MVP

Do not add these unless the project owner explicitly approves them:

- Mandatory user registration, password authentication, or GitHub OAuth.
- Private repository access.
- Microservices.
- Redis or another external cache.
- Docker/Kubernetes deployment infrastructure.
- Vector database, embeddings, custom RAG pipeline, LangChain, or LangGraph.
- A separate paid LLM API or a second AI provider.
- Complex admin panels, recruitment workflows, or job application tracking.
- Persistent chat/interview history unless later required.

## 3. Actors and user types

- **Developer/visitor:** Enters a public GitHub username, views analytics and portfolio, analyzes a job description, and optionally uses DeepWiki features.
- **GitHub REST/GraphQL APIs:** External source of profile, repository, and contribution data.
- **DeepWiki MCP service:** External repository documentation and question-answering service.

The MVP does not require an authenticated application account. Public portfolio data is identified by GitHub username. Do not imply that username-only settings are private or securely owned.

## 4. Functional requirements

### 4.1 GitHub profile integration

- **FR-01:** Provide a username input on the landing page.
- **FR-02:** Trim whitespace and reject an empty username.
- **FR-03:** Fetch public GitHub profile data through the backend.
- **FR-04:** Fetch the user's public repositories.
- **FR-05:** Fetch daily contribution data using GitHub GraphQL where available.
- **FR-06:** Show loading, success, empty, and error states.
- **FR-07:** Provide a refresh action to request fresh data.
- **FR-08:** Preserve cached data if a refresh fails.

### 4.2 Dashboard analytics

- **FR-09:** Display avatar, username, bio, GitHub URL, followers, following, and public repository count where available.
- **FR-10:** Display total stars across the user's fetched public repositories.
- **FR-11:** Display total forks where available.
- **FR-12:** Display a contribution heatmap with date and count on hover or selection.
- **FR-13:** Calculate current and longest contribution streak from daily contribution data.
- **FR-14:** Display repository cards with name, description, primary language, stars, forks, and GitHub URL.
- **FR-15:** Support repository sorting by stars, updated date, or name.
- **FR-16:** Aggregate repositories by primary language and display a pie/doughnut chart.
- **FR-17:** Clearly document that initial language distribution is based on repository counts, not source-code line counts.

### 4.3 Backend and SQLite caching

- **FR-18:** Route external GitHub requests through FastAPI; never call GitHub directly from browser code.
- **FR-19:** Normalize GitHub responses into application data structures.
- **FR-20:** Persist profile and repository metadata in SQLite.
- **FR-21:** Persist daily contribution records if retrieved.
- **FR-22:** Persist user settings and featured repository selections.
- **FR-23:** Check cache validity before making GitHub requests.
- **FR-24:** Use configurable TTL values and synchronization timestamps.
- **FR-25:** Use upsert/update behavior to avoid duplicate repository and contribution records.
- **FR-26:** On GitHub failure, return stale cached data with an explicit stale-data indicator if available.
- **FR-27:** If no cached data exists and GitHub fails, return a meaningful error.

Suggested initial TTLs (configurable): profile/repositories 1 hour; contributions 6 hours. Settings do not expire automatically.

### 4.4 Mandatory Tech Stack Compatibility / Vibe Check

- **FR-28:** Provide a multiline job-description input.
- **FR-29:** Reject empty or excessively long input with a clear validation message.
- **FR-30:** Extract recognized technical keywords using a predefined, maintainable skill/language dictionary.
- **FR-31:** Normalize language names and aliases (for example, `C++` and `cpp`) to canonical names.
- **FR-32:** Retrieve the user's cached repository language data from SQLite for matching.
- **FR-33:** Compare recognized programming-language requirements in the job description against the distinct primary languages represented in the user's cached repositories.
- **FR-34:** Return matched and unmatched recognized languages.
- **FR-35:** Calculate a match percentage on the backend.
- **FR-36:** Display the Match Percentage badge prominently at the top of the profile/dashboard, as explicitly required by the problem statement.
- **FR-37:** Display a breakdown explaining the score and allow another job description to be analyzed.
- **FR-38:** Handle a job description with no recognized languages without division-by-zero; show “Not enough recognized language requirements to calculate a score” or equivalent rather than inventing a percentage.

**Required scoring definition for the MVP:**

`match_percentage = (number_of_matched_required_languages / number_of_distinct_recognized_required_languages) * 100`

Use distinct canonical language names in the denominator. A language is matched if it appears as a primary language in at least one of the user's cached repositories. Round only for display; retain a numeric value in the API response.

**Important semantics:**

- The input is a full job description, but the required comparison is against languages used in cached repositories.
- Do not count frameworks, databases, cloud platforms, tools, or general skills as matched merely because they appear in the job description.
- Optionally return these as `unassessed_keywords` so the UI can explain that the MVP evaluates programming-language evidence only.
- This is a GitHub-evidence compatibility estimate, not proof of the user's actual skills.
- If the user has no cached repositories, do not silently treat every language as missing without explaining that repository evidence is unavailable. Return a clear state and prompt the user to sync their profile.

### 4.5 Career recommendations

- **FR-39:** Generate lightweight, deterministic recommendations from unmatched recognized language requirements.
- **FR-40:** Make it clear that recommendations are suggestions, not verified facts.
- **FR-41:** Do not add an external LLM dependency for this module.

### 4.6 DeepWiki repository assistant

- **FR-42:** Allow the user to select one of their public repositories.
- **FR-43:** Use a dedicated backend integration to connect to DeepWiki MCP.
- **FR-44:** Support retrieving documentation structure and contents where available.
- **FR-45:** Support asking a natural-language question about a repository.
- **FR-46:** Handle unindexed repositories, timeouts, MCP errors, and unavailable service with a retryable AI-only error.
- **FR-47:** Keep the GitHub dashboard functional if DeepWiki is unavailable.
- **FR-48:** Do not fabricate repository details if DeepWiki has insufficient information.

Use the documented DeepWiki MCP tools, such as `read_wiki_structure`, `read_wiki_contents`, and `ask_question`, through an MCP client. Do not assume the MCP tools are ordinary REST endpoints.

### 4.7 Interview preparation

- **FR-49:** Generate repository-specific technical questions using available DeepWiki context.
- **FR-50:** Allow the user to submit an answer.
- **FR-51:** Request feedback grounded in repository context when supported.
- **FR-52:** Clearly communicate when the repository documentation is insufficient.
- **FR-53:** Keep interview state in frontend memory for the MVP; persistent interview history is not required.

### 4.8 Personal branding and settings

- **FR-54:** Provide a professional portfolio view identified by GitHub username.
- **FR-55:** Allow selection and ordering of featured repositories.
- **FR-56:** Provide a shareable route such as `/portfolio/{username}`.
- **FR-57:** Provide a basic theme preference.
- **FR-58:** Avoid exposing internal data or treating username-only preferences as private.

## 5. Non-functional requirements

- **NFR-01 Performance:** Use cache-first retrieval; avoid unnecessary external requests; paginate or limit large repository lists.
- **NFR-02 Reliability:** Handle external API errors, timeouts, rate limits, empty profiles, and missing fields gracefully.
- **NFR-03 Security:** Keep API tokens and secrets on the backend in environment variables; never commit secrets; validate inputs; avoid leaking stack traces.
- **NFR-04 Usability:** Provide clear navigation, responsive layouts, loading indicators, empty states, and understandable error messages.
- **NFR-05 Maintainability:** Separate API routes, services, database models, schemas, and external integrations.
- **NFR-06 Extensibility:** Keep GitHub and DeepWiki integrations isolated so they can be changed without rewriting business logic.
- **NFR-07 Data accuracy:** Use real source data; do not fabricate contribution activity, repository metadata, or skill evidence.
- **NFR-08 AI quality:** Ground repository answers in DeepWiki results; state limitations when context is missing.
- **NFR-09 Portability:** Document setup and environment variables; application should run locally with SQLite and no separately managed database server.
- **NFR-10 Testing:** Test core API routes, cache hit/miss/expiry, compatibility calculations, validation, and external-service failure paths.

## 6. Technology stack

| Layer/module | Technology |
|---|---|
| Frontend | React + Vite |
| Styling | Tailwind CSS |
| Routing | React Router |
| Server state | TanStack Query |
| HTTP client | Axios |
| Charts | Recharts |
| Icons | Lucide React |
| Backend | Python + FastAPI |
| Backend HTTP | HTTPX |
| Validation | Pydantic |
| Database | SQLite |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| GitHub integration | REST API + GraphQL API |
| DeepWiki integration | MCP over HTTP using a compatible Python MCP client |
| Backend tests | Pytest |
| Frontend tests | Vitest + React Testing Library |
| API documentation | FastAPI OpenAPI/Swagger UI |
| Version control | Git + GitHub |

## 7. Architecture constraints

- Use a **modular monolith**, not microservices.
- Frontend communicates with FastAPI through REST endpoints.
- FastAPI owns business logic, calculations, validation, caching, and external API orchestration.
- SQLite is the only required database.
- GitHub API credentials remain on the backend.
- DeepWiki is accessed only through a dedicated backend integration.
- AI features are optional and must not block the core dashboard.
- Do not introduce Redis, Docker, Kubernetes, vector databases, custom RAG, LangChain, or a separate LLM provider in the MVP.
- Prefer understandable, working code over speculative abstractions.

## 8. Definition of Done

The MVP is complete when:

1. A user can enter a public GitHub username and view real profile data.
2. Repository cards show required metadata.
3. Contribution heatmap and streaks use real contribution data when available.
4. Profile header shows followers, total stars, top languages, and the **Tech Stack Compatibility Match Percentage badge** after a job description is analyzed.
5. The compatibility backend compares job-description language keywords against languages in cached repositories.
6. SQLite caching works, including cache hit, miss, refresh, and stale fallback.
7. Featured repositories and portfolio view work.
8. DeepWiki assistant is integrated where the public repository is supported; failure does not break the dashboard.
9. Interview preparation works to the extent supported by DeepWiki.
10. Setup instructions, environment example files, and tests are included.
