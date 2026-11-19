"""Build the GS PDFs (Big Data, RPA, DevSecOps) from the repository evidence.

    python gerar_pdfs.py                      # writes docs/entregas/*.pdf
    VIDEO_RPA=https://youtu.be/... python gerar_pdfs.py

Numbers come from the evidence files, never typed by hand. Prints come from
docs/entregas/prints/ (capturar_prints.py, render_bpmn.py). Optional extra prints
named databricks_*.png in that folder are added to the Big Data report.
"""
import base64, html, json, os, re
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; PRINTS = HERE / 'prints'
REPO = 'https://github.com/Acolhe-Projeto/Acolhe---GS8'
BRANCH_URL = REPO + '/tree/Aksel%2BIan'
MVP = 'https://acolhe-gs8.ambitiousbeach-2f5aaa39.canadacentral.azurecontainerapps.io'
RUN = REPO + '/actions/runs/'
TEAM = [('Tomáz Versolato Carballo', '551417'), ('Rony Ken Nagai', '551549'),
        ('Aksel Viktor Caminha Rae', '99011'), ('Ian Xavier Kuraoka', '98860')]
VIDEO_RPA = os.environ.get('VIDEO_RPA', '')

# ---------- helpers ----------
def e(s): return html.escape(str(s))
def img(name, caption, width='100%'):
    path = PRINTS / name
    if not path.exists(): return f'<p class="missing">[print ausente: {e(name)}]</p>'
    data = base64.b64encode(path.read_bytes()).decode()
    return f'<figure><img src="data:image/png;base64,{data}" style="width:{width}"><figcaption>{caption}</figcaption></figure>'
def table(cols, rows, cls=''):
    head = ''.join(f'<th>{e(c)}</th>' for c in cols)
    body = ''.join('<tr>' + ''.join(f'<td>{e(v)}</td>' for v in r) + '</tr>' for r in rows)
    return f'<table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'
def link(url, text=None): return f'<a href="{e(url)}">{e(text or url)}</a>'
def team_block():
    return '<h2>Integrantes</h2>' + table(['Nome completo', 'RM'], TEAM, 'narrow')
def md_tables(path):
    """Parse markdown tables of an evidence file -> {section heading: [(cols, rows), ...]}"""
    out, heading, current = {}, '', None
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if line.startswith('#'): heading = line.lstrip('#').strip(); current = None; continue
        if line.startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if set(''.join(cells)) <= set('-: '): continue
            if current is None: current = (cells, []); out.setdefault(heading, []).append(current)
            else: current[1].append(cells)
        else: current = None
    return out
def flow(steps):
    boxes = '<div class="arrow">→</div>'.join(f'<div class="box"><b>{t}</b><span>{s}</span></div>' for t, s in steps)
    return f'<div class="flow">{boxes}</div>'
CSS = """
@page { size: A4; margin: 16mm 14mm 16mm 14mm; }
body { font-family: 'Segoe UI', Arial, sans-serif; color: #1d2b2a; font-size: 10.5pt; line-height: 1.45; }
h1 { color: #0f5e57; font-size: 21pt; margin: 0 0 4px; } h2 { color: #0f5e57; border-bottom: 2px solid #cfe3df; padding-bottom: 3px; margin-top: 22px; font-size: 14pt; }
h3 { font-size: 11.5pt; margin: 14px 0 4px; } .sub { color: #4a5e5c; margin-bottom: 14px; }
table { border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 9pt; page-break-inside: avoid; }
th { background: #e6f1ef; text-align: left; } th, td { border: 1px solid #c9d8d5; padding: 4px 6px; vertical-align: top; }
table.narrow { width: 60%; } figure { margin: 8px 0 14px; page-break-inside: avoid; } img { border: 1px solid #c9d8d5; }
figcaption { font-size: 8.8pt; color: #4a5e5c; margin-top: 3px; } code, pre { font-family: Consolas, monospace; font-size: 8.6pt; }
pre { background: #f4f7f6; border: 1px solid #dbe5e3; padding: 8px; white-space: pre-wrap; page-break-inside: avoid; }
.flow { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; margin: 8px 0 12px; }
.box { border: 1.5px solid #0f5e57; border-radius: 8px; padding: 6px 8px; background: #f2f8f7; font-size: 8.6pt; max-width: 118px; }
.box b { display: block; color: #0f5e57; } .box span { color: #33413f; } .arrow { color: #0f5e57; font-size: 15pt; }
.missing { color: #a33; } .note { background: #fff7e0; border-left: 4px solid #e0b030; padding: 6px 10px; font-size: 9.5pt; }
.req { page-break-inside: avoid; } a { color: #0b6e9e; }
h2, h3 { break-after: avoid; page-break-after: avoid; }
"""
def page(title, subtitle, body):
    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{e(title)}</title><style>{CSS}</style></head><body><h1>{e(title)}</h1><div class="sub">{subtitle}</div>{body}</body></html>'

