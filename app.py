import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

PATH = "C:/Users/USER/Desktop/FinalExam/FinalExam/msedgedriver.exe"

# 建立資料庫連線
conn = sqlite3.connect('scrape.db')
cursor = conn.cursor()

# 建立資料表
def create_table():
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS titles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cname TEXT NOT NULL
        )
        '''
    )

# 插入爬取的標題
def insert_title(cname):
    cursor.execute(
        '''
        INSERT INTO titles (cname)
        VALUES (?)
        ''', (cname,)
    )
    conn.commit()

# 清空資料表
def clear_table():
    cursor.execute('DELETE FROM titles')
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="titles"')
    conn.commit()

# 爬取並顯示內容
def scrape_and_display(url_entry, text_area):
    try:
        # 獲取 URL
        url = url_entry.get()

        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, "載入中，請稍候...\n")
        text_area.update_idletasks()

        service = Service(PATH)
        driver = webdriver.Edge(service=service)
        driver.get(url)

        # 爬取標題
        titles = driver.find_elements(By.CLASS_NAME, "board")
        scraped_titles = [title.text for title in titles]

        # 清空文字區域與資料庫
        text_area.delete(1.0, tk.END)
        clear_table()

        # 儲存爬取結果到全域變數
        global all_titles
        all_titles = scraped_titles

        # 更新文字區域並插入資料庫
        for idx, title in enumerate(scraped_titles):
            text_area.insert(tk.END, f"{idx + 1}. {title}\n")
            insert_title(title)

    except Exception as e:
        messagebox.showerror("錯誤", f"發生錯誤：{e}")

    # 處理無法連接或瀏覽器啟動失敗
    except WebDriverException as we:
        text_area.delete(1.0, tk.END)
        messagebox.showerror("無法連接", f"無法連接到指定的 URL，請檢查您的網路或 URL 是否正確。\n\n詳細資訊: {we}")

    driver.quit()

# 搜尋並過濾內容
def search_titles(search_entry, text_area):
    # 獲取搜尋關鍵字
    keyword = search_entry.get().strip()
    if not keyword:
        messagebox.showinfo("提示", "請輸入搜尋關鍵字")
        return

    # 篩選包含關鍵字的標題
    filtered_titles = [title for title in all_titles if keyword in title]

    # 更新文字區域
    text_area.delete(1.0, tk.END)
    if filtered_titles:
        for idx, title in enumerate(filtered_titles):
            text_area.insert(tk.END, f"{idx + 1}. {title}\n")

# 建立 Tkinter 主介面
def tkinter_window():
    root = tk.Tk()
    root.title("PTT 網頁爬蟲")
    root.geometry("640x480")
    root.columnconfigure(1, weight=1)
    root.rowconfigure(1, weight=1)

    # URL 輸入
    url_label = ttk.Label(root, text="URL:")
    url_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

    url_entry = ttk.Entry(root, width=60)
    url_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
    url_entry.insert(0, "https://www.ptt.cc/bbs/index.html")

    # 滑動文字區域
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=25)
    text_area.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=tk.NSEW)

    search_entry = ttk.Entry(root, width=20)
    search_entry.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)

    # 爬取按鈕
    scrape_button = ttk.Button(
        root, text="開始爬取",
        command=lambda: scrape_and_display(url_entry, text_area)
    )
    scrape_button.grid(row=0, column=2, sticky=tk.E, padx=5, pady=5)

    # 搜尋按鈕
    search_button = ttk.Button(
        root, text="搜尋", command=lambda: search_titles(search_entry, text_area)
    )
    search_button.grid(row=2, column=2, sticky=tk.W, padx=150, pady=5)

    # 刷新按鈕
    refresh_button = ttk.Button(
        root, text="刷新內容",
        command=lambda: scrape_and_display(url_entry, text_area)
    )
    refresh_button.grid(row=2, column=2, sticky=tk.E, padx=5, pady=5)

    root.mainloop()

# 初始化資料表並啟動程式
create_table()
tkinter_window()

# 關閉資料庫連線
conn.close()
