import { useState } from 'react';
import { Info } from 'lucide-react';
import UploadForm from './components/UploadForm';
import JobStatus from './components/JobStatus';
import ReportViewer from './components/ReportViewer';
import InfoSidebar from './components/InfoSidebar';

function App() {
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const resetFlow = () => {
    setJobId(null);
    setJobStatus(null);
  };

  return (
    <>
      <div className="glass-banner" style={{ position: 'relative' }}>
        <h1>DDR Generator</h1>
        <p>Automated Detailed Diagnosis Report for Property Inspections</p>

        <button
          onClick={() => setSidebarOpen(true)}
          className="info-blink-btn"
          aria-label="Open feature info sidebar"
        >
          <Info size={14} style={{ flexShrink: 0 }} />
          Tap here to know about this application
        </button>
      </div>

      {!jobId && <UploadForm onJobCreated={setJobId} />}

      {jobId && jobStatus !== 'complete' && jobStatus !== 'failed' && (
        <JobStatus jobId={jobId} onStatusChange={setJobStatus} />
      )}

      {jobId && jobStatus === 'complete' && (
        <ReportViewer jobId={jobId} onReset={resetFlow} />
      )}

      {jobId && jobStatus === 'failed' && (
        <div className="card" style={{ textAlign: 'center' }}>
          <h3 className="error-text" style={{ background: 'none' }}>Generation Failed</h3>
          <button onClick={resetFlow} style={{ marginTop: '1rem' }}>Try Again</button>
        </div>
      )}

      <InfoSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
    </>
  );
}

export default App;