# ---------- Big Data ----------
def big_data():
    clean = md_tables(ROOT / 'big_data/evidence/databricks_20261117_acolhe_gs.md')
    local = md_tables(ROOT / 'big_data/EVIDENCIAS.md')
    sql = re.sub(r'--[^\n]*', '', (ROOT / 'big_data/queries.sql').read_text(encoding='utf-8'))
    queries = [q.strip() for q in sql.split(';') if q.strip()]
    from importlib import util
    spec = util.spec_from_file_location('ev', ROOT / 'big_data/evidence.py'); ev = util.module_from_spec(spec)
    import sys; sys.path.insert(0, str(ROOT)); spec.loader.exec_module(ev)
    counts = clean['Contagens antes, depois de cada lote e na reexecucao'][0]
    keep = ['Etapa', 'bronze', 'bronze_municipios', 'silver_municipios', 'bronze_obmigra', 'silver_obmigra', 'quarantine']
    idx = [counts[0].index(k) for k in keep]
    counts_rows = [[r[i] for i in idx] for r in counts[1]]
    rules = clean['Regras de qualidade da Prata (total barrado por regra)'][0]
    lotes = clean['Lotes reais enviados ao Volume'][0]
    origem = clean['Bronze real por arquivo de origem'][0]
    hist = clean['DESCRIBE HISTORY bronze_municipios'][0]
    captions = {
        'databricks_1_volume_lotes_reais': 'Requisito 04: Volume workspace.acolhe_gs.data com os dois lotes reais em input/chegada/ibge, um por dia de coleta (14/11 e 17/11).',
        'databricks_2_tabelas_do_schema': 'Requisitos 05 a 07: as 13 tabelas do schema acolhe_gs (Bronze, Prata, quarentena, regras de qualidade, fato e dimensões).',
        'databricks_3_bronze_municipios_history': 'Requisito 05: histórico Delta de bronze_municipios, com uma carga COPY INTO por lote e nenhuma versão nova na reexecução.',
        'databricks_4_quality_rules_barrados': 'Requisito 06: total barrado por regra (tabela quality_rules); R1, R2 e R3 barram uma linha cada no lote de teste de qualidade.',
        'databricks_5_execucoes_succeeded': 'Execuções do notebook no Databricks Free Edition (serverless), todas Succeeded. Os 2 erros no gráfico são de tentativas anteriores no mesmo dia, corrigidas no código (esquema da quarentena e lote sem uma das fontes).',
        'databricks_6_consulta_de_impacto': 'Requisito 07: consulta de impacto no SQL Editor, cerca de 12.096 crianças de 0 a 11 anos entre os pedidos de refúgio de 2025 (OBMigra).',
    }
    extra = '<div class="req"><h3>Prints da interface do Databricks</h3><p>E-mail e ID de usuário ocultados.</p></div>' + ''.join(
        img(p.name, captions.get(p.stem, 'Interface do Databricks')) for p in sorted(PRINTS.glob('databricks_*.png')))
    qblocks = ''
    for n, q in enumerate(queries, 1):
        res = clean.get(f'Consulta {n}', [None])[0]
        qblocks += f'<div class="req"><h3>Consulta {n}{" (impacto)" if n == 6 else ""}</h3><pre>{e(q)}</pre>'
        qblocks += (table(*res) if res else '') + f'<p><b>Interpretação.</b> {e(ev.INTERPRETATION[n-1])}</p></div>'
    body = team_block() + f"""
<h2>1. O produto e as perguntas que o MVP responde</h2>
<p>O Acolhe é um aplicativo bilíngue (português e espanhol) que ajuda crianças hispanofalantes recém-chegadas ao Brasil a aprender o português do dia a dia, com mediação de responsáveis e educadores. MVP público: {link(MVP)}.</p>
<p>Perguntas que o componente de dados responde na tela "Território e acolhimento":</p>
<ul><li>Quantos pedidos de refúgio o Brasil recebeu e quantos vieram de crianças de 0 a 11 anos? (dado real, OBMigra 2025)</li>
<li>Quantos pedidos foram deferidos? (dado real, OBMigra 2025)</li>
<li>Qual o território de referência em SP? (dado real, IBGE: 645 municípios)</li>
<li>Onde está a demanda por acolhimento linguístico, em qual idioma, e qual a pressão sobre a oferta? (fontes demonstrativas, marcadas como sintéticas na tela)</li></ul>

<h2>2. Fluxo de dados, da fonte ao MVP</h2>
{flow([('Fontes', 'API IBGE (JSON) · PDF OBMigra · CSV demo'), ('Airflow 3', 'coletar_ibge ∥ coletar_obmigra → conferir_chegada'), ('chegada/', 'um arquivo por coleta com a data no nome'), ('Volume', 'upload em lotes por dia de coleta'), ('Bronze', 'COPY INTO incremental + arquivo de origem'), ('Prata', 'tipos, MERGE pela chave, 3 regras por fonte'), ('Ouro', 'fato + dimensões + contexto oficial'), ('MVP', 'summary.json em /api/gold')])}
<p>O Databricks Free Edition não se conecta ao Airflow: os arquivos de <code>chegada/</code> sobem ao Volume em lotes, um por dia de coleta (<code>big_data/databricks/run_evidence.py</code>).</p>

<h2>3. Fontes</h2>
{table(['Fonte', 'Origem', 'Formato', 'Frequência de coleta', 'Licença'], [
 ('IBGE, municípios de SP', 'servicodados.ibge.gov.br/api/v1/localidades/estados/35/municipios', 'API JSON → CSV normalizado', 'diária (DAG 04:00 UTC); lotes reais de 14/11 e 17/11', 'dado aberto IBGE, citar a fonte'),
 ('OBMigra/MJSP, Dados Consolidados 2025', 'gov.br/mj (Dados2025.pdf)', 'PDF → 7 indicadores extraídos do texto, com página', 'diária (mesmo DAG); relatório anual', 'reprodução com citação, uso não comercial (p.4)'),
 ('demand / services', 'gerados pela equipe', 'CSV', 'lotes 05/11, 06/11 e 07/11 (teste de qualidade)', 'sintético, sinalizado na tela')])}

<h2>4. Requisitos 01 a 09</h2>
<div class="req"><h3>01 · Duas fontes, uma externa real</h3><p>IBGE e OBMigra são externas e reais; amostras de cada fonte em <code>big_data/amostras/</code>. Os números reais aparecem no MVP:</p>{img('mvp_painel.png', 'MVP público, painel "Território e acolhimento": dados oficiais OBMigra 2025 e IBGE ao lado da camada demonstrativa, sinalizada como sintética.')}</div>
<div class="req"><h3>02 · DAG agendado grava em chegada/</h3><p><code>acolhe_official_snapshots</code> roda todo dia às 04:00 UTC e grava <code>chegada/ibge/municipios_AAAA-MM-DD.csv</code> e <code>chegada/obmigra/indicadores_AAAA-MM-DD.csv</code>. A data é o dia real da coleta e um lote existente nunca é sobrescrito.</p></div>
<div class="req"><h3>03 · Paralelismo, conferência e chaves fora do código</h3><p>As duas coletas rodam em paralelo e <code>conferir_chegada</code> confere se cada arquivo chegou, com cabeçalho e linhas. Os endpoints vêm das Variables <code>acolhe_ibge_url</code> e <code>acolhe_obmigra_url</code>; as fontes são públicas e não usam chave. Falhas acionam a notificação <code>task_failure</code>, e a conferência registra <code>chegada_ok</code>, ambas em <code>chegada/_notificacoes/notificacoes.jsonl</code>. Em 17/11, apontar a Variable para um endereço <code>http://</code> fez <code>coletar_ibge</code> falhar após 3 tentativas, gerou <code>{{"event": "task_failure", "task_id": "coletar_ibge", "try_number": 3}}</code> e deixou o ramo paralelo intacto (último quadrado vermelho na Grid, seção 5).</p></div>
<div class="req"><h3>04 · Dois lotes de dias de coleta diferentes no Volume</h3>{table(*lotes)}</div>
<div class="req"><h3>05 · Bronze incremental sem duplicar</h3><p><code>COPY INTO</code> com <code>force=false</code> lê só arquivos novos. Cada linha guarda <code>arquivo_origem</code> e <code>carregado_em</code>:</p>{table(*origem)}<p>Histórico Delta de <code>bronze_municipios</code>: duas cargas de 645 linhas, uma por lote, e nenhuma versão nova na reexecução.</p>{table(hist[0], [[r[0], r[1], r[2], r[3][:90]] for r in hist[1]])}</div>
<div class="req"><h3>06 · Prata: tipos, nulos, MERGE e três regras com contagem</h3><p>Tipos convertidos com <code>try_cast</code>, linhas inválidas vão para a quarentena com a regra que quebraram, e o MERGE usa a chave de cada fonte (<code>source, record_id</code>; <code>municipality_id</code>; <code>indicator_id, reference_year, territory</code>). O lote sintético <code>demand_2026-11-07.csv</code> traz uma linha inválida por regra, para mostrar cada regra barrando.</p>{table(*rules)}</div>
<div class="req"><h3>07 · Ouro dimensional e cinco consultas</h3><p>Fato <code>fact_indicators</code> com as dimensões <code>dim_region</code> e <code>dim_language</code> (chaves SHA-256), mais <code>dim_municipality</code> (IBGE) e <code>gold_official_context</code> (OBMigra). Consultas e resultados na seção 7.</p></div>
<div class="req"><h3>08 · LGPD na Ouro e tela do MVP</h3><p>Nenhuma camada tem dado pessoal: as fontes são agregadas e as chaves das dimensões são hash. O MVP consome o contrato <code>summary.json</code> (fato agregado + <code>official_context</code>) em <code>/api/gold</code>, exibido no painel da seção 01.</p></div>
<div class="req"><h3>09 · README e organização</h3><p>{link(BRANCH_URL + '/big_data', 'big_data/README.md')} traz integrantes, arquitetura, a tabela destes requisitos e o passo a passo. Pastas: <code>airflow/</code> (DAGs), <code>databricks/</code> (notebooks), <code>queries.sql</code>, <code>amostras/</code>.</p></div>
{extra}

<h2>5. Airflow: visões Graph e Grid com execuções concluídas</h2>
{img('airflow_acolhe_official_snapshots_graph.png', 'Graph de acolhe_official_snapshots: coletar_ibge e coletar_obmigra em paralelo, depois conferir_chegada.')}
{img('airflow_acolhe_official_snapshots_grid.png', 'Grid de acolhe_official_snapshots: execuções concluídas (verde) e a falha provocada para testar a notificação (vermelho).')}
{img('airflow_acolhe_medallion_graph.png', 'Graph de acolhe_medallion: ingest_demand ∥ ingest_services → medallion → integrate_official.')}
{img('airflow_acolhe_medallion_grid.png', 'Grid de acolhe_medallion com execuções concluídas.')}

<h2>6. Contagens antes e depois do 2º lote e da 2ª execução (Databricks)</h2>
<p>Execução limpa em 17/11 num schema novo (<code>workspace.acolhe_gs</code>), Databricks Free Edition serverless:</p>
{table([k.replace('bronze', 'bronze_demo', 1) if k == 'bronze' else k for k in keep], counts_rows)}
<p>A Bronze real vai de 0 para 645 no lote de 14/11 e para 1290 no lote de 17/11; a reexecução não carrega nada. A Prata fica em 645 municípios e 7 indicadores, porque o MERGE atualiza as mesmas chaves.</p>

<h2>7. Consultas SQL com resultado e interpretação</h2>
<p>Resultados da execução no Databricks (iguais aos do pipeline local em SQLite).</p>
{qblocks}

<h2>8. Conclusão técnica</h2>
<p>O pipeline coleta duas fontes reais por dia no Airflow, confere a chegada e avisa quando algo falha. No Databricks, a Bronze carrega cada lote uma única vez, a Prata trata os tipos, aplica as regras com contagem e faz MERGE pela chave, e a Ouro entrega ao MVP um contrato pequeno e sem dados pessoais. A execução real revelou defeitos que os testes locais não pegavam (importação no worker do Airflow, permissão de cópia, esquema da quarentena, pasta no Volume), todos corrigidos e registrados no repositório. Limitação: os indicadores de demanda e oferta continuam demonstrativos e aparecem marcados como tal; os dados reais servem de contexto, sem serem somados a eles.</p>
<p>Repositório: {link(BRANCH_URL, REPO + ' (branch Aksel+Ian)')}</p>
"""
    return page('Acolhe · Big Data Architecture & Data Integration', 'Global Solution 2026.2 · FIAP · CitizenTech', body)

