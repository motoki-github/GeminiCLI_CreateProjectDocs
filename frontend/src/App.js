import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import mermaid from 'mermaid';
import './App.css';

mermaid.initialize({ startOnLoad: false, theme: 'forest' });

function App() {
  const [path, setPath] = useState('Gemini_CLI/backend'); // 初期値を設定
  const [docContent, setDocContent] = useState(''); // 変数名を document から docContent に変更
  const [loading, setLoading] = useState(false);
  const markdownRef = useRef(null); // 結果表示エリアへの参照

  useEffect(() => {
    if (docContent && markdownRef.current) {
      try {
        // markdownRef.current の中にある mermaid クラスを持つ要素を探してレンダリング
        const mermaidElements = markdownRef.current.querySelectorAll('.language-mermaid');
        if (mermaidElements.length > 0) {
            mermaid.run({
                nodes: mermaidElements,
            });
        }
      } catch (e) {
        console.error('Mermaid rendering error:', e);
      }
    }
  }, [docContent]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setDocContent('');
    try {
      const response = await fetch('http://localhost:8000/api/generate-doc', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ path }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'ドキュメントの生成に失敗しました。');
      }
      const data = await response.json();
      setDocContent(data.document); // 正しい変数にセット
    } catch (error) {
      console.error('ドキュメント生成エラー:', error);
      setDocContent(`エラー: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>プロジェクトドキュメント生成ツール</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={path}
            onChange={(e) => setPath(e.target.value)}
            placeholder="プロジェクトのパスを入力 (例: Gemini_CLI/backend)"
            style={{ width: '400px', padding: '10px' }}
          />
          <button type="submit" disabled={loading} style={{ padding: '10px' }}>
            {loading ? '生成中...' : 'ドキュメントを生成'}
          </button>
        </form>
        <div ref={markdownRef} style={{ width: '80%', textAlign: 'left', marginTop: '20px', backgroundColor: '#fff', padding: '20px', borderRadius: '5px', color: '#333' }}>
          <ReactMarkdown components={{
            code({node, inline, className, children, ...props}) {
              const match = /language-(\w+)/.exec(className || '')
              return !inline && match && match[1] === 'mermaid' ? 
                <div className="language-mermaid">{String(children)}</div> : 
                <code className={className} {...props}>{children}</code>
            }
          }}>
            {docContent}{/* 正しい変数を参照 */}
          </ReactMarkdown>
        </div>
      </header>
    </div>
  );
}

export default App;
