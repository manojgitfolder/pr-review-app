# TaskFlow — PR Auto Review with DeepSeek AI

A React task manager app with automated AI-powered PR code review using DeepSeek LLM, Jira integration, and GitHub Actions.

---

## 🚀 Quick Start

```bash
npm install
npm start        # Run app
npm test         # Run tests
```

---

## 🏗️ Project Structure

```
pr-review-app/
├── src/
│   ├── App.jsx                    # Root component
│   ├── App.css
│   ├── components/
│   │   ├── TaskList.jsx
│   │   ├── TaskList.css
│   │   ├── AddTask.jsx
│   │   └── AddTask.css
│   └── __tests__/
│       ├── App.test.jsx
│       ├── TaskList.test.jsx
│       └── AddTask.test.jsx
└── .github/
    └── workflows/
        ├── pr-review.yml          # ← Main AI review workflow
        └── ci.yml                 # Main branch CI
```

---

## ⚙️ GitHub Secrets Setup

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|--------|-------------|
| `DEEPSEEK_API_KEY` | Get from [platform.deepseek.com](https://platform.deepseek.com) |
| `JIRA_BASE_URL` | e.g. `https://yourcompany.atlassian.net` |
| `JIRA_EMAIL` | Your Jira account email |
| `JIRA_API_TOKEN` | Create at [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens) |

---

## 🔄 How the PR Review Works

```
PR Opened / Updated
        │
        ▼
┌─────────────────┐
│  Run Unit Tests │  ← Fails fast if tests break
└────────┬────────┘
         │
         ▼
┌──────────────────────────┐
│  Extract PR code diff    │  ← git diff vs base branch
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Extract Jira ticket key │  ← from PR title/description
│  e.g. PROJ-123           │     regex: [A-Z]+-[0-9]+
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Fetch Jira AC           │  ← Jira REST API v3
│  (acceptance criteria)   │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Send to DeepSeek LLM    │  ← diff + AC → review JSON
│  (deepseek-chat, free)   │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Post comments to PR     │  ← inline line comments
│  + summary comment       │     + review summary
└──────────┬───────────────┘
           │
      ┌────┴────┐
      ▼         ▼
  APPROVE   REQUEST_CHANGES
  ✅ Auto   ❌ Developer must
  approve    fix & re-push
```

---

## 📝 PR Description Format

Include your Jira ticket key in the PR title or description:

```
feat: Add user authentication [PROJ-123]

## Changes
- Added login/logout flow
- JWT token handling

## Jira
Fixes PROJ-123
```

---

## 🔑 Getting DeepSeek API Key (Free Tier)

1. Go to [platform.deepseek.com](https://platform.deepseek.com)
2. Sign up / log in
3. Go to **API Keys** → **Create new key**
4. Copy and add as `DEEPSEEK_API_KEY` secret in GitHub

DeepSeek offers a generous free tier — `deepseek-chat` model used here.

---

## 🔑 Getting Jira API Token

1. Go to [id.atlassian.com](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Create API token**
3. Copy token → add as `JIRA_API_TOKEN` in GitHub secrets

---

## 🧪 Test Coverage

Tests cover:
- ✅ App: task CRUD, progress counter, state management
- ✅ TaskList: rendering, empty state, toggle/delete callbacks, CSS classes
- ✅ AddTask: form submission, validation, error handling, state reset

Run with coverage:
```bash
npm run test:ci
```

Coverage threshold: **70%** lines/functions/branches

---

## 📋 Jira Acceptance Criteria Field

The workflow tries these Jira custom fields in order:
1. `customfield_10033` (common AC field)
2. `customfield_10016` (story points / sometimes AC)
3. `customfield_10014`
4. Falls back to the issue `description`

To find your Jira AC field ID, check your Jira admin or use:
```
GET /rest/api/3/issue/{issueKey}?expand=names
```
Then update the field names in the workflow accordingly.