# ---------- RPA ----------
def rpa():
    ev_dir = sorted((ROOT / 'rpa/evidence').glob('2026*'))[-1]
    e2e = json.loads((ev_dir / 'e2e.json').read_text(encoding='utf-8'))
    steps = {s['step']: s for s in e2e['steps']}
    log = (sorted((ROOT / 'rpa/logs').glob('*.log'))[-1]).read_text(encoding='utf-8')
    video = link(VIDEO_RPA) if VIDEO_RPA else '<span class="missing">inserir o link do vídeo antes do envio</span>'
    tests = [('Sucesso', '5 lições respondidas corretamente', f"decisão {steps['1_success']['decision']['status']}; MVP mostra {steps['1_success']['mvp']['attempts']} tentativas, acurácia {steps['1_success']['mvp']['accuracy']:.0%}"),
             ('Decisão', '3 erros na lição "mobilidade"', f"decisão {steps['2_decision']['decision']['status']}; revisar {', '.join(steps['2_decision']['decision']['lessons_to_review'])}"),
             ('Falha', 'banco inexistente', f"{steps['3_failure']['error']}; banco criado: {steps['3_failure']['db_created']}; MVP mantém o último relatório ({steps['3_failure']['mvp_still_serves']})"),
             ('Inconsistências', 'sessão inexistente, lição desconhecida, acerto inválido, duplicada', '4 linhas descartadas e contadas por motivo; WARNING no log sem IDs (teste automatizado)')]
    body = team_block() + f"""
<h2>1. CitizenTech e problema resolvido</h2>
<p>O Acolhe ajuda crianças hispanofalantes recém-chegadas ao Brasil a aprender português do dia a dia. Educadores e voluntários precisam saber como as crianças estão indo nas lições, mas consolidar isso à mão no banco do aplicativo é lento e arrisca expor dados. A automação faz essa consolidação sozinha, com regras de negócio, e entrega o resultado ao próprio MVP.</p>
<h2>2. Objetivo e benefício para o cidadão</h2>
<p>Gerar, sem intervenção humana, um relatório agregado de progresso e decidir quais lições precisam de reforço, para que o educador saiba onde agir. Nenhum dado identificável sai do banco e nada é enviado a terceiros.</p>
<h2>3. Processo e fluxo (BPMN)</h2>
{img('rpa_bpmn.png', 'BPMN 2.0 (rpa/processo.bpmn): validação, gateway de leitura, regra de negócio com três saídas, geração dos relatórios, log e consumo pelo MVP.')}
<p>PDD resumido. Entrada: SQLite do MVP (somente leitura). Etapas: validar o banco, ler as tentativas, percorrê-las aplicando as regras de consistência, agregar por idioma e lição, decidir e gravar <code>progress.json</code>/<code>progress.md</code> de forma atômica. Saída: relatório lido em <code>/api/automation</code>. Disparo: manual ou agendado (<code>--every N</code>, ou <code>schtasks</code>/cron conforme o README).</p>
<h2>4. Tecnologias e justificativa</h2>
<p>Python 3.12 da biblioteca padrão (sqlite3, logging, json), opção permitida pelo enunciado. O robô roda no mesmo ambiente do MVP sem dependência externa, é versionado e testado no GitHub (testes automatizados na esteira) e lê o banco em modo somente leitura.</p>
<h2>5. Regras de negócio, decisões e processamento</h2>
{table(['Regra', 'Condição', 'Ação'], [('Sem atividade', 'nenhuma tentativa válida', 'status sem_atividade, nada a consolidar'),
  ('Reforço', 'lição com pelo menos 3 tentativas e menos de 60% de acerto', 'status reforco_recomendado e a lição entra na lista de revisão'),
  ('Progresso adequado', 'demais casos', 'status progresso_adequado'),
  ('Consistência (laço)', 'cada tentativa é conferida antes da agregação', 'descarta sessão inexistente, lição desconhecida, acerto fora de 0/1 e duplicada (mesma sessão e request_id)')])}
<h2>6. Exceções e recuperação</h2>
<p>Banco ausente: erro registrado, código de saída 1 e nenhum banco vazio é criado. Esquema inválido: <code>report_failed</code> no log, sem relatório parcial. Banco ocupado: espera de até 10 s. Dados inconsistentes: descartados e contados por motivo. A escrita é atômica (arquivo temporário e troca), então o MVP sempre lê o último relatório válido. Com <code>--every</code>, uma falha não interrompe as execuções seguintes.</p>
<h2>7. Logs e evidências de auditoria</h2>
<pre>{e(log.strip())}</pre>
<p>Amostra real em <code>rpa/logs/</code>: data e hora, itens processados, decisão, sucesso e falha, sem identificadores.</p>
<h2>8. Integração com o MVP</h2>
{img('rpa_mvp_painel.png', 'Painel "Acompanhamento automático" do MVP lendo /api/automation: 2 sessões, 8 tentativas, 63% de acerto e a lição "mobilidade" para revisar.')}
<h2>9. Testes realizados</h2>
{table(['Cenário', 'Entrada', 'Resultado registrado'], tests)}
<p>Execução de ponta a ponta: <code>python -B -m rpa.demo_e2e --evidence rpa/evidence</code> (servidor HTTP real, robô e leitura pelo MVP). Os testes automatizados do robô rodam na esteira a cada push.</p>
<h2>10. Segurança e LGPD</h2>
<p>Leitura em modo somente leitura (<code>mode=ro</code>, <code>query_only</code>); nenhum ID de sessão ou tentativa vai para relatório ou log; os relatórios são agregados e locais, sem e-mail, upload ou mensagem. Grupos pequenos ainda podem dar contexto, então o acesso aos relatórios deve ficar restrito aos educadores e a retenção acompanha a do app (7 dias).</p>
<h2>11. Links</h2>
<ul><li>Repositório: {link(BRANCH_URL + '/rpa', 'rpa/ na branch Aksel+Ian')}</li><li>Vídeo demonstrativo: {video}</li></ul>
"""
    return page('Acolhe · Robotic Process Automation', 'Do processo manual à automação inteligente · Global Solution 2026.2 · FIAP', body)

