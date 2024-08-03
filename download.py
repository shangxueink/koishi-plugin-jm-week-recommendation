from flask import Flask, request, jsonify, send_from_directory
import os
import subprocess
import shutil
import time
from jmcomic import JmOption

app = Flask(__name__)
option = JmOption.default()
client = option.new_jm_client()

# 获取最新章节ID的函数
def get_latest_chapter_id(book_id):
    album_detail = client.get_album_detail(book_id)  # 获取专辑详情
    if album_detail and album_detail.is_album():
        chapters_after_first = find_chapters_after_first(album_detail)
        if chapters_after_first:
            latest_chapter = chapters_after_first[-1]  # 获取最新的章节
            return latest_chapter.photo_id
    return None

def find_chapters_after_first(album):
    chapters = []
    first_chapter_id = album[0].photo_id
    found_first = False
    
    for chapter in album:
        if found_first:
            chapters.append(chapter)
        if chapter.photo_id == first_chapter_id:
            found_first = True
            
    return chapters

# 搜索漫画
@app.route('/jmcomic/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({"error": "缺少关键词"}), 400
    page = client.search_site(search_query=keyword, page=1)
    results = [{"album_id": album_id, "title": title} for album_id, title in page]
    return jsonify(results)

# 下载漫画
@app.route('/jmcomic/download', methods=['GET'])
def download():
    book_id = request.args.get('bookid')
    page_number = request.args.get('page')
    if not book_id or not page_number:
        return jsonify({"error": "缺少书籍ID或页码"}), 400

    # 获取最新章节ID
    latest_chapter_id = get_latest_chapter_id(book_id)
    if latest_chapter_id is None:
        latest_chapter_id = book_id

    # 创建以最新章节ID命名的文件夹
    download_path = os.path.join(os.getcwd(), latest_chapter_id)
    os.makedirs(download_path, exist_ok=True)

    # 检查是否已经下载过图片
    images = [f for f in os.listdir(download_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))]
    if images:
        # 返回对应页码的图片URL
        if int(page_number) > len(images) or int(page_number) <= 0:
            return jsonify({"error": "页码超出范围"}), 400

        image_path = images[int(page_number) - 1]
        image_url = f"/jmcomic/download_server/{latest_chapter_id}/{image_path}"  # 使用最新章节 ID 和文件名构建 URL
        return jsonify({"image_url": image_url})

    # 创建下载脚本
    script_content = f"""from jmcomic import JmOption, download_album
option = JmOption.default()
download_album('{latest_chapter_id}')
"""
    script_path = os.path.join(download_path, 'download.py')
    with open(script_path, 'w') as script_file:
        script_file.write(script_content)

    # 切换到下载文件夹
    original_cwd = os.getcwd()  # 保存原始工作目录
    os.chdir(download_path)  # 切换到下载文件夹

    # 执行下载脚本
    try:
        subprocess.run(['python', 'download.py'], check=True, timeout=15)  # 设置超时为15秒
    except subprocess.TimeoutExpired:
        os.chdir(original_cwd)  # 恢复原始工作目录
        shutil.rmtree(download_path)  # 删除下载文件夹
        return jsonify({"error": "章节数过多！建议还是去官网看吧!"}), 400
    except subprocess.CalledProcessError as e:
        os.chdir(original_cwd)  # 恢复原始工作目录
        shutil.rmtree(download_path)  # 删除下载文件夹
        return jsonify({"error": str(e)}), 500

    # 恢复原始工作目录
    os.chdir(original_cwd)

    # 移动下载的图片到指定文件夹
    for root, dirs, files in os.walk(download_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                src_path = os.path.join(root, file)
                shutil.move(src_path, download_path)  # 移动到 download_path

    # 返回对应页码的图片URL
    if int(page_number) > len(images) or int(page_number) <= 0:
        return jsonify({"error": "页码超出范围"}), 400

    image_path = images[int(page_number) - 1]
    image_url = f"/jmcomic/download_server/{latest_chapter_id}/{image_path}"  # 使用最新章节 ID 和文件名构建 URL

    return jsonify({"image_url": image_url})

# 提供下载的图片
@app.route('/jmcomic/download_server/<path:filename>', methods=['GET'])
def download_server(filename):
    # 获取文件的完整路径
    download_path = os.path.join(os.getcwd(), os.path.dirname(filename))
    file_name = os.path.basename(filename)
    full_path = os.path.join(download_path, file_name)

    # 调试信息
    if not os.path.exists(full_path):
        return jsonify({"error": "文件未找到", "path": full_path}), 404

    return send_from_directory(download_path, file_name)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=44555)
