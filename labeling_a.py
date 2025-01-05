import os
import shutil
import hashlib

# 元のフォルダ群
SOURCE_FOLDERS = [
    "images_jimin", "images_taehyung",
    "images_jimin_instagram", "images_taehyung_instagram",
    "images_jimin_twitter", "images_taehyung_twitter",
    "images_jimin_getty", "images_taehyung_getty"
]

# 出力先フォルダ
TARGET_FOLDERS = {
    "jimin": "images_jimin",
    "taehyung": "images_taehyung",
}

# ターゲットフォルダ内の既存ファイルにofficialラベルを付加
def relabel_existing_images(target_folders):
    for label, folder in target_folders.items():
        if not os.path.exists(folder):
            os.makedirs(folder)
        for file in os.listdir(folder):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')) and not file.startswith("official_"):
                old_path = os.path.join(folder, file)
                new_filename = f"official_{file}"
                new_path = os.path.join(folder, new_filename)
                os.rename(old_path, new_path)
                print(f"Relabeled {old_path} to {new_path}")

# ラベル付けとフォルダ分け
def organize_images(source_folders, target_folders):
    # 既存ファイルのラベル付け
    relabel_existing_images(target_folders)
   
    # 各元フォルダを走査
    for folder in source_folders:
        # データ元ラベルを抽出（フォルダ名に含まれる部分）
        if "instagram" in folder.lower():
            label = "instagram"
        elif "twitter" in folder.lower():
            label = "twitter"
        elif "getty" in folder.lower():
            label = "getty"
        else:
            label = "official"

        # JiminかTaehyungかを判断
        if "jimin" in folder.lower():
            target_folder = target_folders["jimin"]
        elif "taehyung" in folder.lower():
            target_folder = target_folders["taehyung"]
        else:
            print(f"Skipping folder: {folder} (unknown category)")
            continue

        # フォルダ内の画像を処理
        for file in os.listdir(folder):
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                source_path = os.path.join(folder, file)

                # ファイル名にラベルを追加
                file_hash = hashlib.md5(file.encode()).hexdigest()
                target_filename = f"{label}_{file_hash}{os.path.splitext(file)[1]}"
                target_path = os.path.join(target_folder, target_filename)

                # 画像を新しいフォルダにコピー
                shutil.copy2(source_path, target_path)
                print(f"Copied {source_path} to {target_path}")

# 実行
if __name__ == "__main__":
    organize_images(SOURCE_FOLDERS, TARGET_FOLDERS)
    print("Image organization completed.")
