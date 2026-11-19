"""Render the Vision report; assert the two word limits required by the rubric."""
import argparse
import html
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'docs/entregas/VISION_RELATORIO.md'


def render(output):
    source = SOURCE.read_text(encoding='utf-8')
    for heading, required in [('Resumo', 250), ('Objetivo', 50)]:
        body = source.split('## ' + heading + '\n', 1)[1].split('\n## ', 1)[0].strip()
        actual = len(body.split())
        if actual != required:
            raise ValueError(f'{heading}: {actual} palavras, esperado {required}')
    pdfmetrics.registerFont(TTFont('Acolhe', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('AcolheBold', 'C:/Windows/Fonts/arialbd.ttf'))
    pdfmetrics.registerFontFamily('Acolhe', normal='Acolhe', bold='AcolheBold')
    styles = {
        'body': ParagraphStyle('body', fontName='Acolhe', fontSize=10, leading=14, spaceAfter=8,
                               allowWidows=0, allowOrphans=0),
        'title': ParagraphStyle('title', fontName='AcolheBold', fontSize=21, leading=26, spaceAfter=18),
        'heading': ParagraphStyle('heading', fontName='AcolheBold', fontSize=13, leading=17,
                                  spaceBefore=14, spaceAfter=8, keepWithNext=True,
                                  textColor=colors.HexColor('#116e68')),
    }
    story, pending, table_rows = [], [], []

    def flush():
        if pending:
            value = html.escape(' '.join(pending))
            value = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', value)
            story.append(Paragraph(value, styles['body']))
            pending.clear()

    def flush_table():
        if not table_rows:
            return
        cells = [[Paragraph(html.escape(cell), styles['body']) for cell in row] for row in table_rows]
        columns = len(cells[0])
        if columns < 2 or any(len(row) != columns for row in cells):
            raise ValueError('Report table must have consistent columns')
        table = Table(cells, colWidths=[155] + [344/(columns-1)]*(columns-1), repeatRows=1)
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e1eee9')),
                                  ('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#b9cbc4')),
                                  ('VALIGN',(0,0),(-1,-1),'TOP')]))
        story.extend([table, Spacer(1, 12)])
        table_rows.clear()

    for line in source.splitlines():
        if line.startswith('|'):
            flush()
            if not re.match(r'^\|[\s|:\-]+\|$', line):
                table_rows.append([cell.strip() for cell in line.strip('|').split('|')])
            continue
        flush_table()
        image = re.match(r'!\[([^]]*)\]\(([^)]+)\)', line)
        if image:
            flush()
            path = (SOURCE.parent/image.group(2)).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file():
                raise ValueError('Report figure must be a local repository artifact')
            figure = Image(str(path))
            scale = min(499/figure.imageWidth, 480/figure.imageHeight)
            figure.drawWidth = figure.imageWidth*scale
            figure.drawHeight = figure.imageHeight*scale
            story.extend([figure, Paragraph(html.escape(image.group(1)), styles['body'])])
            continue
        if line.startswith('# '):
            flush()
            story.append(Paragraph(html.escape(line[2:]), styles['title']))
        elif line.startswith('## '):
            flush()
            story.append(Paragraph(html.escape(line[3:]), styles['heading']))
        elif not line.strip():
            flush()
        elif line.startswith('- ') or re.match(r'^\d+\. ', line):
            flush()
            story.append(Paragraph(html.escape(line), styles['body']))
        else:
            pending.append(line)
    flush()
    flush_table()

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#168c86'))
        canvas.line(48, 40, A4[0]-48, 40)
        canvas.setFont('Acolhe', 8)
        label = 'treinamento pendente' if 'anterior ao treinamento' in source else 'piloto treinado - qualidade não validada'
        canvas.drawString(48, 28, 'ACOLHE | Vision | ' + label)
        canvas.drawRightString(A4[0]-48, 28, str(document.page))
        canvas.restoreState()

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=48, rightMargin=48,
                            topMargin=45, bottomMargin=55, title='Acolhe - Applied Computer Vision',
                            author='Equipe Acolhe')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f'{output}: resumo 250 palavras, objetivo 50 palavras')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'docs/ACOLHE_VISION.pdf')
    render(parser.parse_args().output)
