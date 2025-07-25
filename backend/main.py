from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import ast
import markdown
from xhtml2pdf import pisa

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PathRequest(BaseModel):
    path: str

IGNORE_DIRS = {'.git', '__pycache__', 'node_modules', 'venv', '.vscode'}
IGNORE_FILES = {'.DS_Store'}

def generate_directory_tree(start_path):
    tree_lines = []
    for root, dirs, files in os.walk(start_path, topdown=True):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        level = root.replace(start_path, '').count(os.sep)
        indent = '  ' * level
        tree_lines.append(f"{indent}└── {os.path.basename(root)}/")
        sub_indent = '  ' * (level + 1)
        for f in sorted(files):
            if f not in IGNORE_FILES:
                tree_lines.append(f"{sub_indent}├── {f}")
    return "\n".join(tree_lines)

def analyze_dependencies(start_path):
    dependencies = set()
    py_files = []
    for root, dirs, files in os.walk(start_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))

    for file_path in py_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=file_path)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            dependencies.add((os.path.basename(file_path), alias.name.split('.')[0]))
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            dependencies.add((os.path.basename(file_path), node.module.split('.')[0]))
            except Exception:
                continue
    return dependencies

def to_mermaid_graph(dependencies):
    graph_str = "graph TD;\n"
    nodes = set()
    for A, B in dependencies:
        nodes.add(A)
        nodes.add(B)
        graph_str += f'    {A.replace(".", "_")} --> {B.replace(".", "_")};\n'
    for node in nodes:
        graph_str += f'    style {node.replace(".", "_")} fill:#f9f,stroke:#333,stroke-width:2px\n'
    return graph_str

def generate_project_summary(project_name, tree_doc, mermaid_graph):
    summary = f"""
# プロジェクト概要: {project_name}

このドキュメントは、プロジェクトの構造と主要な依存関係を自動生成したものです。

## フォルダ構成

```
{tree_doc}
```

## システム依存関係図

```mermaid
{mermaid_graph}
```

## 動作概要

このプロジェクトは、指定されたディレクトリのファイル構造を解析し、Pythonファイルの依存関係を抽出し、その情報を基にMarkdown形式のドキュメントとMermaid形式のシステム依存関係図を生成します。

### 主要な機能:

-   **ディレクトリツリーの生成**: プロジェクト内のファイルとフォルダの階層構造を視覚的に表示します。
-   **Python依存関係の解析**: Pythonソースコード内のインポート文を解析し、ファイル間の依存関係を特定します。
-   **Mermaid図の生成**: 解析された依存関係をMermaid形式のグラフ定義に変換し、視覚的なシステム構成図を提供します。
-   **Webインターフェース**: ユーザーがプロジェクトパスを入力し、生成されたドキュメントをブラウザで確認できるシンプルなWebアプリケーションです。

### 技術スタック:

-   **バックエンド**: Python (FastAPI)
-   **フロントエンド**: React.js
-   **図の描画**: Mermaid.js

このドキュメントは、プロジェクトの全体像を素早く把握するために役立ちます。
"""
    return summary

