import os
from datetime import datetime
import pandas as pd
from fpdf import FPDF

def get_chinese_font_file() -> str:
    """
    只檢查 Windows 系統字型資料夾中是否存在候選中文字型（TTF 格式）。
    若找到則回傳完整路徑；否則回傳 None。
    """
    font_dir = r"/Library/Fonts"
    # candidates = ["kaiu.ttf"]  # 這裡以楷體為例，可依需要修改
    for font in os.listdir(font_dir):
        font_path = os.path.join(font_dir, font)
        if os.path.exists(font_path):
            print("找到系統中文字型：", font_path)
            return os.path.abspath(font_path)
    print("未在系統中找到候選中文字型檔案。")
    return None

def get_auto_column_widths(pdf: FPDF, df: pd.DataFrame, padding: int = 4) -> list:
    """
    根據 DataFrame 內容，自動計算每欄適合的寬度。
    pdf: 當前的 FPDF 實例（已經設定好字體）
    df: 要顯示的資料
    padding: 每邊額外加的寬度（避免太緊）
    """
    col_widths = []
    for col in df.columns:
        max_width = pdf.get_string_width(str(col))  # 先算標題的寬
        for cell in df[col]:
            cell_width = pdf.get_string_width(str(cell))
            if cell_width > max_width:
                max_width = cell_width
        col_widths.append(max_width + padding)  # 加一點空間
    return col_widths


def create_table(pdf: FPDF, df: pd.DataFrame):
    """
    使用 FPDF 將 DataFrame 以漂亮的表格形式繪製至 PDF，
    支援自動換行、交替背景色、標題區塊，並自動處理分頁。
    """
    available_width = pdf.w - 2 * pdf.l_margin
    num_columns = len(df.columns)
    col_width = available_width / num_columns
    line_height = 6  # 每行高度
    font_size = 4

    def draw_header():
        pdf.set_fill_color(200, 200, 200)
        pdf.set_font("ChineseFont", "", font_size)
        for col in df.columns:
            pdf.cell(col_width, line_height * 2, str(col), border=1, align="C", fill=True)
        pdf.ln(line_height * 2)

    draw_header()
    fill = False


    for _, row in df.iterrows():
        # 計算每個 cell 要幾行，以及拆解後的文字內容
        cell_lines = []
        max_lines = 1
        for item in row:
            text = str(item)
            lines = pdf.multi_cell(col_width, line_height, text, border=0, align='L', split_only=True)
            cell_lines.append(lines)
            max_lines = max(max_lines, len(lines))

        row_height = line_height * max_lines

        # 檢查是否需要分頁
        if pdf.get_y() + row_height > pdf.h - pdf.b_margin:
            pdf.add_page()
            draw_header()

        y_start = pdf.get_y()
        x_start = pdf.get_x()

        # 畫每一格（等高處理）
        for col_index, lines in enumerate(cell_lines):
            x_cell = x_start + col_index * col_width
            y_cell = y_start
            pdf.set_xy(x_cell, y_cell)

            if fill:
                pdf.set_fill_color(230, 240, 255)
            else:
                pdf.set_fill_color(255, 255, 255)
            pdf.rect(x_cell, y_start, col_width, row_height, style='F')

            # 畫格子的每一行
            for line in lines:
                pdf.set_xy(x_cell, y_cell)
                pdf.cell(col_width, line_height, line, border=0, align='L', fill=False)
                y_cell += line_height

            # 補框線（畫完整格子高度）
            pdf.rect(x_cell, y_start, col_width, row_height)

        # 換到下一列
        pdf.set_y(y_start + row_height)
        fill = not fill



def generate_pdf(text: str = None, df: pd.DataFrame = None) -> str:
    print("開始生成 PDF")
    pdf = FPDF(format="A4")
    pdf.add_page()
    
    # 取得中文字型
    # chinese_font_path = get_chinese_font_file()
    chinese_font_path = "font/NotoSansTC-Regular.ttf"
    if not chinese_font_path:
        error_msg = "錯誤：無法取得中文字型檔，請先安裝合適的中文字型！"
        print(error_msg)
        return error_msg
    pdf.add_font("ChineseFont", "", chinese_font_path, uni=True)
    pdf.set_font("ChineseFont", "", 4)
    
    if df is not None:
        create_table(pdf, df)
    elif text is not None:
        # 嘗試檢查 text 是否包含 Markdown 表格格式
        if "|" in text:
            # 找出可能的表格部分（假設從第一個 '|' 開始到最後一個 '|'）
            table_part = "\n".join([line for line in text.splitlines() if line.strip().startswith("|")])
            parsed_df = parse_markdown_table(table_part)
            if parsed_df is not None:
                create_table(pdf, parsed_df)
            else:
                pdf.multi_cell(0, 10, text)
        else:
            pdf.multi_cell(0, 10, text)
    else:
        pdf.cell(0, 10, "沒有可呈現的內容")
    
    pdf_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    print("輸出 PDF 至檔案：", pdf_filename)
    pdf.output(pdf_filename)
    print("PDF 生成完成")
    return pdf_filename

# df = pd.read_csv('final_result2.csv') #已結合dataAgent和Playwright結果至這個csv中
# generate_pdf(text=None, df=df)