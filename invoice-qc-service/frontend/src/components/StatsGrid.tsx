import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, AlertCircle, FileText } from 'lucide-react';

interface Summary {
    total_invoices: number;
    valid_invoices: number;
    invalid_invoices: number;
}

interface StatsGridProps {
    summary: Summary;
}

export const StatsGrid: React.FC<StatsGridProps> = ({ summary }) => {
    const cards = [
        {
            label: "Total Processed",
            value: summary.total_invoices,
            icon: FileText,
            color: "text-blue-600",
            bg: "bg-blue-50",
            border: "border-blue-100"
        },
        {
            label: "Valid Invoices",
            value: summary.valid_invoices,
            icon: CheckCircle,
            color: "text-green-600",
            bg: "bg-green-50",
            border: "border-green-100"
        },
        {
            label: "Needs Review",
            value: summary.invalid_invoices,
            icon: AlertCircle,
            color: "text-red-600",
            bg: "bg-red-50",
            border: "border-red-100"
        }
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
            {cards.map((card, idx) => (
                <motion.div
                    key={card.label}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className={`p-6 rounded-2xl bg-white border ${card.border} shadow-sm hover:shadow-md transition-shadow`}
                >
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-sm font-medium text-slate-500 mb-1">{card.label}</p>
                            <h3 className="text-3xl font-bold text-slate-800">{card.value}</h3>
                        </div>
                        <div className={`p-3 rounded-xl ${card.bg}`}>
                            <card.icon className={`w-6 h-6 ${card.color}`} />
                        </div>
                    </div>
                </motion.div>
            ))}
        </div>
    );
};
