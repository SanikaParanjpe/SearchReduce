export function StatisticsCard({statistics}) {
    
    return (
        <div className="statistics-container">
            <div className="statistics-header">Statistics</div>

            {
                statistics && <>
                    <div className="statistics-title">Documents Uploaded</div>
            <div className="statistics-value">{statistics.documents_uploaded}</div>

            <div className="statistics-title">Keywords Processed</div>
            <div className="statistics-value">{statistics.keywords_processed}</div>
                </>
            }
        </div>
    );
}