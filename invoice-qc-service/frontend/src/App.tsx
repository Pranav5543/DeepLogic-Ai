import React, { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Layout } from './components/Layout';
import { FileUpload } from './components/FileUpload';
import { StatsGrid } from './components/StatsGrid';
import { ResultCard } from './components/ResultCard';
import { Filter } from 'lucide-react';
import { clsx } from 'clsx';

// Types
interface ValidationError {
  field: string;
  message: string;
}

interface ValidationResult {
  invoice_id: string;
  is_valid: boolean;
  errors: ValidationError[];
}

interface Summary {
  total_invoices: number;
  valid_invoices: number;
  invalid_invoices: number;
  error_counts: Record<string, number>;
}

interface ApiResponse {
  summary: Summary;
  results: ValidationResult[];
}

function App() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<ApiResponse | null>(null);
  const [showInvalidOnly, setShowInvalidOnly] = useState(false);

  const handleUpload = async () => {
    if (!files || files.length === 0) return;
    setLoading(true);
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      const res = await axios.post('http://localhost:8000/extract-and-validate-pdfs', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setData(res.data);
    } catch (err) {
      console.error(err);
      alert('Error uploading files');
    } finally {
      setLoading(false);
    }
  };

  const filteredResults = showInvalidOnly
    ? data?.results.filter(r => !r.is_valid)
    : data?.results;

  return (
    <Layout>
      <AnimatePresence mode="wait">
        {!data ? (
          <motion.div
            key="upload"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="py-20"
          >
            <div className="text-center mb-12">
              <h2 className="text-4xl font-extrabold text-slate-900 mb-4 tracking-tight">
                Automated Invoice Validation
              </h2>
              <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                Upload your invoice PDFs to instantly extract data, validate calculations, and detect duplicates with our intelligent engine.
              </p>
            </div>
            <FileUpload
              files={files}
              setFiles={setFiles}
              onUpload={handleUpload}
              loading={loading}
            />
          </motion.div>
        ) : (
          <motion.div
            key="results"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-8"
          >
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-slate-900">Validation Report</h2>
              <button
                onClick={() => setData(null)}
                className="text-sm font-medium text-indigo-600 hover:text-indigo-700 hover:underline"
              >
                Process New Batch
              </button>
            </div>

            <StatsGrid summary={data.summary} />

            <div className="bg-white rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
              <div className="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white/50 backdrop-blur-sm sticky top-0 z-10">
                <div className="flex items-center space-x-2">
                  <span className="flex h-2 w-2 rounded-full bg-indigo-500"></span>
                  <h3 className="font-semibold text-slate-800">Detailed Results</h3>
                  <span className="px-2 py-0.5 rounded-full bg-slate-100 text-xs font-medium text-slate-600">
                    {filteredResults?.length}
                  </span>
                </div>

                <button
                  onClick={() => setShowInvalidOnly(!showInvalidOnly)}
                  className={clsx(
                    "flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                    showInvalidOnly
                      ? "bg-red-50 text-red-700 ring-1 ring-red-200"
                      : "bg-slate-50 text-slate-600 hover:bg-slate-100 ring-1 ring-slate-200"
                  )}
                >
                  <Filter className="w-4 h-4" />
                  <span>{showInvalidOnly ? "Showing Issues Only" : "Filter by Issues"}</span>
                </button>
              </div>

              <div className="p-6 space-y-4 bg-slate-50/50 min-h-[400px]">
                {filteredResults?.length === 0 ? (
                  <div className="text-center py-20">
                    <p className="text-slate-500">No invoices match your filter.</p>
                  </div>
                ) : (
                  filteredResults?.map((res, idx) => (
                    <ResultCard key={res.invoice_id} result={res} index={idx} />
                  ))
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Layout>
  );
}

export default App;
