from jinja2 import Environment, FileSystemLoader
import pandas as pd
from io import BytesIO
from markupsafe import Markup
# from weasyprint import HTML
from xhtml2pdf import pisa
import os
import re


def create_pdf(result_df):
    def _break_chinese_paragraph(text, max_chars=30):
        # 先用中文標點分句，加上 <br>（也支援英文句點）
        text = re.sub(r'([。！？\?])', r'\1<br>', text)
        # 若句子太長仍超出，額外加 <wbr> 每 max_chars 字
        chunks = []
        for line in text.split('<br>'):
            if len(line) > max_chars:
                chunks.extend([line[i:i+max_chars] + '<wbr>' for i in range(0, len(line), max_chars)])
            else:
                chunks.append(line)
        return '<br>'.join(chunks)

    def _nl2br(value):
        return Markup(value.replace('\n', '<br>'))
    
    patient = result_df.iloc[0].to_dict()
    text_fields = ["可能疾病分析依據", "疫情新聞摘要", "是否與症狀有關聯", "參考來源", "嚴重程度評估", "是否需立即就醫", "看診科別建議 / 藥品購買建議"]
    for field in text_fields:
        if field in patient and isinstance(patient[field], str):
            patient[field] = _break_chinese_paragraph(patient[field])
    template_dir = os.path.dirname(__file__)
    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters['nl2br'] = _nl2br
    template = env.get_template("report_template.html")
    html_out = template.render(patient=patient)

    # 產生 PDF
    pdf_output = BytesIO()
    # pdfkit.from_string(html_out, pdf_output)
    # HTML(string=html_out).write_pdf(pdf_output)
    def fetch_resources(uri, rel):
        path = os.path.join(os.path.dirname(__file__), uri)
        return os.path.abspath(path)

    pisa_status = pisa.CreatePDF(html_out, dest=pdf_output, link_callback=fetch_resources)
    pdf_output.seek(0)  # 重設游標到檔案開頭
    return pdf_output