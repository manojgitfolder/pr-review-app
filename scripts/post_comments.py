import json, os
import urllib.request, urllib.error

review = json.load(open('/tmp/review_result.json'))
token = os.environ['GH_TOKEN']
repo = os.environ['GITHUB_REPOSITORY']
pr_number = os.environ['PR_NUMBER']
commit_sha = os.environ['PR_COMMIT_SHA']
jira_key = os.environ.get('JIRA_KEY', '')
jira_base = os.environ.get('JIRA_BASE_URL', '')
tests_passed = os.environ.get('TESTS_PASSED', 'false')

base_url = f"https://api.github.com/repos/{repo}"
headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
    'Content-Type': 'application/json'
}

def gh_post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        print(f"GitHub error {e.code}: {e.read().decode()}")
        return None, e.code

s = "✅" if review['overall_status'] == 'APPROVE' else "❌"
a = "✅" if review.get('meets_acceptance_criteria') else "❌"
t = "✅" if tests_passed == "true" else "❌"
jira_link = f"[{jira_key}]({jira_base}/browse/{jira_key})" if jira_key and jira_base else (jira_key or "Not linked")

body = f"""## 🤖 DeepSeek AI Code Review

| Check | Status |
|-------|--------|
| Overall | {s} **{review['overall_status']}** |
| Unit Tests | {t} {'Passed' if tests_passed=='true' else 'Failed'} |
| Acceptance Criteria | {a} {'Met' if review.get('meets_acceptance_criteria') else 'Not met'} |
| Jira Ticket | {jira_link} |

### Summary
{review.get('summary','')}

### Decision
{review.get('approval_reason','')}

---
*Reviewed by DeepSeek AI • {len(review.get('comments',[]))} inline comment(s)*"""

gh_post(f"{base_url}/issues/{pr_number}/comments", {"body": body})
print("Summary comment posted")

emojis = {'error': '🔴', 'warning': '🟡', 'suggestion': '🔵'}
comments = []
for c in review.get('comments', []):
    if not c.get('file') or not c.get('line') or not c.get('message'):
        continue
    comments.append({
        "path": c['file'],
        "line": int(c['line']),
        "side": "RIGHT",
        "body": f"{emojis.get(c.get('severity','suggestion'),'💬')} **{c.get('severity','SUGGESTION').upper()}**\n\n{c['message']}"
    })

event = "APPROVE" if review['overall_status'] == 'APPROVE' else "REQUEST_CHANGES"
payload = {
    "commit_id": commit_sha,
    "body": review.get('approval_reason', ''),
    "event": event,
    "comments": comments
}
_, status = gh_post(f"{base_url}/pulls/{pr_number}/reviews", payload)
if status not in [200, 201]:
    print("Retrying without inline comments...")
    payload['comments'] = []
    gh_post(f"{base_url}/pulls/{pr_number}/reviews", payload)

print(f"Review submitted: {event}")