def generate_developer_guide():
    guide = f"""
# 開発者ガイド

このドキュメントは、プロジェクトのバックエンドコード（`backend/main.py`）の主要な機能と構造を説明します。

## 主要な関数

### `generate_directory_tree(start_path: str) -> str`
-   **説明**: 指定されたパス以下のディレクトリツリーをMarkdown形式の文字列として生成します。
-   **引数**: `start_path` (str): ツリーを生成する開始ディレクトリの絶対パス。
-   **戻り値**: (str): ディレクトリツリーを表すMarkdown形式の文字列。

### `analyze_dependencies(start_path: str) -> set[tuple[str, str]]`
-   **説明**: 指定されたパス以下のPythonファイル（`.py`）を解析し、ファイル間のインポート依存関係を抽出します。
-   **引数**: `start_path` (str): 依存関係を解析する開始ディレクトリの絶対パス。
-   **戻り値**: (set[tuple[str, str]]): (依存元ファイル名, 依存先モジュール名) のタプルのセット。

### `to_mermaid_graph(dependencies: set[tuple[str, str]]) -> str`
-   **説明**: 抽出された依存関係のセットをMermaid.js形式のグラフ定義文字列に変換します。
-   **引数**: `dependencies` (set[tuple[str, str]]): `analyze_dependencies` から返される依存関係のセット。
-   **戻り値**: (str): Mermaid.jsのグラフ定義文字列。

### `generate_project_summary(project_name: str, tree_doc: str, mermaid_graph: str) -> str`
-   **説明**: プロジェクトの概要、フォルダ構成、システム依存関係図、動作概要、技術スタックを含むMarkdown形式のサマリーを生成します。
-   **引数**: 
    - `project_name` (str): プロジェクト名。
    - `tree_doc` (str): `generate_directory_tree` から生成されたディレクトリツリー。
    - `mermaid_graph` (str): `to_mermaid_graph` から生成されたMermaidグラフ定義。
-   **戻り値**: (str): プロジェクトの概要を表すMarkdown形式の文字列。

### `generate_developer_guide() -> str`
-   **説明**: この開発者ガイド自体を生成します。
-   **引数**: なし。
-   **戻り値**: (str): 開発者ガイドのMarkdown形式の文字列。

### `generate_user_manual() -> str`
-   **説明**: ユーザー向け運用マニュアルを生成します。
-   **引数**: なし。
-   **戻り値**: (str): ユーザーマニュアルのMarkdown形式の文字列。

## APIエンドポイント

### `POST /api/generate-doc`
-   **説明**: 指定されたプロジェクトパスのドキュメントを生成し、ブラウザに表示します。また、プロジェクト概要、開発者ガイド、ユーザーマニュアルをファイルとして保存します。
-   **リクエストボディ**: 
    ```json
    {{
        "path": "string"
    }}
    ```
-   **レスポンス**: 
    ```json
    {{
        "document": "string"
    }}
    ```
-   **エラー**: 
    - `400 Bad Request`: 無効なパスが指定された場合。
    - `404 Not Found`: 指定されたディレクトリが見つからない場合。
    - `500 Internal Server Error`: ドキュメント生成中に予期せぬエラーが発生した場合。

## 依存関係

-   `FastAPI`: Web APIフレームワーク。
-   `uvicorn`: ASGIサーバー。
-   `pydantic`: データ検証と設定管理。
-   `os`, `ast`: Python標準ライブラリ（ファイルシステム操作、AST解析）。

"""
    return guide

def generate_user_manual():
    manual = f"""
# ユーザーマニュアル

このドキュメントは、プロジェクトドキュメント生成ツールの使い方を説明します。

## 1. アプリケーションの起動

### バックエンドの起動
1.  ターミナルを開き、プロジェクトのルートディレクトリ（例: `/Users/mo/Projects/Gemini_CLI/`）に移動します。
2.  `backend` ディレクトリに移動します。
    ```bash
    cd backend
    ```
3.  仮想環境を有効化し、FastAPIサーバーを起動します。
    ```bash
    source venv/bin/activate
    uvicorn main:app --reload
    ```
    サーバーは `http://127.0.0.1:8000` で起動します。

### フロントエンドの起動
1.  別のターミナルを開き、プロジェクトのルートディレクトリに移動します。
2.  `frontend` ディレクトリに移動します。
    ```bash
    cd frontend
    ```
3.  React開発サーバーを起動します。
    ```bash
    npm start
    ```
    ブラウザが自動的に開き、`http://localhost:3000` でアプリケーションが表示されます。

## 2. ドキュメントの生成

1.  ブラウザで開いたアプリケーションの入力欄に、ドキュメントを生成したいプロジェクトの**絶対パス**、または `/Users/mo/Projects/` を基準とした**相対パス**を入力します。
    -   例: `/Users/mo/Projects/Gemini_CLI/backend` （絶対パス）
    -   例: `Gemini_CLI/backend` （相対パス）
2.  「ドキュメントを生成」ボタンをクリックします。
3.  しばらくすると、ブラウザ上にプロジェクトの「フォルダ構成」と「システム依存関係図」が表示されます。

## 3. 生成されるファイル

ドキュメントを生成すると、以下のファイルが自動的に作成され、指定したプロジェクトのルートディレクトリに保存されます。

-   `[プロジェクト名]_project_summary.md`: プロジェクトの概要、フォルダ構成、システム依存関係図、動作概要、技術スタックを含むMarkdownファイル。

また、アプリケーションのルートディレクトリ（`/Users/mo/Projects/Gemini_CLI/`）には、以下のドキュメントが生成されます。

-   `DEVELOPER_GUIDE.md`: 開発者向けのコード設計書。
-   `USER_MANUAL.md`: この運用マニュアル自体。

## 4. トラブルシューティング

-   **「Directory not found.」エラー**: 入力したパスが間違っているか、存在しないディレクトリを指しています。パスを再確認してください。
-   **「Invalid path specified.」エラー**: 指定されたパスが、許可されたベースディレクトリ（`/Users/mo/Projects/`）の外を指しています。セキュリティ上の理由から、このディレクトリ外のパスは許可されていません。
-   **Mermaid図が表示されない**: ブラウザのコンソールにエラーが出ていないか確認してください。Mermaid.jsのレンダリングに問題がある可能性があります。

ご不明な点がありましたら、開発者にお問い合わせください。

### PDF出力に関する注意点

生成されるPDFファイルで日本語が正しく表示されない場合、システムに適切な日本語フォントがインストールされていない可能性があります。多くのシステムでは、以下のフォントが利用可能です。

-   Windows: Meiryo, Yu Gothic
-   macOS: Hiragino Kaku Gothic ProN, Yu Gothic
-   Linux: Noto Sans CJK JP, Takao Gothic

これらのフォントがインストールされていることを確認するか、必要に応じてインストールしてください。
"""
    return manual

