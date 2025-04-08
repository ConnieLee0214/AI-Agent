from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

# 讀取 .env 檔案
# load_dotenv()
# FB_EMAIL = os.getenv("FACEBOOK_EMAIL")
# FB_PASSWORD = os.getenv("FACEBOOK_PASSWORD")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 顯示瀏覽器
    page = browser.new_page()

    print("啟動瀏覽器，進入Google Map")

    # 進入 Facebook 登入頁面
    page.goto("https://www.google.com/maps/")
    page.wait_for_timeout(3000)

    # 輸入地址（例如 "Taipei 101"）
    address = "台北市大安區敦化南路二段218號"
    print(f"輸入地址：{address}")
    search_box = page.locator("input#searchboxinput")
    search_box.fill(address)
    page.locator("button#searchbox-searchbutton").click()
    page.wait_for_timeout(5000)

    # 搜尋附近診所或醫院
    print("搜尋附近診所或醫院")
    # 點擊左上角的「搜尋附近」
    page.keyboard.press("Tab")  # 可能需要根據狀況多次 Tab，這裡假設已 focus 到正確位置
    page.keyboard.press("Tab")
    page.keyboard.press("Enter")
    page.wait_for_timeout(2000)

    # 輸入「診所或醫院」
    nearby_search_box = page.locator("input#searchboxinput")
    nearby_search_box.fill("clinic or hospital")
    page.locator("button#searchbox-searchbutton").click()
    page.wait_for_timeout(5000)

    print("完成搜尋，可以查看結果。")

    # 可加：保留畫面直到手動關閉
    input("按下 Enter 關閉瀏覽器...")
    browser.close()