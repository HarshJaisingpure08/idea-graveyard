/**
 * Import — file upload for CSV/JSON idea imports.
 */
import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { importFile } from '../api';
import type { ImportResult } from '../types';

export default function Import() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  function handleDragOver(e: React.DragEvent) {
    e.preventDefault();
    setDragging(true);
  }

  function handleDragLeave() {
    setDragging(false);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  }

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) processFile(file);
  }

  function processFile(file: File) {
    const ext = file.name.toLowerCase();
    if (!ext.endsWith('.csv') && !ext.endsWith('.json')) {
      setError('Only CSV and JSON files are supported.');
      return;
    }
    setSelectedFile(file);
    setError(null);
    setResult(null);
  }

  async function handleUpload() {
    if (!selectedFile) return;
    setUploading(true);
    setError(null);
    try {
      const res = await importFile(selectedFile);
      setResult(res);
      setSelectedFile(null);
    } catch (e: any) {
      setError(e.message || 'Import failed.');
    } finally {
      setUploading(false);
    }
  }

  function handleReset() {
    setSelectedFile(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  }

  return (
    <div className="layout">
      <div className="editorial-header">
        <h1>Import Ideas</h1>
        <p className="editorial-subtitle">
          Upload a CSV or JSON file of ideas you've been sitting on.
        </p>
      </div>

      <hr className="divider" />

      {/* Upload zone */}
      {!result && (
        <>
          <div
            className={`upload-zone${dragging ? ' active' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <p className="upload-zone-text">
              {selectedFile ? selectedFile.name : 'Drop a file here, or click to browse'}
            </p>
            <p className="upload-zone-hint">CSV or JSON · max 5MB</p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.json"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              id="file-upload"
              aria-label="Upload ideas file"
            />
          </div>

          {/* CSV format hint */}
          <div style={{ marginTop: '24px' }}>
            <div className="section-title">CSV format</div>
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', fontFamily: 'monospace' }}>
              title, description, source, tags, captured_at
            </p>
          </div>

          {selectedFile && (
            <div style={{ marginTop: '24px', display: 'flex', gap: '12px' }}>
              <button
                className="btn btn-primary"
                onClick={handleUpload}
                disabled={uploading}
              >
                {uploading ? 'Importing...' : 'Import ideas'}
              </button>
              <button className="btn btn-secondary" onClick={handleReset}>
                Cancel
              </button>
            </div>
          )}
        </>
      )}

      {/* Error */}
      {error && (
        <div className="error-state" style={{ textAlign: 'left', marginTop: '24px' }}>
          <p>{error}</p>
          <button className="btn btn-secondary" onClick={handleReset} style={{ marginTop: '12px' }}>
            Choose another file
          </button>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="fade-in" style={{ marginTop: '24px' }}>
          <div style={{ marginBottom: '24px' }}>
            {result.imported > 0 && (
              <p style={{ color: 'var(--accent-forest)', fontWeight: 500, marginBottom: '4px' }}>
                {result.imported} idea{result.imported !== 1 ? 's' : ''} imported.
              </p>
            )}
            {result.skipped > 0 && (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                {result.skipped} duplicate{result.skipped !== 1 ? 's' : ''} skipped.
              </p>
            )}
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button className="btn btn-primary" onClick={() => navigate('/')}>
              View dashboard
            </button>
            <button className="btn btn-secondary" onClick={handleReset}>
              Import more
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
