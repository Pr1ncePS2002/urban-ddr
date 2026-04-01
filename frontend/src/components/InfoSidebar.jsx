import { X, ShieldCheck, Zap, RefreshCw, Layers, Lock, AlertTriangle, Cpu, TrendingUp, Globe } from 'lucide-react';

const Section = ({ icon: Icon, color, title, children }) => (
    <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '0.6rem' }}>
            <div style={{
                width: '32px', height: '32px', borderRadius: '8px',
                background: `${color}22`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
            }}>
                <Icon size={16} color={color} />
            </div>
            <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700, color: '#fff' }}>{title}</h3>
        </div>
        <div style={{ paddingLeft: '42px', fontSize: '0.82rem', color: '#bbb', lineHeight: 1.7 }}>
            {children}
        </div>
    </div>
);

const Pill = ({ label, color }) => (
    <span style={{
        display: 'inline-block', fontSize: '0.7rem', fontWeight: 600,
        padding: '2px 8px', borderRadius: '20px', marginRight: '6px', marginBottom: '4px',
        background: `${color}22`, color: color, border: `1px solid ${color}44`,
    }}>{label}</span>
);

const RoadmapItem = ({ status, text }) => {
    const colors = { done: '#2ecc71', planned: '#F5A623', idea: '#4285F4' };
    const labels = { done: '✓ Live', planned: '⏳ Planned', idea: '💡 Idea' };
    return (
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', marginBottom: '8px' }}>
            <span style={{
                fontSize: '0.65rem', fontWeight: 700, padding: '2px 7px', borderRadius: '20px', flexShrink: 0, marginTop: '2px',
                background: `${colors[status]}22`, color: colors[status], border: `1px solid ${colors[status]}44`,
            }}>{labels[status]}</span>
            <span style={{ fontSize: '0.82rem', color: '#ccc', lineHeight: 1.5 }}>{text}</span>
        </div>
    );
};

