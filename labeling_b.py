import os
import shutil
import hashlib

# 元フォルダ群とターゲットフォルダ
SOURCE_FOLDERS = [
    "images_jimin", "images_taehyung",
    "images_jimin_instagram", "images_taehyung_instagram",
    "images_jimin_twitter", "images_taehyung_twitter",
    "images_jimin_getty", "images_taehyung_getty"
]
TARGET_FOLDERS = {"jimin": "images_jimin", "taehyung": "images_taehyung"}

# フォルダをクリア
def clear_folders(folders):
    for folder in folders.values():
        os.makedirs(folder, exist_ok=True)
        for file in os.listdir(folder):
            os.remove(os.path.join(folder, file))

# データ元ラベルを抽出
def get_label_and_target(folder_name):
    label = "official"
    for key in ["instagram", "twitter", "getty"]:
        if key in folder_name.lower():
            label = key
            break
    target = "jimin" if "jimin" in folder_name.lower() else "taehyung" if "taehyung" in folder_name.lower() else None
    return label, target

# 画像を振り分け
def organize_images(source_folders, target_folders):
    clear_folders(target_folders)  # 出力先フォルダをクリア
    for folder in source_folders:
        label, target = get_label_and_target(folder)
        if not target:
            print(f"Skipping unknown folder: {folder}")
            continue
        for file in os.listdir(folder):
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                source_path = os.path.join(folder, file)
                file_hash = hashlib.md5(file.encode()).hexdigest()
                target_filename = f"{label}_{file_hash}{os.path.splitext(file)[1]}"
                target_path = os.path.join(target_folders[target], target_filename)
                shutil.copy2(source_path, target_path)
                print(f"Copied {source_path} to {target_path}")

# 実行
if __name__ == "__main__":
    organize_images(SOURCE_FOLDERS, TARGET_FOLDERS)
    print("Image organization completed.")
