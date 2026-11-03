# GitHub Developer Portfolio — User Stories and Acceptance Criteria

**Purpose:** Define user-visible behavior and testable acceptance criteria for the AI coding agent.

## Product assumptions

- Public GitHub repositories only for the MVP.
- No mandatory application login or GitHub OAuth.
- A user is identified by GitHub username.
- SQLite stores cached GitHub data and settings.
- DeepWiki MCP powers repository explanation and interview preparation.
- The mandatory Vibe Check compares job-description language keywords against languages in cached repositories.
- The application is a modular monolith.

## Epic 1 — GitHub profile integration

### US-01: Enter a GitHub username

**As a developer, I want to enter my GitHub username so that I can generate my developer dashboard and portfolio.**

Acceptance criteria:
- Landing page contains a username field and submit action.
- Trim leading/trailing whitespace.
- Reject empty input.
- Show loading state during synchronization.
- On success, navigate to or render the user's dashboard.
- On invalid/nonexistent username, show a clear error and allow correction.
- Handle network failures and GitHub rate limits without crashing.

### US-02: Retrieve profile information

**As a developer, I want my public GitHub profile information fetched automatically so that I do not need to enter it manually.**

Acceptance criteria:
- Retrieve username, name, avatar, bio, profile URL, followers, following, and public repository count where available.
- Display optional fields gracefully when absent.
- All GitHub requests go through the backend.
- Show a link to the original GitHub profile.

### US-03: Refresh profile data

**As a developer, I want to refresh my GitHub information so that the dashboard can reflect newer activity.**

Acceptance criteria:
- Provide a refresh control.
- Force a GitHub fetch rather than returning a valid cache unchanged.
- Update SQLite only after successful retrieval.
- Display last successful synchronization time.
- If refresh fails, preserve previous cache and show a warning.

## Epic 2 — Analytics dashboard

### US-04: View profile statistics

**As a developer, I want to see my profile statistics in one place so that I can understand my GitHub presence.**

Acceptance criteria:
- Display followers, following, public repository count, and total stars.
- Total stars are calculated from the user's fetched public repositories.
- Calculations are performed by backend services.
- Missing data is not silently presented as a verified zero.

### US-05: View contribution heatmap

**As a developer, I want to see a calendar heatmap of daily contributions so that I can understand my coding activity over time.**

Acceptance criteria:
- One cell represents one calendar date.
- Color intensity reflects daily contribution count.
- Hover/selection shows date and count.
- Empty days are represented correctly.
- Use GitHub contribution data, not fabricated sample data.
- If contribution data is unavailable, show a useful unavailable state.

### US-06: View coding streaks

**As a developer, I want to see current and longest contribution streaks so that I can understand consistency.**

Acceptance criteria:
- Calculate streaks from daily contribution counts.
- A zero-contribution day breaks a streak.
- Display current and longest streak.
- Handle profiles with no contributions.
- Define current streak consistently, including the case where the latest contribution was yesterday.

### US-07: View repository cards

**As a developer, I want to see my repositories as cards so that visitors can quickly understand my projects.**

Acceptance criteria:
- Each card shows name, description, primary language, stars, forks, and repository URL.
- Clicking the card/link opens the GitHub repository.
- Missing descriptions and languages have clear fallback labels.
- Only public repositories are included in the MVP.

### US-08: Sort repositories

**As a developer, I want to sort repositories so that I can find or showcase important projects.**

Acceptance criteria:
- Support sorting by stars, recently updated, and name.
- Sort order is deterministic.
- Empty repository lists are handled.

### US-09: View top languages

**As a developer, I want to see the languages represented in my repositories so that visitors can understand my technical background.**

Acceptance criteria:
- Aggregate by each repository's primary language.
- Display a pie/doughnut chart and language names/percentages.
- Initial percentage is based on repository count, not lines of code.
- Repositories with no language are excluded from the language denominator and are not mislabeled.
- Show an empty state when no language data exists.

## Epic 3 — Backend, database, and caching

### US-10: Retrieve GitHub data through the backend

**As a system, I want GitHub requests handled by FastAPI so that credentials and business logic are not exposed in browser code.**

Acceptance criteria:
- React calls FastAPI.
- FastAPI calls GitHub REST/GraphQL.
- Tokens are read from backend environment variables.
- Normalize external response data before returning it.
- Return structured errors.

### US-11: Cache profile and repositories

**As a system, I want profile and repository data stored in SQLite so that repeated requests can be served efficiently.**

Acceptance criteria:
- Store profile and repository metadata.
- Associate records with the correct user.
- Store synchronization timestamps.
- Check valid cache before making external requests.
- Use upsert/update behavior to avoid duplicates.

