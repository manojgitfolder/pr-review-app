import json, os, sys, base64
import urllib.request, urllib.error

jira_key = os.environ.get('JIRA_KEY', '')
jira_base = os.environ.get('JIRA_BASE_URL', '')
jira_email = os.environ.get('JIRA_EMAIL', '')
jira_token = os.environ.get('JIRA_API_TOKEN', '')
github_output = os.environ.get('GITHUB_OUTPUT', '/tmp/github_output.txt')

def clean_text(text):
    if not text:
        return ''
    # Flatten to single line - removes all newline issues
    text = ' '.join(text.split())
    text = text.replace('EOF', 'END').replace('<<', '< <').replace('>>', '> >')
    return text.strip()[:2000]

def extract_adf(val):
    texts = []
    for block in val.get('content', []):
        for item in block.get('content', []):
            if item.get('type') == 'text':
                texts.append(item.get('text', ''))
    return ' '.join(texts)

def write_output(key, value):
    """Write to GITHUB_OUTPUT directly from Python"""
    delimiter = f"DELIM_{key}_12345"
    with open(github_output, 'a') as f:
        f.write(f"{key}<<{delimiter}\n{value}\n{delimiter}\n")

if not jira_key:
    ac = 'No Jira ticket linked. Review for general code quality.'
    summary = 'No Jira ticket'
    write_output('acceptance_criteria', ac)
    write_output('jira_summary', summary)
    print("No Jira key found")
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
                ac = clean_text(extract_adf(desc))
            elif isinstance(desc, str):
                ac = clean_text(desc)
        if not ac:
            ac = 'No acceptance criteria found.'

        write_output('acceptance_criteria', ac)
        write_output('jira_summary', summary)
        print(f"Fetched: {jira_key} - {summary}")
        print(f"AC length: {len(ac)} chars")

except urllib.error.HTTPError as e:
    msg = f"Could not fetch Jira ticket {jira_key} HTTP {e.code}. Review for general quality."
    write_output('acceptance_criteria', msg)
    write_output('jira_summary', f"Fetch failed HTTP {e.code}")
    print(f"Jira fetch failed: {e.code}")

except Exception as e:
    write_output('acceptance_criteria', 'Jira fetch error. Review for general quality.')
    write_output('jira_summary', 'Fetch error')
    print(f"Error: {e}")
