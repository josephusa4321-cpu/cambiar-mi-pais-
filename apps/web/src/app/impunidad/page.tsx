import { Clock, ShieldCheck, MailWarning, Gavel, Calendar, History } from 'lucide-react';
import * as motion from 'motion/react-client';
import DisclaimerSlapp from '@/components/ui/DisclaimerSlapp';
import CSVDownloadButton from '@/components/ui/CSVDownloadButton';

async function getImpunidad() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    const res = await fetch(`${apiUrl}/api/impunidad`, { next: { revalidate: 3600 } });
    if (!res.ok) return [];
    return res.json();
  } catch (error) {
    console.error("Error fetching impunidad:", error);
    return [];
  }
}

export default async function ImpunidadPage() {
  const alerts = await getImpunidad();

  const getInactivityColor = (days: number) => {
    if (days >= 30) return "text-rose-500 bg-rose-500/10 border-rose-500/20";
    if (days >= 15) return "text-orange-500 bg-orange-500/10 border-orange-500/20";
    return "text-emerald-500 bg-emerald-500/10 border-emerald-500/20";
  };

  return (
    <div className="container mx-auto px-4 py-24 space-y-12 min-h-screen">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-white/5">
        <div className="space-y-4 max-w-3xl">
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-3 text-primary"
          >
            <History size={32} />
            <h1 className="text-4xl md:text-5xl font-black tracking-tight uppercase">Cronómetro de <span className="text-white">Impunidad</span></h1>
          </motion.div>
          <p className="text-slate-400 text-lg leading-relaxed">
            Lupa vigila el **silencio institucional**. Contamos los días desde una alerta SOS hasta una respuesta efectiva de los entes de control.
          </p>
        </div>
        <CSVDownloadButton data={alerts} filename="lupa_impunidad" />
      </div>

      <div className="space-y-4">
        {alerts.length > 0 ? (
          alerts.map((item: any, idx: number) => (
            <motion.div 
              key={item.id_alerta}
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="card-premium p-8 flex flex-col md:flex-row gap-8 items-center bg-slate-900/30 overflow-hidden relative"
            >
              <div className="md:w-32 flex flex-col items-center justify-center shrink-0 border-r border-white/5 py-2">
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Inactividad</p>
                <div className={`text-3xl font-black p-4 rounded-xl border ${getInactivityColor(item.dias_inactividad)}`}>
                  {item.dias_inactividad}d
                </div>
              </div>

              <div className="flex-1 space-y-4 w-full">
                <div className="flex flex-wrap justify-between items-start gap-4">
                  <div className="space-y-1">
                    <p className="text-xs font-mono text-slate-500 uppercase tracking-tight">{item.id_contrato}</p>
                    <h3 className="text-xl font-black text-white leading-tight">
                      {item.contratos_raw?.nombre_entidad || "Entidad en proceso"}
                    </h3>
                    <p className="text-sm text-slate-400">
                      Proveedor: <span className="text-slate-200">{item.contratos_raw?.proveedor_adjudicado || "Pendiente"}</span>
                    </p>
                  </div>
                  <div className={`px-4 py-2 rounded-lg text-xs font-black tracking-widest border border-white/5 
                                ${item.estado_respuesta === 'PENDIENTE' ? 'bg-amber-500/10 text-amber-500' : 
                                  item.estado_respuesta === 'RADICADO' ? 'bg-blue-500/10 text-blue-500' : 
                                  item.estado_respuesta === 'EN_INDAGACION' ? 'bg-purple-500/10 text-purple-500' :
                                  'bg-emerald-500/10 text-emerald-500'}`}>
                    {item.estado_respuesta}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 border-t border-white/5">
                  <div className="flex items-center gap-3">
                    <Calendar size={18} className="text-slate-500" />
                    <div>
                      <p className="text-[10px] text-slate-500 font-bold uppercase">Alerta LUPA</p>
                      <p className="text-xs font-bold">{new Date(item.fecha_alerta).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <MailWarning size={18} className="text-slate-500" />
                    <div>
                      <p className="text-[10px] text-slate-500 font-bold uppercase">Notificación Radicada</p>
                      <p className="text-xs font-bold">
                        {item.fecha_notificacion ? new Date(item.fecha_notificacion).toLocaleDateString() : "PENDIENTE"}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <ShieldCheck size={18} className="text-slate-500" />
                    <div>
                      <p className="text-[10px] text-slate-500 font-bold uppercase">Respuesta Efectiva</p>
                      <p className="text-xs font-bold text-emerald-400">
                        {item.fecha_respuesta ? new Date(item.fecha_respuesta).toLocaleDateString() : "SILENCIO"}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Progress visual background element */}
              <div 
                className="absolute left-0 bottom-0 h-1 bg-gradient-to-r from-emerald-500 via-amber-500 to-rose-500 opacity-20"
                style={{ width: `${Math.min(item.dias_inactividad * 3, 100)}%` }}
              />
            </motion.div>
          ))
        ) : (
          <div className="flex flex-col items-center justify-center py-24 text-slate-600 space-y-4">
            <ShieldCheck size={64} className="opacity-20 text-emerald-500" />
            <p className="font-bold text-xl uppercase tracking-widest opacity-50">No hay deudas de respuesta activas</p>
            <p className="text-sm">Esto significa que todos los riesgos SOS han sido atendidos por las autoridades (o aún no hay alertas Nivel 2).</p>
          </div>
        )}
      </div>
      
      <div className="bg-slate-900/50 p-8 rounded-3xl border border-white/5 space-y-6 max-w-2xl mx-auto text-center mt-12">
        <Gavel className="text-primary mx-auto" size={40} />
        <h3 className="text-2xl font-black">¿Un contrato SOS no se mueve?</h3>
        <p className="text-slate-400 text-sm">
          Lupa escala automáticamente a medios de comunicación y concejales cuando los días de inactividad superan los 45 días naturales. 
          Auditar es solo la mitad del camino.
        </p>
      </div>

      <DisclaimerSlapp />
    </div>
  );
}