const InfoSidebar = ({ open, onClose }) => {
    return (
        <>
            {/* Backdrop */}
            {open && (
                <div
                    onClick={onClose}
                    style={{
                        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)',
                        zIndex: 999, backdropFilter: 'blur(2px)',
                    }}
                />
            )}

            {/* Drawer */}
            <div style={{
                position: 'fixed', top: 0, right: 0, bottom: 0,
                width: 'min(480px, 100vw)',
                background: '#12122a',
                borderLeft: '1px solid rgba(255,255,255,0.1)',
                zIndex: 1000,
                transform: open ? 'translateX(0)' : 'translateX(100%)',
                transition: 'transform 0.3s cubic-bezier(0.4,0,0.2,1)',
                display: 'flex', flexDirection: 'column',
                boxShadow: '-8px 0 40px rgba(0,0,0,0.5)',
            }}>
                {/* Header */}
                <div style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    padding: '1.25rem 1.5rem',
                    borderBottom: '1px solid rgba(255,255,255,0.08)',
                    flexShrink: 0,
                }}>
                    <div>
                        <h2 style={{ margin: 0, fontSize: '1.1rem', color: '#F5A623' }}>How This App Works</h2>
                        <p style={{ margin: '4px 0 0', fontSize: '0.75rem', color: '#888' }}>
                            Production architecture &amp; roadmap
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        style={{
                            width: '32px', height: '32px', padding: 0, borderRadius: '8px',
                            background: 'rgba(255,255,255,0.07)', color: '#ccc',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                        }}
                        aria-label="Close"
                    >
                        <X size={16} />
                    </button>
                </div>

                {/* Scrollable body */}
                <div style={{ overflowY: 'auto', padding: '1.5rem', flex: 1 }}>

                    {/* ── API Key Security ── */}
                    <Section icon={Lock} color="#F5A623" title="Zero-Persistence API Keys">
                        Your API key is transmitted over HTTPS, used <strong style={{ color: '#fff' }}>in-memory only</strong> for
                        the duration of the job, and immediately discarded. It is never written to disk, never logged,
                        and never stored in any database. If an error occurs, the key is automatically redacted from
                        the error message before it reaches any log.
                        <br /><br />
                        <Pill label="Form(None) in FastAPI" color="#F5A623" />
                        <Pill label="Redacted in worker errors" color="#F5A623" />
                        <Pill label="Never persisted" color="#F5A623" />
                    </Section>

                    {/* ── Multi-Key Round Robin ── */}
                    <Section icon={RefreshCw} color="#4285F4" title="Multi-Key Round-Robin Retry">
                        The backend implements a <strong style={{ color: '#fff' }}>RoundRobinLLMProvider</strong> and
                        <strong style={{ color: '#fff' }}> RoundRobinEmbedProvider</strong>. If you supply multiple
                        comma-separated API keys, requests are distributed across all keys in rotation.
                        When a key hits a <code style={{ color: '#4285F4' }}>429 / quota exhausted</code> error, the
                        system automatically retries with the next key. After all keys are exhausted in one cycle,
                        it backs off for 33 seconds before retrying the full pool — up to 5× per key.
                        <br /><br />
                        <Pill label="Round-robin distribution" color="#4285F4" />
                        <Pill label="Auto rate-limit retry" color="#4285F4" />
                        <Pill label="33s backoff between cycles" color="#4285F4" />
                        <Pill label="Up to 5× retries per key" color="#4285F4" />
                    </Section>

                    {/* ── Multi-Provider ── */}
                    <Section icon={Layers} color="#10A37F" title="Multi-Provider Support">
                        Three LLM providers are supported interchangeably — <strong style={{ color: '#fff' }}>Google Gemini</strong>,{' '}
                        <strong style={{ color: '#fff' }}>OpenAI GPT-4o</strong>, and{' '}
                        <strong style={{ color: '#fff' }}>Anthropic Claude 3.5 Sonnet</strong>. Each provider
                        implements the same <code style={{ color: '#10A37F' }}>AbstractLLMProvider</code> interface, so
                        swapping providers requires zero pipeline changes. Embeddings are handled by Gemini or OpenAI;
                        when using Anthropic for LLM, the app uses a "describe-then-embed" strategy — Claude describes
                        the image, then a Gemini/OpenAI model embeds the description.
                        <br /><br />
                        <Pill label="Gemini 2.0 Flash" color="#4285F4" />
                        <Pill label="GPT-4o" color="#10A37F" />
                        <Pill label="Claude 3.5 Sonnet" color="#D97757" />
                        <Pill label="Describe-then-embed fallback" color="#888" />
                    </Section>

                    {/* ── Pipeline ── */}
                    <Section icon={Cpu} color="#9b59b6" title="7-Stage Report Pipeline">
                        Each job runs through a fully async pipeline:
                        <ol style={{ paddingLeft: '1.2rem', margin: '8px 0 0' }}>
                            <li><strong style={{ color: '#fff' }}>Extract</strong> — PyMuPDF + pdfplumber parse text &amp; images from both PDFs.</li>
                            <li><strong style={{ color: '#fff' }}>Analyze Images</strong> — Vision LLM describes every thermal/inspection image.</li>
                            <li><strong style={{ color: '#fff' }}>Merge</strong> — Inspection and thermal documents are combined into a unified structure.</li>
                            <li><strong style={{ color: '#fff' }}>Conflict Detection</strong> — Contradictions between reports are flagged automatically.</li>
                            <li><strong style={{ color: '#fff' }}>Deduplication</strong> — ChromaDB vector similarity removes duplicate observations (threshold: 0.85).</li>
                            <li><strong style={{ color: '#fff' }}>Report Generation</strong> — LLM synthesises the final DDR narrative.</li>
                            <li><strong style={{ color: '#fff' }}>PDF Render</strong> — WeasyPrint produces a styled, downloadable PDF.</li>
                        </ol>
                    </Section>

                    {/* ── Security ── */}
                    <Section icon={ShieldCheck} color="#2ecc71" title="Security Practices">
                        <ul style={{ paddingLeft: '1.2rem', margin: 0 }}>
                            <li>File uploads are validated for <code>.pdf</code> extension and capped at 50 MB.</li>
                            <li>Provider names are validated against an allowlist before use.</li>
                            <li>Gemini keys are validated for the <code>AIza</code> prefix before the job starts.</li>
                            <li>Temporary files are cleaned up after every job, success or failure.</li>
                            <li>Jobs expire from memory after 1 hour (configurable TTL).</li>
                            <li>CORS is locked to <code>localhost:5173</code> and <code>*.vercel.app</code> origins.</li>
                        </ul>
                    </Section>

                    {/* ── Paid Key Notice ── */}
                    <Section icon={AlertTriangle} color="#e67e22" title="Why You Need a Paid API Key">
                        Generating a 20-page DDR report involves <strong style={{ color: '#fff' }}>30–80+ LLM calls</strong> (image
                        analysis, conflict detection, deduplication, report generation) plus dozens of embedding calls.
                        Free-tier keys from Google AI Studio, OpenAI, or Anthropic have strict per-minute and per-day
                        quotas that will cause the job to fail mid-pipeline.
                        <br /><br />
                        A <strong style={{ color: '#fff' }}>paid key</strong> (even a low-spend account) will handle a
                        full report without interruption. The multi-key retry logic provides additional resilience if
                        you supply multiple keys.
                    </Section>

                    {/* ── Roadmap ── */}
                    <Section icon={TrendingUp} color="#F5A623" title="Roadmap &amp; Improvements">
                        <RoadmapItem status="done" text="Multi-provider support: Gemini, OpenAI, Anthropic" />
                        <RoadmapItem status="done" text="Round-robin multi-key retry with rate-limit backoff" />
                        <RoadmapItem status="done" text="Zero-persistence API key handling" />
                        <RoadmapItem status="done" text="ChromaDB semantic deduplication of observations" />
                        <RoadmapItem status="done" text="Conflict detection between inspection & thermal reports" />
                        <RoadmapItem status="planned" text="Redis-backed job queue (replace in-memory JOB_STORE) for multi-worker deployments" />
                        <RoadmapItem status="planned" text="Horizontal load balancing — run multiple FastAPI workers behind Nginx or a cloud load balancer so concurrent jobs don't block each other" />
                        <RoadmapItem status="planned" text="GCS / S3 storage backend for result PDFs (already wired in config)" />
                        <RoadmapItem status="planned" text="Webhook / email notification when a long job completes" />
                        <RoadmapItem status="idea" text="Bring-your-own model: let users point to a self-hosted Ollama or Azure OpenAI endpoint" />
                        <RoadmapItem status="idea" text="Streaming progress — push real-time pipeline stage updates via WebSocket instead of polling" />
                        <RoadmapItem status="idea" text="Audit log: optional server-side log of job metadata (no keys) for analytics" />
                        <RoadmapItem status="idea" text="Multi-region deployment with latency-based routing for global users" />
                    </Section>

                    {/* ── Load Balancing note ── */}
                    <Section icon={Globe} color="#4285F4" title="Load Balancing (How It Would Work)">
                        Currently the app runs as a single FastAPI process. To scale:
                        <ol style={{ paddingLeft: '1.2rem', margin: '8px 0 0' }}>
                            <li>Replace the in-memory <code>JOB_STORE</code> dict with a <strong style={{ color: '#fff' }}>Redis</strong> instance so all workers share state.</li>
                            <li>Run <strong style={{ color: '#fff' }}>N Uvicorn workers</strong> (or Gunicorn with Uvicorn workers) behind an <strong style={{ color: '#fff' }}>Nginx</strong> reverse proxy or a cloud load balancer (AWS ALB, GCP HTTPS LB).</li>
                            <li>Move background tasks to a proper queue (<strong style={{ color: '#fff' }}>Celery + Redis</strong> or <strong style={{ color: '#fff' }}>ARQ</strong>) so heavy pipeline work runs in dedicated worker processes, not in the API process.</li>
                            <li>Store result PDFs in <strong style={{ color: '#fff' }}>GCS / S3</strong> so any worker can serve the download endpoint.</li>
                        </ol>
                        This architecture would support hundreds of concurrent report jobs with no single point of failure.
                    </Section>

                </div>

                {/* Footer */}
                <div style={{
                    padding: '1rem 1.5rem',
                    borderTop: '1px solid rgba(255,255,255,0.08)',
                    fontSize: '0.72rem', color: '#555', flexShrink: 0, textAlign: 'center',
                }}>
                    DDR Generator — keys are never stored &bull; built with FastAPI + React
                </div>
            </div>
        </>
    );
};

export default InfoSidebar;