# ---------- DevSecOps ----------
def devsecops():
    body = team_block() + f"""
<h2>1. Links</h2>
<ul><li>MVP público: {link(MVP)}</li>
<li>Repositório: {link(BRANCH_URL, REPO + ' (branch Aksel+Ian)')}; Dockerfile, <code>.github/workflows/devsecops.yml</code>, <code>devsecops/terraform/</code>; Ficha Técnica no README</li>
<li>Execução barrada: {link(RUN + '44190586981')} · corrigida: {link(RUN + '44191227009')}</li>
<li>Deploy automático pela <code>main</code>, sem passo manual: {link(RUN + '44218762634')} (e o primeiro, {link(RUN + '44218099076')})</li></ul>

<h2>2. Arquitetura</h2>
{flow([('Dev', 'push em qualquer branch / PR'), ('GitHub Actions', 'testes · Gitleaks · Semgrep · build · Trivy'), ('OIDC → Azure', 'subject imutável, só environment production'), ('ACR privado', 'imagem testada; CI com AcrPush'), ('Container Apps', 'HTTPS, 0..1 réplica, UID 10001, AcrPull'), ('Azure Files', 'SQLite em /data, firewall Deny'), ('Cidadão', 'URL pública')])}
{flow([('Prometheus', '/metrics por HTTPS'), ('Regras', 'indisponibilidade, erros, latência, concorrência'), ('Grafana', '4 sinais de ouro')])}
<p>Infraestrutura criada por Terraform (<code>devsecops/terraform/main.tf</code>): resource group, VNet e sub-rede delegada, storage account com firewall e criptografia de infraestrutura, share de 1 GiB, Azure Container Registry sem usuário admin, identidade gerenciada de pull, ambiente e Container App. State e <code>.tfvars</code> ficam fora do repositório; nenhuma porta administrativa é aberta (só o ingress HTTPS 443).</p>

<h2>3. Container e IaC</h2>
<p>Imagem <code>python:3.12-alpine</code> fixada por digest, <code>apk upgrade</code>, usuário não root (UID 10001), filesystem somente leitura no Compose, <code>cap_drop: ALL</code> e <code>no-new-privileges</code>. A stack sobe com <code>docker compose up --build</code>, e <code>devsecops/persistence_check.sh</code> mostrou os dados sobrevivendo a <code>down</code>/<code>up</code>. No Azure, os dados sobreviveram a dois reinícios do container (<code>devsecops/evidence/azure_deploy_20261114.md</code>).</p>

<h2>4. Pipeline DevSecOps: execução barrada e corrigida</h2>
{img('gh_run_barrado.png', 'Run 44190586981: o commit 6abd6ac introduz eval(); test-and-build falha e o deploy é pulado.')}
<pre>Semgrep local rules (no external code upload)
    /src/rpa/_gate_demo.py
   ❯❯❱ devsecops.no-dynamic-evaluation
            3┆ return eval(expressao)</pre>
{img('gh_run_corrigido.png', 'Run 44191227009: o commit d68f2af remove o eval() e todos os gates passam.')}
<p>O workflow roda a cada push e PR: testes Python e Node, Gitleaks no histórico, Semgrep com regras locais, build, testes dentro da imagem, smoke HTTP/SQLite, Trivy na imagem e na IaC, com bloqueio em HIGH/CRITICAL. O deploy é automático em push na <code>main</code>. O job entra no Azure por OIDC, com secrets no environment <code>production</code> e credencial federada presa ao subject imutável do repositório. Depois envia a imagem testada ao ACR privado, roda o <code>az containerapp update</code> e faz um health check na URL pública. Comprovado no run {link(RUN + '44218762634')}: build, gates, envio, deploy e health check, sem passo manual.</p>
<p>Uma barrada de deploy também aconteceu: o primeiro deploy pela <code>main</code> publicaria num pacote GHCR privado da organização, e a verificação de pull anônimo parou o job antes de tocar no Azure ({link(RUN + '44210859059')}). A solução foi trocar para o ACR com identidades gerenciadas.</p>
<p>Outras barradas reais registradas no README: o Semgrep apontou um <code>exec()</code> num teste ao ampliar o escopo; o Trivy barrou como CRITICAL a conta de armazenamento sem regra de rede (corrigido com VNet e firewall); o Trivy 0.60 barrou um falso positivo no Dockerfile de experimento.</p>

<h2>5. Observabilidade</h2>
{img('grafana_sinais_de_ouro.png', 'Grafana (local, apontando para o MVP publicado): latência média, tráfego, proporção de erros e requisições ativas, com tráfego real na URL pública.')}
{img('prometheus_alvo_publico.png', 'Prometheus coletando /metrics da URL pública por HTTPS.')}
{img('prometheus_alerta_disparado.png', 'Alerta AcolheUnavailable em firing: ensaio controlado com o container local do app parado (o MVP público não foi derrubado).')}

<h2>6. Custos (Azure Retail Prices API, canadacentral)</h2>
{table(['Item', 'Preço de lista', 'Demonstração (40 h/mês)', 'Sempre ligado'], [
 ('vCPU ativa (0,25 vCPU)', 'US$ 0,000034/s', 'US$ 1,22', 'US$ 22,34'),
 ('Memória (0,5 GiB)', 'US$ 0,000004/GiB-s', 'US$ 0,29', 'US$ 5,26'),
 ('Requisições', 'US$ 0,40/milhão', 'US$ 0,04', 'conforme uso'),
 ('Azure Files (1 GiB, Hot LRS)', 'US$ 0,03/GB-mês', 'centavos', 'centavos'),
 ('Azure Container Registry Basic (10 GB incluídos)', 'US$ 0,1666/dia', 'US$ 5,00', 'US$ 5,00'),
 ('VNet, GitHub Actions em repositório público', 'sem custo', '-', '-')])}
<p>Total estimado: cerca de US$ 6,70/mês em uso de demonstração (o app escala a zero sem tráfego; o ACR é cobrado por dia) e cerca de US$ 33/mês no pior caso, coberto pelo crédito Azure for Students de US$ 100.</p>

<h2>7. Responsabilidade compartilhada</h2>
{table(['Camada', 'Provedor', 'Equipe'], [
 ('Datacenter, hardware, hipervisor', 'Azure', '-'),
 ('Plataforma Container Apps e TLS do ingress', 'Azure', 'região, escala, ingress só HTTPS'),
 ('Runners do GitHub Actions', 'GitHub', 'versões fixadas, sem segredo no código'),
 ('Registro de imagens (ACR)', 'Azure', 'sem usuário admin, push só pela CI, pull só pela identidade do app'),
 ('Imagem do container', '-', 'digest fixado, Trivy, usuário não root'),
 ('Código', '-', 'testes, Semgrep, validação de entrada, CSP'),
 ('Identidade e acesso', 'Entra ID (OIDC)', 'identidade só no RG e no environment production'),
 ('Dados', 'durabilidade do Azure Files', 'retenção de 7 dias, exclusão por sessão, firewall'),
 ('Monitoramento', 'coleta da plataforma', 'sinais de ouro, regras de alerta')])}

<h2>8. Onde ficam os dados pessoais (LGPD)</h2>
<p>O único dado pessoal é pseudônimo: o código aleatório de sessão, com idioma, lição, acerto e horário, no SQLite em <code>/data</code> (Azure Files, conta com firewall Deny, TLS 1.2 e criptografia em repouso). Não há nome, documento, foto, áudio ou localização. As sessões são apagadas após 7 dias, e o botão "Apagar minha sessão de teste" exclui a pedido. RPA e Big Data só exportam agregados. O ACR guarda só a imagem do app, sem dados pessoais. Como a assinatura de estudante não permite <code>brazilsouth</code>, o deploy está em <code>canadacentral</code>, o que é transferência internacional (art. 33); em uso real com crianças, usar região no Brasil e cumprir o art. 14 (consentimento de um dos pais ou responsável).</p>

<h2>9. Ficha Técnica e reprodução</h2>
<p>API 0.1.0 em Python 3.12 (biblioteca padrão) e SQLite; interface HTML/CSS/JS bilíngue. Para reproduzir: <code>bash devsecops/ci_local.sh</code> (mesmos gates da CI), <code>docker compose up --build</code>, <code>terraform -chdir=devsecops/terraform init && terraform apply</code> com um <code>terraform.tfvars</code> local, e <code>docker compose -f devsecops/monitoring/public/compose.yaml up -d</code> para o Grafana.</p>
"""
    return page('Acolhe · Secure DevOps Tools & Cloud Computing', 'Deploy Blindado · Global Solution 2026.2 · FIAP', body)

if __name__ == '__main__':
    docs = {'GS_BigData_Acolhe': big_data(), 'GS_RPA_Acolhe': rpa(), 'GS_DevSecOps_Acolhe': devsecops()}
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        for name, content in docs.items():
            (HERE / f'{name}.html').write_text(content, encoding='utf-8')
            pg.set_content(content, wait_until='load')
            pg.pdf(path=str(HERE / f'{name}.pdf'), format='A4', print_background=True,
                   display_header_footer=True, header_template='<span></span>',
                   footer_template='<div style="font-size:8px;width:100%;text-align:center;color:#777">Acolhe · GS 2026.2 · <span class="pageNumber"></span>/<span class="totalPages"></span></div>',
                   margin={'top': '16mm', 'bottom': '16mm', 'left': '14mm', 'right': '14mm'})
            print('pdf', name)
        b.close()
