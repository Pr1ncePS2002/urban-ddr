import { useState } from 'react';
import { Eye, EyeOff, KeyRound } from 'lucide-react';

const PROVIDER_META = {
    gemini: {
        label: 'Google Gemini',
        placeholder: 'AIza...',
        hint: 'Get your key at aistudio.google.com',
        color: '#4285F4',
    },
    openai: {
        label: 'OpenAI',
        placeholder: 'sk-...',
        hint: 'Get your key at platform.openai.com/api-keys',
        color: '#10A37F',
    },
    anthropic: {
        label: 'Anthropic (Claude)',
        placeholder: 'sk-ant-...',
        hint: 'Get your key at console.anthropic.com/settings/keys',
        color: '#D97757',
    },
};

const ApiKeySection = ({ apiKey, onApiKeyChange, provider, onProviderChange }) => {
    const [showKey, setShowKey] = useState(false);
    const meta = PROVIDER_META[provider] || PROVIDER_META.gemini;

    return (
        <div style={{
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.12)',
            borderRadius: '10px',
            padding: '1.25rem',
            marginBottom: '1.5rem',
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
                <KeyRound size={16} color={meta.color} />
                <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>API Key</span>
                <span style={{
                    marginLeft: 'auto',
                    fontSize: '0.7rem',
                    background: 'rgba(255,255,255,0.08)',
                    padding: '2px 8px',
                    borderRadius: '20px',
                    color: '#aaa',
                }}>Required</span>
            </div>

            <label className="label" style={{ marginBottom: '6px' }}>Provider</label>
            <select
                value={provider}
                onChange={(e) => {
                    onProviderChange(e.target.value);
                    onApiKeyChange('');
                }}
                style={{ marginBottom: '1rem' }}
            >
                {Object.entries(PROVIDER_META).map(([key, m]) => (
                    <option key={key} value={key}>{m.label}</option>
                ))}
            </select>

            <label className="label" style={{ marginBottom: '6px' }}>{meta.label} API Key</label>
            <div style={{ position: 'relative' }}>
                <input
                    type={showKey ? 'text' : 'password'}
                    value={apiKey}
                    onChange={(e) => onApiKeyChange(e.target.value)}
                    placeholder={meta.placeholder}
                    required
                    style={{
                        paddingRight: '80px',
                        borderColor: apiKey ? meta.color : undefined,
                        outline: apiKey ? `1px solid ${meta.color}33` : undefined,
                    }}
                />
                <button
                    type="button"
                    onClick={() => setShowKey((v) => !v)}
                    style={{
                        position: 'absolute',
                        right: '8px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        width: 'auto',
                        padding: '4px 10px',
                        background: 'transparent',
                        color: '#aaa',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: '0.8rem',
                    }}
                    aria-label={showKey ? 'Hide API key' : 'Show API key'}
                >
                    {showKey ? <EyeOff size={14} /> : <Eye size={14} />}
                    {showKey ? 'Hide' : 'Show'}
                </button>
            </div>

            {!apiKey && (
                <p style={{ fontSize: '0.78rem', color: '#e57373', marginTop: '6px', marginBottom: 0 }}>
                    An API key is required to generate a report.
                </p>
            )}

            <p style={{ fontSize: '0.75rem', color: '#888', marginTop: '6px', marginBottom: '10px' }}>
                {meta.hint} &mdash; your key is used only for this request and never stored.
            </p>

            <div style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '8px',
                background: 'rgba(245, 166, 35, 0.08)',
                border: '1px solid rgba(245, 166, 35, 0.3)',
                borderRadius: '8px',
                padding: '10px 12px',
            }}>
                <span style={{ fontSize: '1rem', flexShrink: 0, marginTop: '1px' }}>⚠️</span>
                <p style={{ fontSize: '0.75rem', color: '#F5A623', margin: 0, lineHeight: 1.5 }}>
                    <strong>Use a paid API key.</strong> Generating a 20-page DDR report makes dozens of LLM and embedding calls.
                    Free-tier keys will hit quota limits and cause the job to fail mid-way.
                    A paid key (Gemini, OpenAI, or Anthropic) ensures the full report completes without interruption.
                </p>
            </div>
        </div>
    );
};

export default ApiKeySection;
