import React, { useCallback } from 'react';
import { motion } from 'framer-motion';
import { Upload, FileText, X } from 'lucide-react';
import { clsx } from 'clsx';

interface FileUploadProps {
    files: FileList | null;
    setFiles: (files: FileList | null) => void;
    onUpload: () => void;
    loading: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({ files, setFiles, onUpload, loading }) => {
    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            setFiles(e.dataTransfer.files);
        }
    }, [setFiles]);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-2xl mx-auto"
        >
            <div
                className={clsx(
                    "relative group cursor-pointer overflow-hidden rounded-3xl border-2 border-dashed transition-all duration-300",
                    files ? "border-indigo-500 bg-indigo-50/50" : "border-slate-300 hover:border-indigo-400 hover:bg-slate-50"
                )}
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    multiple
                    accept=".pdf"
                    onChange={(e) => setFiles(e.target.files)}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                />

                <div className="p-12 flex flex-col items-center justify-center text-center">
                    <div className={clsx(
                        "w-20 h-20 rounded-2xl flex items-center justify-center mb-6 transition-all duration-300 shadow-xl",
                        files ? "bg-indigo-600 rotate-0" : "bg-white rotate-12 group-hover:rotate-0 group-hover:scale-110"
                    )}>
                        {files ? (
                            <FileText className="w-10 h-10 text-white" />
                        ) : (
                            <Upload className="w-10 h-10 text-indigo-600" />
                        )}
                    </div>

                    <h3 className="text-2xl font-bold text-slate-800 mb-2">
                        {files ? `${files.length} Files Selected` : "Drop invoices here"}
                    </h3>
                    <p className="text-slate-500 max-w-sm mx-auto mb-8">
                        {files ? "Ready to process. Click below to start." : "Support for PDF files. Drag and drop or click to browse."}
                    </p>

                    <button
                        onClick={(e) => {
                            e.stopPropagation(); // Prevent triggering input
                            if (files) onUpload();
                            else document.querySelector('input[type="file"]')?.click();
                        }}
                        disabled={loading}
                        className={clsx(
                            "relative z-20 px-8 py-3 rounded-xl font-semibold shadow-lg transition-all duration-300 transform active:scale-95",
                            files
                                ? "bg-indigo-600 text-white hover:bg-indigo-700 hover:shadow-indigo-200"
                                : "bg-white text-indigo-600 hover:bg-indigo-50"
                        )}
                    >
                        {loading ? (
                            <span className="flex items-center space-x-2">
                                <svg className="animate-spin h-5 w-5 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                <span>Processing...</span>
                            </span>
                        ) : (
                            files ? "Start Extraction" : "Browse Files"
                        )}
                    </button>
                </div>
            </div>
        </motion.div>
    );
};
