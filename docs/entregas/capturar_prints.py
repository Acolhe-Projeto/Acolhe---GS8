"""Capture the screenshots used in the GS PDFs (headless Chromium via Playwright).

    python capturar_prints.py airflow github mvp grafana bpmn   # any subset
Services: Airflow at localhost:8081, Grafana at localhost:3000, Prometheus at localhost:9091.
"""
import os, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).with_name('prints'); OUT.mkdir(exist_ok=True)
MVP = 'https://acolhe-gs8.ambitiousbeach-2f5aaa39.canadacentral.azurecontainerapps.io'
GH = 'https://github.com/Acolhe-Projeto/Acolhe---GS8/actions/runs/'
HOST = os.environ.get('SERVICES_HOST', 'localhost')  # WSL IP when services run inside WSL
AIRFLOW = f'http://{HOST}:' + os.environ.get('AIRFLOW_PORT', '8081')
GRAFANA = f'http://{HOST}:' + os.environ.get('GRAFANA_PORT', '3000')
PROM = f'http://{HOST}:' + os.environ.get('PROM_PORT', '9091')
RUNS = {'gh_run_barrado': '44190586981', 'gh_run_corrigido': '44191227009', 'gh_run_branch': '44198056749'}

def shot(page, url, name, wait=2500, full=False, clip=None, action=None, until='networkidle'):
    page.goto(url, wait_until=until, timeout=90000)
    page.wait_for_timeout(wait)
    if action: action(page); page.wait_for_timeout(wait)
    path = OUT / f'{name}.png'
    page.screenshot(path=str(path), full_page=full, clip=clip)
    print('saved', path.name, page.title()[:60])

def airflow(page):
    base = AIRFLOW
    for dag in ('acolhe_official_snapshots', 'acolhe_medallion'):
        shot(page, f'{base}/dags/{dag}', f'airflow_{dag}_grid', wait=5000)
        shot(page, f'{base}/dags/{dag}/runs', f'airflow_{dag}_runs', wait=4000)
        # Graph view: second toggle button above the grid (Airflow 3.1 UI)
        shot(page, f'{base}/dags/{dag}', f'airflow_{dag}_graph', wait=4000,
             action=lambda p: p.mouse.click(145, 82))

def github(page):
    for name, run in RUNS.items():
        shot(page, GH + run, name, wait=3000)

def mvp(page):
    shot(page, MVP + '/', 'mvp_inicio', wait=4000)
    shot(page, MVP + '/#painel', 'mvp_painel', wait=4000,
         action=lambda p: p.locator('#painel').scroll_into_view_if_needed())

def rpa(page):
    # local MVP with activity + robot report (the robot runs locally, not in Azure)
    shot(page, 'http://127.0.0.1:8090/#painel', 'rpa_mvp_painel', wait=4000,
         action=lambda p: p.locator('#painel').scroll_into_view_if_needed())

def grafana(page):
    shot(page, GRAFANA + '/d/acolhe-signals?orgId=1&from=now-10m&to=now&kiosk', 'grafana_sinais_de_ouro', wait=12000, until='load')
    shot(page, PROM + '/alerts', 'prometheus_alertas', wait=4000, until='load')
    shot(page, PROM + '/targets', 'prometheus_alvo_publico', wait=4000, until='load')

if __name__ == '__main__':
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
        for group in sys.argv[1:]:
            globals()[group](page)
        browser.close()