def convert_markdown_to_pdf(markdown_content, output_pdf_path):
    # 日本語フォントを優先的に使用するCSSスタイルを追加
    html_content = f"""
    <style>
        body {{ font-family: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif; }}
        pre.mermaid {{ font-family: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', 'Meiryo', monospace; }}
    </style>
    """
    html_content += markdown.markdown(markdown_content, extensions=['fenced_code', 'tables'])
    
    # Mermaid.jsのコードブロックをHTMLに変換する際に、Mermaid.jsがレンダリングできるようにclassを追加
    # xhtml2pdfはJavaScriptを実行しないため、Mermaid図はPDFには直接レンダリングされません。
    # ここでは、Mermaidのコードブロックをそのまま表示する形になります。
    html_content = html_content.replace('<pre><code class="language-mermaid">', '<pre class="mermaid"><code class="language-mermaid">')
    
    # PDF変換
    with open(output_pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(
                html_content,                # the HTML to convert
                dest=pdf_file)              # file handle to receive result
    return not pisa_status.err

@app.post("/api/generate-doc")
async def generate_doc(request: PathRequest):
    user_path = request.path
    
    # ユーザーが入力するパスの基準となるディレクトリ
    base_project_dir = os.path.abspath('/Users/mo/Projects')
    
    # ユーザーが指定したパスを、base_project_dir を基準に解決
    target_path = os.path.abspath(os.path.join(base_project_dir, user_path))

    # このアプリケーションのルートディレクトリ（backend/main.py が存在するディレクトリの2つ上）
    app_root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # セキュリティチェック：指定されたパスが base_project_dir 内にあることを確認
    if not os.path.commonpath([base_project_dir, target_path]) == base_project_dir:
        raise HTTPException(status_code=400, detail="Invalid path specified. Path must be within the allowed base directory (/Users/mo/Projects/).")

    if not os.path.isdir(target_path):
        raise HTTPException(status_code=404, detail="Directory not found.")

    try:
        tree_doc = generate_directory_tree(target_path)
        deps = analyze_dependencies(target_path)
        mermaid_graph = to_mermaid_graph(deps)

        # フロントエンドに返すドキュメント
        doc_content = f"""
# プロジェクトドキュメント

## フォルダ構成

```
{tree_doc}
```

## システム依存関係図

```mermaid
{mermaid_graph}
```
"""
        
        # プロジェクト概要ファイルを保存 (Markdown & PDF)
        project_name = os.path.basename(target_path)
        summary_content = generate_project_summary(project_name, tree_doc, mermaid_graph)
        output_summary_md_path = os.path.join(target_path, f"{project_name}_project_summary.md")
        output_summary_pdf_path = os.path.join(target_path, f"{project_name}_project_summary.pdf")
        with open(output_summary_md_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        convert_markdown_to_pdf(summary_content, output_summary_pdf_path)

        # 開発者ガイドを保存 (Markdown & PDF)
        developer_guide_content = generate_developer_guide()
        output_developer_guide_md_path = os.path.join(target_path, 'DEVELOPER_GUIDE.md')
        output_developer_guide_pdf_path = os.path.join(target_path, 'DEVELOPER_GUIDE.pdf')
        with open(output_developer_guide_md_path, 'w', encoding='utf-8') as f:
            f.write(developer_guide_content)
        convert_markdown_to_pdf(developer_guide_content, output_developer_guide_pdf_path)

        # ユーザーマニュアルを保存 (Markdown & PDF)
        user_manual_content = generate_user_manual()
        output_user_manual_md_path = os.path.join(target_path, 'USER_MANUAL.md')
        output_user_manual_pdf_path = os.path.join(target_path, 'USER_MANUAL.pdf')
        with open(output_user_manual_md_path, 'w', encoding='utf-8') as f:
            f.write(user_manual_content)
        convert_markdown_to_pdf(user_manual_content, output_user_manual_pdf_path)

        return {"document": doc_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ドキュメントの生成に失敗しました: {e}")