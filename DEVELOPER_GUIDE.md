
# 開発者ガイド

このドキュメントは、プロジェクトのバックエンドコード（`backend/main.py`）の主要な機能と構造を説明します。

## 主要な関数

### `generate_directory_tree(start_path: str) -> str`

- **説明**: 指定されたパス以下のディレクトリツリーをMarkdown形式の文字列として生成します。
- **引数**: `start_path` (str): ツリーを生成する開始ディレクトリの絶対パス。
- **戻り値**: (str): ディレクトリツリーを表すMarkdown形式の文字列。

### `analyze_dependencies(start_path: str) -> set[tuple[str, str]]`

- **説明**: 指定されたパス以下のPythonファイル（`.py`）を解析し、ファイル間のインポート依存関係を抽出します。
- **引数**: `start_path` (str): 依存関係を解析する開始ディレクトリの絶対パス。
- **戻り値**: (set[tuple[str, str]]): (依存元ファイル名, 依存先モジュール名) のタプルのセット。

### `to_mermaid_graph(dependencies: set[tuple[str, str]]) -> str`

- **説明**: 抽出された依存関係のセットをMermaid.js形式のグラフ定義文字列に変換します。
- **引数**: `dependencies` (set[tuple[str, str]]): `analyze_dependencies` から返される依存関係のセット。
- **戻り値**: (str): Mermaid.jsのグラフ定義文字列。

### `generate_project_summary(project_name: str, tree_doc: str, mermaid_graph: str) -> str`

- **説明**: プロジェクトの概要、フォルダ構成、システム依存関係図、動作概要、技術スタックを含むMarkdown形式のサマリーを生成します。
- **引数**:
  - `project_name` (str): プロジェクト名。
  - `tree_doc` (str): `generate_directory_tree` から生成されたディレクトリツリー。
  - `mermaid_graph` (str): `to_mermaid_graph` から生成されたMermaidグラフ定義。
- **戻り値**: (str): プロジェクトの概要を表すMarkdown形式の文字列。

### `generate_developer_guide() -> str`

- **説明**: この開発者ガイド自体を生成します。
- **引数**: なし。
- **戻り値**: (str): 開発者ガイドのMarkdown形式の文字列。

### `generate_user_manual() -> str`

- **説明**: ユーザー向け運用マニュアルを生成します。
- **引数**: なし。
- **戻り値**: (str): ユーザーマニュアルのMarkdown形式の文字列。

## APIエンドポイント

### `POST /api/generate-doc`

- **説明**: 指定されたプロジェクトパスのドキュメントを生成し、ブラウザに表示します。また、プロジェクト概要、開発者ガイド、ユーザーマニュアルをファイルとして保存します。
- **リクエストボディ**:

    ```json
    {
        "path": "string"
    }
    ```

- **レスポンス**:

    ```json
    {
        "document": "string"
    }
    ```

- **エラー**:
  - `400 Bad Request`: 無効なパスが指定された場合。
  - `404 Not Found`: 指定されたディレクトリが見つからない場合。
  - `500 Internal Server Error`: ドキュメント生成中に予期せぬエラーが発生した場合。

## 依存関係

- `FastAPI`: Web APIフレームワーク。
- `uvicorn`: ASGIサーバー。
- `pydantic`: データ検証と設定管理。
- `os`, `ast`: Python標準ライブラリ（ファイルシステム操作、AST解析）。
