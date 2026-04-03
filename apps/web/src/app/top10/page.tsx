'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { supabase } from '@/lib/supabase';
import { 
  ShieldAlert, 
  AlertTriangle, 
  ExternalLink, 
  Calendar, 
  DollarSign, 
  Building2, 
  Download,
  ArrowRight
} from 'lucide-react';
import ScoreBar from '@/components/ui/ScoreBar';

interface ContractAlert {
  id_contrato: string;
  score_total: number;
  nivel_riesgo: string;
  nombre_entidad: string;
  proveedor_adjudicado: string;
  valor_del_contrato: number;
  fecha_de_firma: string;
  objeto_del_contrato: string;
}

export default function Top10Page() {
  const [alerts, setAlerts] = useState<ContractAlert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const { data, error } = await supabase
          .from('contratos_scored')
          .select(`
            id_contrato,
            score_total,
            nivel_riesgo,
            contratos_raw (
              nombre_entidad,
              proveedor_adjudicado,
              valor_del_contrato,
              fecha_de_firma,
              objeto_del_contrato
            )
          `)
          .order('score_total', { ascending: false })
          .limit(10);

        if (error) throw error;

        const formattedData = data.map((item: any) => ({
          id_contrato: item.id_contrato,
          score_total: item.score_total,
          nivel_riesgo: item.nivel_riesgo,
          ...item.contratos_raw
        }));

        setAlerts(formattedData);
      } catch (e) {
        console.error('Error fetching alerts:', e);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  const downloadCSV = () => {
    if (alerts.length === 0) return;

    const headers = ["ID Contrato", "Entidad", "Proveedor", "Valor (COP)", "Score", "Riesgo", "Fecha"];
    const rows = alerts.map(a => [
      a.id_contrato,
      `"${a.nombre_entidad}"`,
      `"${a.proveedor_adjudicado}"`,
      a.valor_del_contrato,
      a.score_total,
      a.nivel_riesgo,
      a.fecha_de_firma
    ]);

    const csvContent = "\xEF\xBB\xBF" + [headers, ...rows].map(e => e.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `lupa_top10_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-rose-500"></div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white pb-20">
      <div className="max-w-6xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-500 text-xs font-bold uppercase tracking-widest leading-none">
              <ShieldAlert size={14} /> Riesgo Crítico
            </div>
            <h1 className="text-4xl md:text-5xl font-black tracking-tight">Top 10 Semanal</h1>
            <p className="text-slate-400 text-lg max-w-xl">
              Análisis algorítmico de los contratos con mayor puntuación de riesgo detectados en Medellín esta semana.
            </p>
          </div>
          
          <button 
            onClick={downloadCSV}
            className="flex items-center gap-2 px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white rounded-xl border border-slate-800 transition-all font-bold text-sm"
          >
            <Download size={18} /> Descargar CSV
          </button>
        </div>

        {/* Disclaimer Area */}
        <div className="bg-amber-500/5 border border-amber-500/20 p-6 rounded-2xl mb-12 flex gap-4">
          <AlertTriangle className="text-amber-500 shrink-0" size={24} />
          <p className="text-sm text-amber-200/70 leading-relaxed font-medium">
             ⚠️ Este análisis es algorítmico y basado en datos públicos del SECOP II. No representa una acusación legal ni prejuzga responsabilidad institucional. La metodología es 100% transparente y auditable.
          </p>
        </div>

        {/* Alerts Grid */}
        <div className="grid grid-cols-1 gap-6">
          {alerts.map((alert, i) => (
            <div 
              key={alert.id_contrato}
              className="group relative bg-slate-900/40 border border-slate-800/50 rounded-3xl overflow-hidden hover:bg-slate-900 hover:border-rose-500/30 transition-all p-8"
            >
              <div className="flex flex-col md:flex-row gap-8">
                {/* Score Column */}
                <div className="flex flex-col items-center justify-center bg-slate-950 p-6 rounded-2xl border border-white/5 min-w-[140px]">
                  <div className={`text-4xl font-black mb-1 ${alert.score_total >= 70 ? 'text-rose-500' : 'text-amber-500'}`}>
                    {alert.score_total}
                  </div>
                  <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 text-center">Score de Riesgo</div>
                  <div className="mt-4 w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${alert.score_total >= 70 ? 'bg-rose-500 shadow-[0_0_8px_rgba(225,29,72,0.5)]' : 'bg-amber-500'}`} 
                      style={{ width: `${alert.score_total}%` }}
                    />
                  </div>
                </div>

                {/* Content Column */}
                <div className="flex-1 space-y-4">
                  <div className="flex items-center gap-2 text-slate-500">
                    <Building2 size={16} />
                    <span className="text-xs font-bold uppercase tracking-wider">{alert.nombre_entidad}</span>
                  </div>
                  <h3 className="text-2xl font-bold text-white group-hover:text-rose-400 transition-colors">
                    {alert.objeto_del_contrato || 'Objeto no disponible'}
                  </h3>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 pt-4">
                    <div className="space-y-1">
                      <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Proveedor</div>
                      <div className="text-sm font-bold text-slate-200 truncate">{alert.proveedor_adjudicado}</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Valor Contrato</div>
                      <div className="text-sm font-bold text-white">${(alert.valor_del_contrato).toLocaleString()} COP</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Fecha Firma</div>
                      <div className="text-sm font-bold text-slate-400 flex items-center gap-2">
                        <Calendar size={14} /> {alert.fecha_de_firma}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Action Column */}
                <div className="flex flex-col justify-center">
                  <Link 
                    href={`/contrato/${alert.id_contrato}`}
                    className="px-6 py-4 bg-white/5 hover:bg-rose-600 text-white rounded-2xl border border-white/10 transition-all font-bold flex items-center gap-3 justify-center group/btn"
                  >
                    Ver Detalle 
                    <ArrowRight size={18} className="transition-transform group-hover/btn:translate-x-1" />
                  </Link>
                </div>
              </div>
            </div>
          ))}
          
          {alerts.length === 0 && (
            <div className="py-20 text-center border-2 border-dashed border-slate-800 rounded-3xl">
              <p className="text-slate-500 font-medium text-lg">No se han detectado contratos de riesgo crítico en las últimas 24h.</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