### US-12: Expire and refresh cache

**As a system, I want cached data to expire after a configurable TTL so that stale data is refreshed appropriately.**

Acceptance criteria:
- Suggested initial TTL: profile/repositories 1 hour; contributions 6 hours.
- Valid cache returns without unnecessary GitHub requests.
- Expired cache triggers a refresh.
- Failed refresh preserves old data.
- Stale fallback is explicitly marked as stale.

### US-13: Save dashboard settings

**As a developer, I want basic settings saved so that my dashboard preferences are retained.**

Acceptance criteria:
- Store theme preference.
- Store featured repository selection/order.
- Associate settings with GitHub username for this no-login MVP.
- Do not represent username-only settings as private or securely owned.

## Epic 4 — Mandatory Tech Stack Compatibility / Vibe Check

> This epic is explicitly required by the Quantiphi problem statement and is a core acceptance criterion for the submission.

### US-14: Enter a job description

**As a developer, I want to paste a job description so that I can evaluate its language requirements against my GitHub repositories.**

Acceptance criteria:
- Provide multiline input.
- Reject empty input.
- Enforce a reasonable maximum length.
- Provide an Analyze action and loading state.

### US-15: Extract and normalize language keywords

**As a system, I want to extract recognized programming-language keywords from the job description so that they can be compared consistently.**

Acceptance criteria:
- Use a predefined language/alias dictionary.
- Normalize case and aliases (e.g. `cpp` to `C++`).
- Deduplicate canonical language names.
- Ignore general words and non-language technologies for the required score.
- Optionally return non-language technical terms separately as unassessed keywords.

### US-16: Compare job-description languages against cached repository languages

**As a developer, I want the backend to compare job-description language keywords against languages in my cached repositories so that the score is based on actual GitHub evidence.**

Acceptance criteria:
- Read repository language fields from SQLite.
- Use distinct canonical primary languages across the user's cached repositories.
- Compare these against distinct recognized programming languages extracted from the job description.
- Return matched and unmatched languages.
- Do not count FastAPI, Docker, PostgreSQL, Redis, Kubernetes, or other non-language technologies as matched merely because they are mentioned in the job description.
- If there are no cached repositories, prompt the user to synchronize GitHub data.

### US-17: Calculate the Match Percentage

**As a developer, I want a Match Percentage so that I can quickly understand how well my GitHub language evidence aligns with a job description.**

Acceptance criteria:
- Calculation happens in the backend.
- Formula: matched distinct required languages / all distinct recognized required languages × 100.
- Score is between 0 and 100.
- No recognized language requirements results in a clear “not enough information” state, not division by zero.
- Return numeric score and matched/unmatched breakdown.

### US-18: Display the Vibe Check badge prominently

**As a developer, I want the Match Percentage badge displayed at the top of my profile/dashboard so that compatibility is immediately visible.**

Acceptance criteria:
- After analysis, show a prominent Match Percentage badge at the top of the profile/dashboard.
- Show matched and unmatched languages nearby.
- Allow another job description to be analyzed.
- Clearly label the score as GitHub-evidence-based, not a definitive measure of skill.
- Preserve profile analytics when a new analysis is performed.

## Epic 5 — Rule-based career assistance

### US-19: Receive skill recommendations

**As a developer, I want practical suggestions for unmatched language requirements so that I can improve my portfolio.**

Acceptance criteria:
- Use compatibility analysis results.
- Generate deterministic recommendations from backend rules.
- Do not require an external LLM.
- Label recommendations as suggestions, not verified facts.

### US-20: View an improvement plan

**As a developer, I want missing language requirements and suggested activities grouped together so that I know what to work on next.**

Acceptance criteria:
- Display missing languages and associated suggestions.
- Show a useful state when there are no identified gaps.
- Allow the user to revisit or run another analysis.

## Epic 6 — DeepWiki repository assistant

### US-21: Select a repository

**As a developer, I want to select one of my public repositories so that I can ask questions about its codebase.**

Acceptance criteria:
- List repositories already retrieved for the user.
- Identify the repository by owner and repository name.
- Allow selection.
- Handle repositories that are not available in DeepWiki.

### US-22: Retrieve DeepWiki documentation

**As a system, I want to retrieve repository documentation through DeepWiki MCP so that I do not need to build a custom indexing/RAG pipeline.**

Acceptance criteria:
- Dedicated backend DeepWiki integration.
- Use supported MCP tools such as `read_wiki_structure` and `read_wiki_contents`.
- Handle unavailable/unindexed repositories, timeouts, and MCP errors.
- Keep DeepWiki failures isolated from core dashboard functionality.

