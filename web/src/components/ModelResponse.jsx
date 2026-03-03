import ReactMarkdown from 'react-markdown'

const MODEL_COLORS = {
  gpt4: '#74aa9c',
  claude: '#d4a574',
  gemini: '#8b9cf7',
  deepseek: '#7ecfcf',
  grok: '#e87777',
  mistral: '#c084fc',
  llama: '#94a3b8',
}

const MODEL_NAMES = {
  gpt4: 'GPT-4',
  claude: 'Claude',
  gemini: 'Gemini',
  deepseek: 'DeepSeek',
  grok: 'Grok',
  mistral: 'Mistral',
  llama: 'Llama',
}

export { MODEL_COLORS, MODEL_NAMES }

export default function ModelResponse({ model, text, compact = false }) {
  const color = MODEL_COLORS[model] || '#94a3b8'
  const name = MODEL_NAMES[model] || model

  if (!text) return null

  return (
    <div className="border border-border rounded overflow-hidden">
      <div
        className="px-3 py-1.5 text-xs font-medium flex items-center gap-2"
        style={{ borderLeft: `3px solid ${color}` }}
      >
        <span style={{ color }}>{name}</span>
      </div>
      <div className={`px-3 pb-3 text-xs leading-relaxed text-gray-300 ${compact ? 'max-h-48 overflow-y-auto' : ''}`}>
        <div className="prose prose-invert prose-xs max-w-none">
          <ReactMarkdown>{text}</ReactMarkdown>
        </div>
      </div>
    </div>
  )
}
