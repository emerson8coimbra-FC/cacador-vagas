import json, re, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
OUTPUT = ROOT / 'vagas.json'
API = 'https://www.arbeitnow.com/api/job-board-api'
KEYWORDS = ('data entry','annotation','annotator','ai trainer','ai training','content moderator','transcription','transcriber','search evaluator','data labeling','virtual assistant','customer support','portuguese','brazil','entry level')
EXCLUDE = ('senior','staff engineer','principal engineer','lead engineer','5+ years','7+ years')

def clean(s):
    return re.sub('<[^>]+>', ' ', s or '').replace('&nbsp;', ' ').strip()

def main():
    req = urllib.request.Request(API, headers={'User-Agent': 'CacadorVagas/1.0 (personal job discovery)'})
    with urllib.request.urlopen(req, timeout=30) as response:
        jobs = json.load(response).get('data', [])
    found = []
    for job in jobs:
        title = clean(job.get('title'))
        desc = clean(job.get('description'))
        text = (title + ' ' + desc).lower()
        if not job.get('remote') or not any(k in text for k in KEYWORDS) or any(k in title.lower() for k in EXCLUDE):
            continue
        found.append({'titulo': title, 'empresa': job.get('company_name',''), 'local': job.get('location',''), 'link': job.get('url',''), 'descricao': desc[:350], 'data': job.get('created_at',''), 'verificar_elegibilidade': True})
    previous = []
    if OUTPUT.exists():
        try: previous = json.loads(OUTPUT.read_text(encoding='utf-8')).get('vagas', [])
        except (ValueError, OSError): pass
    merged = {j['link']: j for j in previous + found if j.get('link')}
    results = sorted(merged.values(), key=lambda x: str(x.get('data','')), reverse=True)[:200]
    OUTPUT.write_text(json.dumps({'atualizado':datetime.now(timezone.utc).isoformat(), 'vagas':results}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{len(found)} vagas encontradas nesta busca; {len(results)} no painel')

if __name__ == '__main__':
    main()
