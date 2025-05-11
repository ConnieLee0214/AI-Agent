from jinja2 import Environment, FileSystemLoader
import pdfkit
import pandas as pd
from io import BytesIO
from markupsafe import Markup


def create_pdf(result_df):
    def _nl2br(value):
        return Markup(value.replace('\n', '<br>'))
    
    patient = result_df.iloc[0].to_dict()
    # 載入模板並渲染
    # env = Environment(loader=FileSystemLoader('/Users/connielee/Desktop/code/Final_Project'))
    env = Environment(loader=FileSystemLoader('./'))
    env.filters['nl2br'] = _nl2br
    template = env.get_template("report_template.html")
    html_out = template.render(patient=patient)

    # 產生 PDF
    # pdfkit.from_string(html_out, "/Users/connielee/Desktop/code/Final_Project/report.pdf")
        # 使用 BytesIO 生成 PDF 並保存在內存中
    pdf_output = BytesIO()
    pdfkit.from_string(html_out, pdf_output)
    pdf_output.seek(0)  # 重設游標到檔案開頭
    return pdf_output