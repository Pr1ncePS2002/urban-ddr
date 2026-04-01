import { useState } from 'react';
import { generateReport } from '../api';
import { ChevronDown, ChevronUp } from 'lucide-react';
import ApiKeySection from './ApiKeySection';

const UploadForm = ({ onJobCreated }) => {
    const [apiKey, setApiKey] = useState('');
    const [keyProvider, setKeyProvider] = useState('gemini');

    const [inspectionPdf, setInspectionPdf] = useState(null);
    const [thermalPdf, setThermalPdf] = useState(null);

    // Advanced options — default to whatever provider the user chose for their key
    const [llmProvider, setLlmProvider] = useState('gemini');
    const [visionProvider, setVisionProvider] = useState('gemini');
    const [embedProvider, setEmbedProvider] = useState('gemini');

    const [advancedOpen, setAdvancedOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // When the user switches key-provider, auto-align LLM + Embed to match
    const handleKeyProviderChange = (provider) => {
        setKeyProvider(provider);
        setLlmProvider(provider);
        // Anthropic has no native embed; keep embed on gemini/openai if possible
        if (provider !== 'anthropic') {
            setEmbedProvider(provider);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!apiKey.trim()) {
            setError('An API key is required to generate a report.');
            return;
        }
        if (!inspectionPdf || !thermalPdf) {
            setError('Please provide both PDF files.');
            return;
        }

        setLoading(true);
        const formData = new FormData();
        formData.append('api_key', apiKey.trim());
        formData.append('inspection_pdf', inspectionPdf);
        formData.append('thermal_pdf', thermalPdf);
        formData.append('llm_provider', llmProvider);
        formData.append('vision_provider', visionProvider);
        formData.append('embed_provider', embedProvider);

        try {
            const data = await generateReport(formData);
            if (data.job_id) {
                onJobCreated(data.job_id);
            }
        } catch (err) {
            let msg = 'Failed to submit job. Please try again.';
            if (err.response?.data?.detail) {
                const detail = err.response.data.detail;
                msg = typeof detail === 'string' ? detail : detail.map((d) => d.msg).join(', ');
            }
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    const isReady = inspectionPdf && thermalPdf && apiKey.trim();

    return (
        <div className="card">
            <h2>Start New Report</h2>
            {error && <div className="error-text">{error}</div>}

            <form onSubmit={handleSubmit}>
                {/* ── API Key ── */}
                <ApiKeySection
                    apiKey={apiKey}
                    onApiKeyChange={setApiKey}
                    provider={keyProvider}
                    onProviderChange={handleKeyProviderChange}
                />

                {/* ── File Uploads ── */}
                <label className="label">Inspection Report PDF</label>
                <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setInspectionPdf(e.target.files[0])}
                    required
                />

                <label className="label">Thermal Images PDF</label>
                <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setThermalPdf(e.target.files[0])}
                    required
                />

                {/* ── Advanced Options ── */}
                <div style={{ marginTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1rem' }}>
                    <button
                        type="button"
                        onClick={() => setAdvancedOpen(!advancedOpen)}
                        style={{
                            background: 'transparent',
                            color: '#ccc',
                            textAlign: 'left',
                            padding: '0',
                            display: 'flex',
                            alignItems: 'center',
                        }}
                    >
                        {advancedOpen
                            ? <ChevronUp size={16} style={{ marginRight: '8px' }} />
                            : <ChevronDown size={16} style={{ marginRight: '8px' }} />}
                        Advanced Options
                    </button>

                    {advancedOpen && (
                        <div style={{ marginTop: '1rem' }}>
                            <label className="label">LLM Provider</label>
                            <select value={llmProvider} onChange={(e) => setLlmProvider(e.target.value)}>
                                <option value="gemini">Gemini</option>
                                <option value="openai">OpenAI</option>
                                <option value="anthropic">Anthropic (Claude)</option>
                            </select>

                            <label className="label">Vision Provider</label>
                            <select value={visionProvider} onChange={(e) => setVisionProvider(e.target.value)}>
                                <option value="gemini">Gemini</option>
                                <option value="openai">OpenAI</option>
                                <option value="anthropic">Anthropic (Claude)</option>
                            </select>

                            <label className="label">Embed Provider</label>
                            <select value={embedProvider} onChange={(e) => setEmbedProvider(e.target.value)}>
                                <option value="gemini">Gemini</option>
                                <option value="openai">OpenAI</option>
                            </select>

                            {llmProvider === 'anthropic' && embedProvider === 'anthropic' && (
                                <p style={{ fontSize: '0.78rem', color: '#e57373', marginTop: '6px' }}>
                                    Anthropic does not support embeddings. Please select Gemini or OpenAI as the Embed Provider, and supply the corresponding key.
                                </p>
                            )}
                        </div>
                    )}
                </div>

                <div style={{ marginTop: '2rem' }}>
                    <button type="submit" disabled={!isReady || loading}>
                        {loading ? 'Submitting...' : 'Generate DDR Report'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default UploadForm;
