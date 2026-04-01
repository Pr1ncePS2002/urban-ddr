import { useEffect, useState } from 'react';
import { getJobStatus } from '../api';

const stages = {
    queued: "Queued...",
    extracting: "Extracting text and images from PDFs...",
    analyzing_images: "Analysing thermal and inspection images...",
    merging: "Merging and cross-referencing observations...",
    generating_report: "Generating DDR sections with AI...",
    rendering_pdf: "Rendering final PDF report...",
    complete: "Your DDR report is ready!",
    failed: "Generation failed."
};

const JobStatus = ({ jobId, onStatusChange }) => {
    const [statusData, setStatusData] = useState(null);

    useEffect(() => {
        let interval;
        const checkStatus = async () => {
            try {
                const data = await getJobStatus(jobId);
                setStatusData(data);
                
                if (data.status === 'complete' || data.status === 'failed') {
                    clearInterval(interval);
                    onStatusChange(data.status);
                }
            } catch (err) {
                console.error("Error fetching job status", err);
            }
        };

        checkStatus();
        interval = setInterval(checkStatus, 3000);

        return () => clearInterval(interval);
    }, [jobId, onStatusChange]);

    if (!statusData) {
        return <div className="card">Loading status...</div>;
    }

    const currentMessage = stages[statusData.status] || "Processing...";
    const progress = statusData.progress || 0;

    return (
        <div className="card text-center">
            <h3>Generating Report</h3>
            <p style={{ margin: '1.5rem 0', fontWeight: '500', color: '#F5A623' }}>
                {currentMessage}
            </p>
            <div className="progress-container">
                <div 
                    className="progress-bar" 
                    style={{ width: `${progress}%` }}
                ></div>
            </div>
            <p style={{ fontSize: '0.8rem', color: '#888' }}>
                {progress}% Complete
            </p>
        </div>
    );
};

export default JobStatus;
