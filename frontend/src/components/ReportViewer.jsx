import { useEffect, useState } from 'react';
import { getDownloadUrl, getJobStatus } from '../api';
import { Download, RefreshCcw } from 'lucide-react';

const ReportViewer = ({ jobId, onReset }) => {
    const [timeTaken, setTimeTaken] = useState('');

    useEffect(() => {
        const fetchTiming = async () => {
            try {
                const data = await getJobStatus(jobId);
                if (data.created_at && data.updated_at) {
                    const start = new Date(data.created_at);
                    const end = new Date(data.updated_at);
                    const diffSeconds = Math.round((end - start) / 1000);
                    setTimeTaken(`${diffSeconds} seconds`);
                }
            } catch (e) {
                console.error(e);
            }
        };
        fetchTiming();
    }, [jobId]);

    const handleDownload = () => {
        const url = getDownloadUrl(jobId);
        window.open(url, '_blank');
    };

    return (
        <div className="card" style={{textAlign: "center"}}>
            <h2 className="success-text" style={{marginBottom: '0.5rem'}}>Report Ready!</h2>
            <p style={{color: '#aaa', margin: '0 0 2rem 0'}}>Your Detailed Diagnosis Report has been generated successfully.</p>
            
            <div className="summary-card" style={{background: 'rgba(0,0,0,0.2)', padding: '1.5rem', borderRadius: '8px', marginBottom: '2rem'}}>
                <p>Job ID: <strong>{jobId.substring(0, 8)}</strong></p>
                <p>Processing Time: <strong>{timeTaken || 'Calculating...'}</strong></p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <button 
                    onClick={handleDownload}
                    style={{display: 'flex', justifyContent: 'center', alignItems: 'center'}}
                >
                    <Download size={18} style={{marginRight: '8px'}} />
                    Download DDR Report (PDF)
                </button>
                
                <button 
                    onClick={onReset}
                    style={{background: 'transparent', border: '1px solid #F5A623', color: '#F5A623', display: 'flex', justifyContent: 'center', alignItems: 'center'}}
                >
                    <RefreshCcw size={18} style={{marginRight: '8px'}} />
                    Generate Another Report
                </button>
            </div>
        </div>
    );
};

export default ReportViewer;
