"""Render rpa/processo.bpmn to PNG with the bpmn-js viewer (headless Chromium)."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
xml = (ROOT / 'rpa' / 'processo.bpmn').read_text(encoding='utf-8')
html = f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://unpkg.com/bpmn-js@17.11.1/dist/assets/bpmn-js.css">
<style>html,body{{margin:0;background:#fff}} #c{{width:1320px;height:460px}}</style>
<script src="https://unpkg.com/bpmn-js@17.11.1/dist/bpmn-viewer.production.min.js"></script></head>
<body><div id="c"></div><script>
const v = new BpmnJS({{container: '#c'}});
v.importXML({json.dumps(xml)}).then(() => {{ v.get('canvas').zoom('fit-viewport'); document.body.dataset.done = '1'; }})
 .catch(e => {{ document.body.dataset.done = 'error: ' + e.message; }});
</script></body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(); page = b.new_page(viewport={'width': 1320, 'height': 460}, device_scale_factor=2)
    page.set_content(html, wait_until='networkidle')
    page.wait_for_function('document.body.dataset.done')
    status = page.evaluate('document.body.dataset.done'); print('bpmn render:', status)
    out = Path(__file__).with_name('prints') / 'rpa_bpmn.png'
    page.screenshot(path=str(out)); print('saved', out.name); b.close()
