import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { clsx } from 'clsx';

interface ValidationError {
    field: string;
    message: string;
}

interface ValidationResult {
    invoice_id: string;
    is_valid: boolean;
    errors: ValidationError[];
}

interface ResultCardProps {
    result: ValidationResult;
    index: number;
}

export const ResultCard: React.FC<ResultCardProps> = ({ result, index }) => {
    const [expanded, setExpanded] = useState(!result.is_valid);

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden hover:shadow-md transition-shadow"
        >
            <div
                className="p-4 flex items-center justify-between cursor-pointer bg-white hover:bg-slate-50 transition-colors"
                onClick={() => setExpanded(!expanded)}
            >
                <div className="flex items-center space-x-4">
                    <div className={clsx(
                        "w-10 h-10 rounded-full flex items-center justify-center",
                        result.is_valid ? "bg-green-100 text-green-600" : "bg-red-100 text-red-600"
                    )}>
                        {result.is_valid ? <CheckCircle className="w-6 h-6" /> : <AlertCircle className="w-6 h-6" />}
                    </div>
                    <div>
                        <h3 className="font-semibold text-slate-900">{result.invoice_id || "Unknown Invoice"}</h3>
                        <p className={clsx("text-sm font-medium", result.is_valid ? "text-green-600" : "text-red-600")}>
                            {result.is_valid ? "Passed Validation" : `${result.errors.length} Issues Found`}
                        </p>
                    </div>
                </div>
                <button className="text-slate-400 hover:text-slate-600">
                    {expanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </button>
            </div>

            <AnimatePresence>
                {expanded && !result.is_valid && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="border-t border-slate-100 bg-red-50/30"
                    >
                        <div className="p-4 pl-16">
                            <h4 className="text-xs font-semibold text-red-800 uppercase tracking-wider mb-3">Validation Errors</h4>
                            <ul className="space-y-2">
                                {result.errors.map((err, idx) => (
                                    <li key={idx} className="flex items-start text-sm text-red-700 bg-white/50 p-2 rounded-lg border border-red-100">
                                        <span className="w-1.5 h-1.5 rounded-full bg-red-500 mt-1.5 mr-2 flex-shrink-0" />
                                        <span>
                                            <span className="font-semibold text-red-900">{err.field}:</span> {err.message}
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};
