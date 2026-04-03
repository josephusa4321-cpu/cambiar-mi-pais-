'use client';

import React from 'react';
import { Download } from 'lucide-react';

interface CSVDownloadButtonProps {
  data: any[];
  filename: string;
}

export default function CSVDownloadButton({ data, filename }: CSVDownloadButtonProps) {
  const downloadCSV = () => {
    if (!data || data.length === 0) return;

    // Detect headers from first object
    const sample = data[0];
    const rawHeaders = Object.keys(sample).filter(h => h !== 'contratos_raw' && h !== 'campos_faltantes');
    
    // Add sub-object headers if they exist (standard for Lupa API)
    const subHeaders = sample.contratos_raw ? Object.keys(sample.contratos_raw) : [];
    const headers = [...rawHeaders, ...subHeaders];

    const rows = data.map(item => {
      const mainValues = rawHeaders.map(h => {
        const val = item[h];
        return typeof val === 'string' ? `"${val.replace(/"/g, '""')}"` : val;
      });
      
      const subValues = item.contratos_raw ? subHeaders.map(sh => {
        const val = item.contratos_raw[sh];
        return typeof val === 'string' ? `"${val.replace(/"/g, '""')}"` : val;
      }) : [];

      return [...mainValues, ...subValues].join(",");
    });

    const csvContent = "\xEF\xBB\xBF" + [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `${filename}_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <button 
      onClick={downloadCSV}
      className="flex items-center gap-2 px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white rounded-xl border border-slate-800 transition-all font-bold text-sm shrink-0 active:scale-95"
    >
      <Download size={18} className="text-secondary" /> 
      <span>Descargar CSV</span>
    </button>
  );
}
