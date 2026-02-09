import { useState } from 'react';
import { Bold, Italic, Underline, Link as LinkIcon, List, Eye, Code, Heading } from 'lucide-react';

export default function MarkdownEditor({ value, onChange, placeholder }) {
    const [mode, setMode] = useState('write'); // 'write' | 'preview'

    const insertText = (before, after = '') => {
        const textarea = document.getElementById('markdown-textarea');
        if (!textarea) return;

        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const text = textarea.value;
        const beforeText = text.substring(0, start);
        const selectedText = text.substring(start, end);
        const afterText = text.substring(end);

        const newText = `${beforeText}${before}${selectedText}${after}${afterText}`;
        onChange(newText);

        // Restore selection (simulated, might not be perfect strictly after react render but good enough)
        setTimeout(() => {
            textarea.focus();
            textarea.setSelectionRange(start + before.length, end + before.length);
        }, 0);
    };

    const handleToolbarClick = (action) => {
        switch (action) {
            case 'bold': insertText('**', '**'); break;
            case 'italic': insertText('*', '*'); break;
            case 'heading': insertText('### '); break;
            case 'link': insertText('[', '](url)'); break;
            case 'list': insertText('- '); break;
            case 'code': insertText('`', '`'); break;
        }
    };

    // Simple Regex Parser for Preview
    const renderMarkdown = (text) => {
        if (!text) return <span className="text-slate-500 italic">Nothing to preview</span>;

        let html = text
            .replace(/^### (.*$)/gim, '<h3 class="text-lg font-bold text-white mt-4 mb-2">$1</h3>')
            .replace(/^## (.*$)/gim, '<h2 class="text-xl font-bold text-white mt-5 mb-2">$1</h2>')
            .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold text-white mt-6 mb-4">$1</h1>')
            .replace(/\*\*(.*)\*\*/gim, '<strong class="text-cyan-400 font-bold">$1</strong>')
            .replace(/\*(.*)\*/gim, '<em class="text-slate-300">$1</em>')
            .replace(/\[(.*?)\]\((.*?)\)/gim, '<a href="$2" target="_blank" class="text-cyan-500 hover:underline">$1</a>')
            .replace(/`(.*?)`/gim, '<code class="bg-slate-800 px-1 py-0.5 rounded text-sm font-mono text-cyan-300">$1</code>')
            .replace(/^\- (.*$)/gim, '<li class="ml-4 list-disc text-slate-300">$1</li>')
            .replace(/\n/gim, '<br />');

        return <div dangerouslySetInnerHTML={{ __html: html }} className="prose prose-invert max-w-none text-slate-300 leading-relaxed" />;
    };

    return (
        <div className="rounded-xl border border-slate-700 bg-slate-900/50 overflow-hidden group focus-within:ring-2 focus-within:ring-cyan-500/20 focus-within:border-cyan-500 transition-all">
            {/* Toolbar */}
            <div className="flex items-center justify-between p-2 border-b border-slate-700 bg-slate-800/50">
                <div className="flex gap-1">
                    <button onClick={() => handleToolbarClick('bold')} className="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors" title="Bold">
                        <Bold size={16} />
                    </button>
                    <button onClick={() => handleToolbarClick('italic')} className="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors" title="Italic">
                        <Italic size={16} />
                    </button>
                    <button onClick={() => handleToolbarClick('heading')} className="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors" title="Heading">
                        <Heading size={16} />
                    </button>
                    <div className="w-px h-4 bg-slate-700 mx-1 self-center"></div>
                    <button onClick={() => handleToolbarClick('link')} className="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors" title="Link">
                        <LinkIcon size={16} />
                    </button>
                    <button onClick={() => handleToolbarClick('list')} className="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors" title="List">
                        <List size={16} />
                    </button>
                    <button onClick={() => handleToolbarClick('code')} className="p-1.5 hover:bg-slate-700 rounded text-slate-400 hover:text-white transition-colors" title="Code">
                        <Code size={16} />
                    </button>
                </div>

                <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-700">
                    <button
                        onClick={() => setMode('write')}
                        className={`px-3 py-1 rounded text-xs font-bold transition-colors ${mode === 'write' ? 'bg-cyan-500 text-slate-900' : 'text-slate-400 hover:text-white'}`}
                    >
                        Write
                    </button>
                    <button
                        onClick={() => setMode('preview')}
                        className={`px-3 py-1 rounded text-xs font-bold transition-colors ${mode === 'preview' ? 'bg-cyan-500 text-slate-900' : 'text-slate-400 hover:text-white'}`}
                    >
                        Preview
                    </button>
                </div>
            </div>

            {/* Editor Area */}
            <div className="min-h-[200px] bg-slate-900/30">
                {mode === 'write' ? (
                    <textarea
                        id="markdown-textarea"
                        value={value}
                        onChange={(e) => onChange(e.target.value)}
                        rows={8}
                        placeholder={placeholder}
                        className="w-full px-5 py-6 bg-transparent border-none focus:outline-none resize-none text-slate-300 leading-relaxed text-lg placeholder:text-slate-600 font-mono"
                    />
                ) : (
                    <div className="px-5 py-6 min-h-[200px]">
                        {renderMarkdown(value)}
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="flex justify-between items-center px-4 py-2 text-[10px] font-bold uppercase text-slate-500 border-t border-slate-700/50 bg-slate-900/30">
                <span>Markdown Supported</span>
                <span>{value.length}/2000 characters</span>
            </div>
        </div>
    );
}
