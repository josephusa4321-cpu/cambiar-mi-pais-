import React from 'react';
import { EyeOff, AlertTriangle, FileWarning, Search } from 'lucide-react';
import * as motion from 'motion/react-client';
import DisclaimerSlapp from '@/components/ui/DisclaimerSlapp';
import CSVDownloadButton from '@/components/ui/CSVDownloadButton';

async function getOpacos() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    const res = await fetch(`${apiUrl}/api/opacos`, { next: { revalidate: 3600 } });
    if (!res.ok) return [];
    return res.json();
  } catch (error) {
    console.error("Error fetching opacos:", error);
    return [];
  }
}

export default async function OpacosPage() {
  const opacos = await getOpacos();

  return (
    <div className="container mx-auto px-4 py-24 space-y-12">
      <div className="space-y-4 max-w-3xl">
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex flex-col md:flex-row md:items-end justify-between gap-6"
        >
          <div className="space-y-4">
            <div className="flex items-center gap-3 text-amber-500">
              <EyeOff size={32} />
              <h1 className="text-4xl md:text-5xl font-black tracking-tight">Contratos <span className="text-white">Opacos</span></h1>
            </div>
            <p className="text-slate-400 text-lg leading-relaxed max-w-3xl">
              Estos contratos tienen un **Índice de Calidad del Dato (ICD) inferior a 40/100**. 
              La falta de información crítica impide un scoring de riesgo preciso.
            </p>
          </div>

          <CSVDownloadButton data={opacos} filename="lupa_opacos" />
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8 space-y-6">
          {opacos.length > 0 ? (
            opacos.map((item: any, idx: number) => (
              <motion.div 
                key={item.id_contrato}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="card-premium p-6 border-l-4 border-l-amber-500/50 hover:border-l-amber-500 transition-all group"
              >
                <div className="flex flex-col md:flex-row justify-between gap-4">
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold px-2 py-0.5 bg-slate-800 text-slate-400 rounded-full font-mono uppercase">
                        {item.id_contrato}
                      </span>
                      <span className="text-xs font-bold text-amber-500">ICD: {item.icd_score}/100</span>
                    </div>
                    <h3 className="text-lg font-bold group-hover:text-primary transition-colors">
                      {item.contratos_raw?.nombre_entidad || "Entidad Desconocida"}
                    </h3>
                    <p className="text-sm text-slate-400">
                      Valor: <span className="text-white font-mono font-bold">${item.contratos_raw?.valor_del_contrato?.toLocaleString() || "0"} COP</span>
                    </p>
                  </div>
                  
                  <div className="md:w-64 space-y-2">
                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-1">
                      <AlertTriangle size={12} /> Datos Faltantes
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {item.campos_faltantes?.map((campo: string) => (
                        <span key={campo} className="px-2 py-1 bg-rose-500/10 border border-rose-500/20 text-[10px] text-rose-400 rounded font-medium">
                          {campo.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))
          ) : (
            <div className="flex flex-col items-center justify-center py-24 text-slate-600 space-y-4">
              <Search size={48} className="opacity-20" />
              <p className="font-bold text-xl uppercase tracking-widest opacity-50">No hay contratos opacos activos</p>
              <p className="text-sm">Esto es inusual. El sistema podría estar en mantenimiento.</p>
            </div>
          )}
        </div>

        <div className="lg:col-span-4 space-y-6">
          <div className="p-6 bg-slate-900/50 border border-white/5 rounded-2xl sticky top-24 space-y-6">
            <h4 className="text-sm font-black uppercase tracking-widest text-slate-500 border-b border-white/5 pb-2">¿Por qué es esto riesgoso?</h4>
            <div className="space-y-4">
              <div className="flex gap-4">
                <FileWarning className="text-amber-500 shrink-0" size={20} />
                <div>
                  <p className="text-sm font-bold">Obscurantismo Deliberado</p>
                  <p className="text-xs text-slate-400 leading-relaxed">Cuando una entidad oculta el número de oferentes o el precio base, está bloqueando la auditoría social de forma proactiva.</p>
                </div>
              </div>
              <div className="flex gap-4">
                <FileWarning className="text-amber-500 shrink-0" size={20} />
                <div>
                  <p className="text-sm font-bold">Inauditable</p>
                  <p className="text-xs text-slate-400 leading-relaxed">Sin datos sobre la modalidad o el objeto social, es imposible aplicar los 14 indicadores de riesgo de LUPA.</p>
                </div>
              </div>
            </div>
            
            <div className="pt-6 border-t border-white/5">
              <p className="text-[10px] text-slate-500 italic">
                * El ICD es calculado algorítmicamente verificando la integridad de 12 campos obligatorios del SECOP II.
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <DisclaimerSlapp />
    </div>
  );
}
