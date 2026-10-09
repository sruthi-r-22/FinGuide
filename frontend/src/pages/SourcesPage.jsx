import React, { useCallback, useState, useEffect } from 'react';
import {
  FileText,
  RotateCw,
  ExternalLink,
  Layers,
  Calendar,
  Building,
  CheckCircle2,
  FolderPlus,
} from 'lucide-react';
import { api } from '../services/api';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { isGeneratedDemo, isVerifiedOfficialSource } from '../utils/sourceProvenance';

export default function SourcesPage() {
  const [sourcesData, setSourcesData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isReindexing, setIsReindexing] = useState(false);
  const [reindexMessage, setReindexMessage] = useState(null);
  const [backupPath, setBackupPath] = useState(null);
  const [reindexError, setReindexError] = useState(null);
  const [error, setError] = useState(null);

  const fetchSources = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getSources();
      setSourcesData(data);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch document sources. Please ensure backend is active.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    api.getSources()
      .then((data) => {
        if (isMounted) setSourcesData(data);
      })
      .catch((err) => {
        console.error(err);
        if (isMounted) {
          setError('Failed to fetch document sources. Please ensure backend is active.');
        }
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const handleReindex = async () => {
    if (!window.confirm(
      'Rebuild only FinGuide AI\'s document collection? A backup of the project-local Chroma data will be created first.'
    )) return;

    setIsReindexing(true);
    setReindexMessage(null);
    setReindexError(null);
    try {
      const res = await api.reindexSources();
      setReindexMessage(res.message);
      setBackupPath(res.backup_path || null);
      await fetchSources();
    } catch (err) {
      console.error(err);
      setReindexError(err.response?.data?.detail || 'Re-index failed. The existing index was not reported as replaced.');
    } finally {
      setIsReindexing(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="p-2 rounded-xl bg-slate-100 border border-slate-200 text-slate-700">
              <FileText className="w-5 h-5" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Sources & Provenance</h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-500">
            Review indexed document provenance. Generated demos and unverified references are clearly identified.
          </p>
        </div>

        <button
          onClick={handleReindex}
          disabled={isReindexing}
          className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 disabled:bg-slate-400 text-white font-semibold text-xs sm:text-sm shadow-md transition-all cursor-pointer shrink-0"
        >
          <RotateCw className={`w-4 h-4 ${isReindexing ? 'animate-spin' : ''}`} />
          <span>{isReindexing ? 'Re-indexing Chunks...' : 'Re-index Vector Store'}</span>
        </button>
      </div>

      {reindexMessage && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs flex items-center gap-2 animate-fade-in">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <div>
            <p>{reindexMessage}</p>
            {backupPath && <p className="mt-1">Previous Chroma data backed up to: <code>{backupPath}</code></p>}
          </div>
        </div>
      )}
      {reindexError && (
        <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-xl text-xs">
          {reindexError}
        </div>
      )}

      {/* Overview Stats */}
      {sourcesData && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Indexed Documents</span>
            <p className="text-2xl font-extrabold text-slate-900 mt-1">{sourcesData.documents.length}</p>
          </div>
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Vector Chunks</span>
            <p className="text-2xl font-extrabold text-blue-600 mt-1">{sourcesData.total_chunks}</p>
          </div>
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-2xs">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Index Status</span>
            <div className="flex items-center gap-2 mt-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-bold text-slate-800">{sourcesData.index_status}</span>
            </div>
          </div>
        </div>
      )}

      {/* Document Cards */}
      {isLoading ? (
        <LoadingSpinner text="Loading document collection..." />
      ) : error ? (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-2xl text-xs">
          {error}
        </div>
      ) : sourcesData && (
        <div className="space-y-4">
          <h2 className="text-base font-bold text-slate-900">Indexed Documents</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {sourcesData.documents.map((doc, idx) => (
              <div
                key={idx}
                className="bg-white p-5 rounded-2xl border border-slate-200 hover:border-blue-300 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between gap-4"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <h3 className="text-base font-bold text-slate-900 leading-snug">{doc.title}</h3>
                    <span className={`px-2 py-1 rounded-lg text-[10px] font-bold shrink-0 ${
                      isGeneratedDemo(doc)
                        ? 'bg-amber-100 text-amber-800'
                        : isVerifiedOfficialSource(doc)
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-slate-100 text-slate-700'
                    }`}>
                      {isGeneratedDemo(doc)
                        ? 'GENERATED DEMO'
                        : isVerifiedOfficialSource(doc)
                          ? 'VERIFIED OFFICIAL'
                          : 'PROVENANCE UNKNOWN'}
                    </span>
                  </div>

                  <div className="space-y-1.5 text-xs text-slate-600">
                    <div className="flex items-center gap-2">
                      <Building className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span><b>Publisher:</b> {doc.publisher || 'Unknown'}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Building className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span><b>Issuing organization:</b> {doc.authority || 'Unknown'}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span><b>Published:</b> {doc.published_date || 'Unknown'}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span><b>Last verified:</b> {doc.last_verified || 'Unknown / not verified'}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Layers className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span><b>Chunks:</b> {doc.chunks_count} chunks ({doc.pages_count} pages)</span>
                    </div>
                    <div className="font-mono text-[11px] text-slate-500 bg-slate-50 p-2 rounded-lg border border-slate-100">
                      {doc.filename}
                    </div>
                    <div className="font-mono text-[10px] text-slate-500">
                      Document ID: {doc.document_id}
                    </div>
                    {doc.provenance_note && (
                      <p className="rounded-lg bg-amber-50 border border-amber-100 p-2 text-[11px] text-amber-900">
                        {doc.provenance_note}
                      </p>
                    )}
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                  <span className="text-[11px] text-slate-500">
                    {isVerifiedOfficialSource(doc) ? 'Verified source' : 'No verified source link'}
                  </span>
                  {isVerifiedOfficialSource(doc) && doc.source_url ? (
                    <a
                      href={doc.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 font-semibold text-blue-600 hover:text-blue-800"
                    >
                      <span>Open official source</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  ) : (
                    <span className="text-[11px] text-slate-400">No reference URL available</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Guide: How to add custom documents */}
      <div className="bg-slate-900 text-slate-200 p-6 rounded-2xl border border-slate-800 space-y-3">
        <div className="flex items-center gap-2 text-white font-bold text-sm">
          <FolderPlus className="w-4 h-4 text-emerald-400" />
          <span>How to Add and Re-index PDFs</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          Add official documents from their publishing organizations. Provenance remains unknown unless verified metadata is supplied; generated demos are never treated as official sources.
        </p>
        <ol className="text-xs text-slate-300 space-y-1.5 list-decimal pl-5 leading-relaxed">
          <li>Download the PDF directly from the organization that publishes it and record the exact source details.</li>
          <li>Place the PDF file inside the directory: <code className="text-emerald-300 bg-slate-800 px-1 py-0.5 rounded">backend/data/documents/</code></li>
          <li>Use the re-index button above or run <code className="text-emerald-300 bg-slate-800 px-1 py-0.5 rounded">python backend/scripts/ingest_documents.py --reindex</code>. Re-indexing replaces only FinGuide AI's named collection after backing up the project-local Chroma directory.</li>
          <li>Check the returned document and chunk totals. Unknown publishers, source URLs, and verification dates remain explicitly unknown.</li>
        </ol>
      </div>
    </div>
  );
}
