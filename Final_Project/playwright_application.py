from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv
import pandas as pd
import csv


def search_medication_location(patient_location):
    def _search_by_adress(page, target):
        nearby_search_box = page.locator("input#searchboxinput")
        nearby_search_box.fill(target)
        page.locator("button#searchbox-searchbutton").click()
        page.wait_for_timeout(5000)

        # print("完成搜尋，可以查看結果。")

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
                if "號" in block.get_text(): 
                    spans = block.find_all("span")
                    for span in spans:
                        if "號" in span.get_text():
                            address = span.get_text(strip=True)
                            break
                if address:
                    break

            if name and address:
                results.append({
                    "name": name.text.strip(),
                    "address": address
                })
        # for r in results:
        #     print(f"{r['name']} - {r['address']}")
        return results

    def _format_clinic_list(clinic_list):
        return "\n".join(f"{clinic['name']} - {clinic['address'].lstrip('·')}" for clinic in clinic_list)

    all_results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.google.com/maps/")
        page.wait_for_timeout(3000)

        for input_address in patient_location:
            # print(f"處理地址：{input_address}")
            search_box = page.locator("input#searchboxinput")
            search_box.fill(input_address)
            page.locator("button#searchbox-searchbutton").click()
            page.wait_for_timeout(5000)

            clincs = _search_by_adress(page, "診所")
            hospitals = _search_by_adress(page, "醫院")
            pharmacies = _search_by_adress(page, "藥局")

            all_results.append({
                # "地址": input_address,
                "診所": _format_clinic_list(clincs),
                "醫院": _format_clinic_list(hospitals),
                "藥局": _format_clinic_list(pharmacies)
            })

        # input("按 Enter 關閉瀏覽器...")
        browser.close()
    result_df = pd.DataFrame(all_results)
    return result_df

# if __name__ == '__main__':
#     # 範例用法
#     locations = ["台北市中山區中山北路二段5號"]
#     df = search_medication_location(locations)
#     print(df)
#     df.to_csv("playwright_test.csv")