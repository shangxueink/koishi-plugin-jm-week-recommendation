
# JMComic 下载器

这是一个使用 Flask 框架构建的漫画下载器，利用 `jmcomic` 库从 JM 官网下载漫画章节的图片。 

## 需求

在运行此项目之前，请确保您的系统中安装了以下软件：

- Python 3.8 及以上版本
- pip（Python 包管理器）

## 安装

1. **创建虚拟环境（可选）**：

   为了避免与其他项目的依赖冲突，建议您创建一个虚拟环境：

   ```bash
   python -m venv venv
   ```

   激活虚拟环境：

   - **Windows**：
     ```bash
     venv\Scripts\activate
     ```

   - **macOS / Linux**：
     ```bash
     source venv/bin/activate
     ```

2. **安装依赖项**：

   首先，安装 `jmcomic` 库：

   ```bash
   pip install jmcomic -i https://pypi.org/project --upgrade
   ```

   然后，安装 Flask：

   ```bash
   pip install Flask
   ```

## 运行

在终端中，导航到包含代码的目录，并运行以下命令启动 Flask 服务器：

```bash
python app.py
```

默认情况下，服务器将在 `127.0.0.1:44555` 上运行。

## API 调用

### 搜索漫画

- **请求**：
  ```
  GET /jmcomic/search?keyword=<关键词>
  ```

- **示例**：
  ```
  GET /jmcomic/search?keyword=你的关键词
  ```

- **返回**：
  ```json
  [
      {"album_id": "书籍ID", "title": "书籍标题"},
      ...
  ]
  ```

### 下载漫画

- **请求**：
  ```
  GET /jmcomic/download?bookid=<书籍ID>&page=<页码>
  ```

- **示例**：
  ```
  GET /jmcomic/download?bookid=12345&page=1
  ```

- **返回**：
  ```json
  {"image_url": "图片的URL"}
  ```

### 获取下载的图片

- **请求**：
  ```
  GET /jmcomic/download_server/<文件名>
  ```

- **示例**：
  ```
  GET /jmcomic/download_server/12345/图片名.webp
  ```

- **返回**：
  图片文件。

## 注意事项

- 请确保您的网络可以访问 JM 官网，以便能够下载漫画内容。
- 如果请求的页码超出范围，API 将返回相应的错误信息。
- 在下载之前，系统会检查目标文件夹中是否已存在所需的图片，以避免重复下载。
