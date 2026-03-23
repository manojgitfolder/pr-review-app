import json, os, sys, base64
import urllib.request, urllib.error

jira_key = os.environ.get('JIRA_KEY', '')
jira_base = os.environ.get('JIRA_BASE_URL', '')
jira_email = os.environ.get('JIRA_EMAIL', '')
jira_token = os.environ.get('JIRA_API_TOKEN', '')

def clean_text(text):
    """Remove characters that break GitHub Actions output delimiters"""
    if not text:
        return ''
    # Replace special chars that cause EOF delimiter issues
    text = text.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
    # Remove any EOF-like strings
    text = text.replace('EOF', 'END').replace('<<', '< <')
    return text.strip()

def extract_adf(val):
    texts = []
    for block in val.get('content', []):
        for item in block.get('content', []):
            if item.get('type') == 'text':
                texts.append(item.get('text', ''))
    return ' '.join(texts)

if not jira_key:
    open('/tmp/jira_ac.txt', 'w').write('No Jira ticket linked. Review for general code quality.')
    open('/tmp/jira_summary.txt', 'w').write('No Jira ticket')
    sys.exit(0)

url = f"{jira_base}/rest/api/3/issue/{jira_key}?fields=summary,description,customfield_10033,customfield_10016,customfield_10014"
creds = base64.b64encode(f"{jira_email}:{jira_token}".encode()).decode()
req = urllib.request.Request(url, headers={
    'Authorization': f'Basic {creds}',
    'Content-Type': 'application/json'
})

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        fields = data.get('fields', {})
        summary = clean_text(fields.get('summary', 'No summary'))
        ac = ''
        for f in ['customfield_10033', 'customfield_10016', 'customfield_10014']:
            v = fields.get(f)
            if not v:
                continue
            if isinstance(v, str) and len(v) > 5:
                ac = clean_text(v)
                break
            if isinstance(v, dict):
                ac = clean_text(extract_adf(v))
                if ac:
                    break
        if not ac:
            desc = fields.get('description', {})
            if isinstance(desc, dict):
                ac = clean_text(extract_adf(desc))[:2000]
            elif isinstance(desc, str):
                ac = clean_text(desc)[:2000]
        if not ac:
            ac = 'No acceptance criteria found.'

        open('/tmp/jira_ac.txt', 'w').write(ac)
        open('/tmp/jira_summary.txt', 'w').write(summary)
        print(f"Fetched: {jira_key} - {summary}")
        print(f"AC length: {len(ac)} chars")

except urllib.error.HTTPError as e:
    msg = f"Could not fetch Jira ticket {jira_key} (HTTP {e.code}). Review for general quality."
    open('/tmp/jira_ac.txt', 'w').write(msg)
    open('/tmp/jira_summary.txt', 'w').write(f"Fetch failed: HTTP {e.code}")
    print(f"Jira fetch failed: {e.code}")

except Exception as e:
    open('/tmp/jira_ac.txt', 'w').write(f'Jira fetch error. Review for general quality.')
    open('/tmp/jira_summary.txt', 'w').write('Fetch error')
    print(f"Error: {e}")
