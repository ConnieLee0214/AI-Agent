import pandas as pd
import chardet
# csv_file_path = "Patient_data.csv"

# 讀取 Excel 文件並分塊處理
chunk_size = 1000  # 每塊讀取1000行
df = pd.read_excel('Patient_data.xlsx', sheet_name='Sheet1')
chunks = [df[i:i + chunk_size] for i in range(0, df.shape[0], chunk_size)]

# 處理每一塊數據
for chunk in chunks:
    print(chunk.head())  # 顯示每塊數據的前5行