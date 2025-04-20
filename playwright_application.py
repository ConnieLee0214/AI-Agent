from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv
import pandas as pd


def search_location(page, target):
    nearby_search_box = page.locator("input#searchboxinput")
    nearby_search_box.fill(target)
    page.locator("button#searchbox-searchbutton").click()
    page.wait_for_timeout(5000)

    print("完成搜尋，可以查看結果。")

    page.wait_for_selector("div.Nv2PK", timeout=10000)

    # 擷取整頁 HTML
    html = page.content()

    # 使用 BeautifulSoup 解析結果
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # 擷取診所/醫院資訊
    results = []
    entries = soup.select("div.Nv2PK")
    for entry in entries:
        name = entry.select_one(".qBF1Pd.fontHeadlineSmall")
        address = None

    # 🔍 抓所有 W4Efsd 的區塊
        info_blocks = entry.select(".W4Efsd")
        # print(info_blocks)
        for block in info_blocks:
            if "號" in block.get_text():  # 找看起來像地址的
                spans = block.find_all("span")
                for span in spans:
                    if "號" in span.get_text():  # 尋找真正包含地址的 span
                        address = span.get_text(strip=True)
                        break
            if address:
                break

        if name and address:
            results.append({
                "name": name.text.strip(),
                "address": address
            })
    for r in results:
        print(f"{r['name']} - {r['address']}")
    return results



df = pd.read_excel('Patient_data.xlsx', sheet_name='Sheet1')
patient_location = df['地址']

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://www.google.com/maps/")
    page.wait_for_timeout(3000)

    all_results = []

    for input_address in patient_location:
        print(f"處理地址：{input_address}")
        search_box = page.locator("input#searchboxinput")
        search_box.fill(input_address)
        page.locator("button#searchbox-searchbutton").click()
        page.wait_for_timeout(5000)

        clincs = search_location(page, "診所")
        hospitals = search_location(page, "醫院")
        pharmacies = search_location(page, "藥局")

        all_results.append({
            "地址": input_address,
            "診所": clincs,
            "醫院": hospitals
        })

    input("按 Enter 關閉瀏覽器...")
    browser.close()
# print(all_results)``

# for input_address in patient_location:

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)  # 顯示瀏覽器
#         page = browser.new_page()

#         print("啟動瀏覽器，進入Google Map")

#         # 進入 Facebook 登入頁面
#         page.goto("https://www.google.com/maps/")
#         page.wait_for_timeout(3000)

#         # 輸入地址（例如 "Taipei 101"）
#         # input_address = "台北市大安區"
#         print(f"輸入地址：{input_address}")
#         search_box = page.locator("input#searchboxinput")
#         search_box.fill(input_address)
#         page.locator("button#searchbox-searchbutton").click()
#         page.wait_for_timeout(5000)

#         # 搜尋附近診所或醫院
#         print("搜尋附近診所或醫院")
#         # 點擊左上角的「搜尋附近」
#         page.keyboard.press("Tab")  # 可能需要根據狀況多次 Tab，這裡假設已 focus 到正確位置
#         page.keyboard.press("Tab")
#         page.keyboard.press("Enter")
#         page.wait_for_timeout(2000)

#         # 輸入「診所或醫院」
#         def search_location(target):
#             nearby_search_box = page.locator("input#searchboxinput")
#             nearby_search_box.fill(target)
#             page.locator("button#searchbox-searchbutton").click()
#             page.wait_for_timeout(5000)

#             print("完成搜尋，可以查看結果。")

#             page.wait_for_selector("div.Nv2PK", timeout=10000)

#             # 擷取整頁 HTML
#             html = page.content()

#             # 使用 BeautifulSoup 解析結果
#             from bs4 import BeautifulSoup
#             soup = BeautifulSoup(html, "html.parser")

#             # 擷取診所/醫院資訊
#             results = []
#             entries = soup.select("div.Nv2PK")
#             for entry in entries:
#                 name = entry.select_one(".qBF1Pd.fontHeadlineSmall")
#                 # address = entry.select_one(".W4Efsd span:nth-of-type(2)")
#                 # address_div = entry.select_one(".W4Efsd")
            
#                 # if address_div:
#                 #     # 選擇地址所在的 span 標籤並提取
#                 #     address = None
#                 #     address_spans = address_div.find_all("span")
#                 #     print(address_spans)
#                 address = None

#             # 🔍 抓所有 W4Efsd 的區塊
#                 info_blocks = entry.select(".W4Efsd")
#                 # print(info_blocks)
#                 for block in info_blocks:
#                     if "號" in block.get_text():  # 找看起來像地址的
#                         spans = block.find_all("span")
#                         for span in spans:
#                             if "號" in span.get_text():  # 尋找真正包含地址的 span
#                                 address = span.get_text(strip=True)
#                                 break
#                     if address:
#                         break

#                 if name and address:
#                     results.append({
#                         "name": name.text.strip(),
#                         "address": address
#                     })
#             for r in results:
#                 print(f"{r['name']} - {r['address']}")
#             return results
        
#         clincs = search_location("診所")
#         hospitals = search_location("醫院")
#         print(clincs)
#         # 可加：保留畫面直到手動關閉
#         input("按下 Enter 關閉瀏覽器...")
#         browser.close()