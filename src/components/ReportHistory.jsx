import { reportService } from '../services/api';

const CLASS_NAMES = {
  0: "No DR",
  1: "Mild DR",
  2: "Moderate DR",
  3: "Severe DR",
  4: "Proliferative DR"
};

function ReportHistory({ reports, onRefresh }) {
  const handleDownload = (reportId) => {
    console.log('Handling download for report:', reportId);
    reportService.downloadReport(reportId);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getConfidenceColor = (confidence) => {
    const normalized = confidence > 1 ? confidence / 100 : confidence;
    if (normalized >= 0.8) return 'text-green-600';
    if (normalized >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatConfidence = (confidence) => {
    const percent = confidence > 1 ? confidence : confidence * 100;
    return `${percent.toFixed(2)}%`;
  };

  const getPredictionName = (prediction) => {
    return CLASS_NAMES[prediction] || `Unknown (${prediction})`;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-gray-900">Report History</h2>
        <button
          onClick={onRefresh}
          className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-lg transition"
        >
          Refresh
        </button>
      </div>

      {reports.length === 0 ? (
        <div className="text-center py-12">
          <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-gray-500">No reports analyzed yet</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">File Name</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Prediction</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Confidence</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Date</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Action</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((report) => (
                <tr key={report._id} className="border-b border-gray-100 hover:bg-gray-50 transition">
                  <td className="py-3 px-4 text-gray-700">{report.original_filename}</td>
                  <td className="py-3 px-4">
                    <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                      {getPredictionName(report.prediction)}
                    </span>
                  </td>
                  <td className={`py-3 px-4 font-semibold ${getConfidenceColor(report.confidence)}`}>
                    {formatConfidence(report.confidence)}
                  </td>
                  <td className="py-3 px-4 text-gray-600 text-sm">{formatDate(report.createdAt)}</td>
                  <td className="py-3 px-4">
                    <button
                      onClick={() => handleDownload(report._id)}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition"
                    >
                      Download
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default ReportHistory;