### US-23: Ask repository questions

**As a developer, I want to ask natural-language questions about a selected repository so that I can understand its architecture and implementation.**

Acceptance criteria:
- Provide chat-like question input and answer display.
- Send repository owner/name and question to backend.
- Backend invokes DeepWiki `ask_question` through MCP.
- Maintain selected repository context in the UI.
- Show loading and retryable error states.
- Do not fabricate answers if documentation is insufficient.

### US-24: Generate project explanation

**As a developer, I want a structured explanation of my selected repository so that I can present it professionally.**

Acceptance criteria:
- Generate overview and component/architecture explanation from available DeepWiki content.
- Identify technologies only when supported by retrieved context.
- Show a limitation message if documentation is insufficient.

## Epic 7 — Interview preparation

### US-25: Generate repository-based interview questions

**As a developer, I want technical questions based on my repository so that I can prepare to explain my own project.**

Acceptance criteria:
- Use DeepWiki repository context.
- Generate questions about architecture, design choices, and implementation.
- Avoid claiming questions are based on code areas that DeepWiki did not document.

### US-26: Practice a mock interview

**As a developer, I want to answer one question at a time so that I can practice explaining my project.**

Acceptance criteria:
- Display one question at a time.
- Accept a text answer.
- Allow next question and end session.
- Frontend state is sufficient for MVP session state.

### US-27: Receive answer feedback

**As a developer, I want feedback grounded in repository context so that I can improve my explanations.**

Acceptance criteria:
- Compare answer with available repository context.
- Identify good points and omissions.
- Suggest a clearer answer.
- Explain when there is insufficient context for evaluation.

## Epic 8 — Personal branding

### US-28: View a professional portfolio

**As a developer, I want my GitHub information presented as a polished portfolio so that I can showcase my developer identity.**

Acceptance criteria:
- Display profile introduction, statistics, contributions, languages, and featured projects.
- Provide GitHub links.
- Responsive layout.
- Include the Vibe Check Match Percentage badge after an analysis exists.

### US-29: Feature repositories

**As a developer, I want to select and order featured repositories so that I can highlight my best projects.**

Acceptance criteria:
- Select/unselect repositories.
- Set display order.
- Persist selections.
- Handle repositories that are no longer available.

### US-30: Share portfolio

**As a developer, I want a shareable portfolio URL so that recruiters and developers can view my public profile.**

Acceptance criteria:
- Route such as `/portfolio/{username}`.
- Public visitor does not need to log in.
- Only public profile and portfolio data are returned.
- Do not expose internal settings or sensitive configuration.

## Epic 9 — Preferences

### US-31: Change theme

**As a developer, I want light and dark themes so that I can choose my preferred appearance.**

Acceptance criteria:
- Theme toggle.
- Persist preference (SQLite or browser storage, consistent with chosen implementation).
- Restore preference on revisit.

### US-32: Restore preferences

**As a developer, I want my preferences restored for the same username so that I do not need to configure them repeatedly.**

Acceptance criteria:
- Retrieve settings.
- Use defaults when no settings exist.
- Do not imply username-only preferences are private.

## Epic 10 — Reliability and edge cases

### US-33: GitHub API failure

**As a developer, I want cached data to remain available if GitHub is unavailable so that I can still view my dashboard.**

Acceptance criteria:
- Try cache fallback after external failure.
- Mark stale data clearly.
- If no cache exists, show a meaningful error.
- Do not crash the application.

### US-34: DeepWiki failure

**As a developer, I want AI-only failures isolated so that analytics and portfolio remain available.**

Acceptance criteria:
- Display error only in AI area.
- Provide retry.
- Preserve selected repository and dashboard state.

### US-35: Empty GitHub profile

**As a developer, I want profiles with no repositories or contributions to remain usable.**

Acceptance criteria:
- Support zero public repositories.
- Support no contribution history.
- Support missing descriptions/languages.
- Show explanatory empty states; never invent data.

### US-36: Loading and duplicate submissions

**As a developer, I want clear loading states so that I understand when work is in progress.**

Acceptance criteria:
- Loading indicators for profile sync, compatibility analysis, and DeepWiki requests.
- Prevent duplicate submission while a request is in progress.
- Show success/error feedback.

## Cross-cutting acceptance rules

1. Frontend must not implement core business calculations.
2. All GitHub and DeepWiki external calls must go through FastAPI.
3. The Vibe Check feature (US-14 through US-18) is mandatory and must be implemented and tested.
4. AI features must not block the dashboard.
5. Each milestone must leave the application runnable.
6. Use real external data; do not use hardcoded mock data in the final integrated flow.
7. Tests must cover happy paths and meaningful failure paths.
