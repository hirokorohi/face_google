from googleapiclient.discovery import build
import os
import shutil
import requests
import cv2  # OpenCVを使用
import numpy as np
import hashlib

# APIキーと検索エンジンIDを設定
API_KEY = "AIzaSyBMobgxw0G6GJbW-9BqixdfFlgVQgyv-OE"
SEARCH_ENGINE_ID = "d7d7d7cd7e9534d79"

# ダウンロード済みURLの管理ファイル
HISTORY_FILE = "download_history.txt"

# 保存フォルダを初期化
def clear_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

# ダウンロード履歴をロード
def load_download_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()

# ダウンロード履歴を更新
def update_download_history(urls):
    with open(HISTORY_FILE, "a") as f:
        for url in urls:
            f.write(url + "\n")

# 画像検索関数
def search_images(query, target_images=300):
    service = build("customsearch", "v1", developerKey=API_KEY)
    results = []
    for start in range(1, target_images + 1, 10):  # 10件ずつ取得
        try:
            response = service.cse().list(
                q=query,
                cx=SEARCH_ENGINE_ID,
                searchType="image",
                num=min(10, target_images - len(results)),  # 残り枚数を計算
                start=start
            ).execute()
            results.extend([item['link'] for item in response.get('items', [])])
        except Exception as e:
            print(f"Error fetching images: {e}")
            break
    return results

# 画像ダウンロード関数
def download_images(image_urls, save_folder="images", clear_existing=False):
    # 必要に応じてフォルダをクリア
    if clear_existing:
        clear_folder(save_folder)
    elif not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # ダウンロード済みURLのロード
    downloaded_urls = load_download_history()
    new_urls = []

    # OpenCVの顔検出モデルをロード
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    for url in image_urls:
        if url in downloaded_urls:
            print(f"Skipping already downloaded image: {url}")
            continue
    
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                content_type = response.headers['Content-Type']
                if "image" not in content_type:
                    print(f"Skipping non-image file: {url}")
                    continue

                # 画像をメモリ上に読み込む
                img_data = np.asarray(bytearray(response.content), dtype="uint8")
                img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)

                # 顔検出を行う
                if img is not None:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                    
                    # 顔が1つだけ検出された場合のみ保存
                    if len(faces) == 1:
                        # URLのハッシュ値を使って一意のファイル名を生成
                        file_hash = hashlib.md5(url.encode()).hexdigest()
                        filename = os.path.join(save_folder, f"{file_hash}.jpg")
                        cv2.imwrite(filename, img)
                        print(f"Downloaded and saved: {filename}")
                        new_urls.append(url)  # 新しいURLを記録
                    else:
                        print(f"Skipping image due to unsuitable face count ({len(faces)} faces): {url}")
                else:
                    print(f"Invalid image file: {url}")
        except Exception as e:
            print(f"Failed to process image: {e}")

    # ダウンロード履歴を更新
    update_download_history(new_urls)


# 実行部分
if __name__ == "__main__":
    queries = [
        {"query": "BTS Park Jimin official", "folder": "images_jimin"},
        {"query": "BTS Kim Taehyung official", "folder": "images_taehyung"},
        {"query": "BTS Park Jimin site:instagram.com", "folder": "images_jimin_instagram"},
        {"query": "BTS Kim Taehyung site:instagram.com", "folder": "images_taehyung_instagram"},
        {"query": "BTS Park Jimin site:twitter.com", "folder": "images_jimin_twitter"},
        {"query": "BTS Kim Taehyung site:twitter.com", "folder": "images_taehyung_twitter"},
        {"query": "BTS Park Jimin site:gettyimages.com", "folder": "images_jimin_getty"},
        {"query": "BTS Kim Taehyung site:gettyimages.com", "folder": "images_taehyung_getty"},
    ]
    num_images = 100  # 各キーワードごとの目標枚数
    clear_existing_folders = False  # 既存フォルダを削除する場合はTrue

    for q in queries:
        print(f"Searching images for: {q['query']}...")
        image_links = search_images(q['query'], target_images=num_images)
        print(f"Found {len(image_links)} images. Downloading to folder: {q['folder']}...")
        download_images(image_links, save_folder=q['folder'], clear_existing=clear_existing_folders)
        print(f"Image download completed for: {q['query']}\n")
