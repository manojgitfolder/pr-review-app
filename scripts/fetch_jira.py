import json, os, sys, base64
import urllib.request, urllib.error

jira_key = os.environ.get('JIRA_KEY', '')
jira_base = os.environ.get('JIRA_BASE_URL', '')
jira_email = os.environ.get('JIRA_EMAIL', '')
jira_token = os.environ.get('JIRA_API_TOKEN', '')

if not jira_key:
    open('/tmp/jira_ac.txt','w').write('No Jira ticket linked. Review for general code quality.')
    open('/tmp/jira_summary.txt','w').write('No Jira ticket')
    sys.exit(0)

url = f"{jira_base}/rest/api/3/issue/{jira_key}?fields=summary,description,customfield_10033,customfield_10016,customfield_10014"
creds = base64.b64encode(f"{jira_email}:{jira_token}".encode()).decode()
req = urllib.request.Request(url, headers={
    'Authorization': f'Basic {creds}',
    'Content-Type': 'application/json'
})

def extract_adf(val):
    texts = []
    for block in val.get('content', []):
        for item in block.get('content', []):
            if item.get('type') == 'text':
                texts.append(item.get('text',''))
    return ' '.join(texts)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        fields = data.get('fields', {})
        summary = fields.get('summary', 'No summary')
        ac = ''
        for f in ['customfield_10033','customfield_10016','customfield_10014']:
            v = fields.get(f)
            if not v: continue
            if isinstance(v, str) and len(v) > 5:
                ac = v
                break
            if isinstance(v, dict):
                ac = extract_adf(v)
                if ac: break
        if not ac:
            desc = fields.get('description', {})
            if isinstance(desc, dict): ac = extract_adf(desc)[:2000]
            elif isinstance(desc, str): ac = desc[:2000]
        if not ac:
            ac = 'No acceptance criteria found.'
        open('/tmp/jira_ac.txt','w').write(ac)
        open('/tmp/jira_summary.txt','w').write(summary)
        print(f"Fetched: {jira_key} - {summary}")
except Exception as e:
    open('/tmp/jira_ac.txt','w').write(f'Could not fetch Jira: {e}')
    open('/tmp/jira_summary.txt','w').write('Fetch failed')
    print(f"Jira error: {e}")
