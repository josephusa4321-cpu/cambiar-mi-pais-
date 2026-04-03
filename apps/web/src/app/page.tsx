import Link from 'next/link';
import { supabase } from '@/lib/supabase';

// Revalidate every hour (as per PRD ISR rule)
export const revalidate = 3600;

async function getStats() {
  try {
    const { count: totalContratos } = await supabase.from('contratos_raw').select('*', { count: 'exact', head: true });
    
    // Sum of value for scored contracts
    const { data: sumData } = await supabase.from('contratos_raw').select('valor_del_contrato');
    const totalValue = sumData?.reduce((acc, curr) => acc + (Number(curr.valor_del_contrato) || 0), 0) || 0;

    const { count: pendingAlerts } = await supabase.from('timeline_impunidad')
      .select('*', { count: 'exact', head: true })
      .eq('estado_respuesta', 'PENDIENTE');

    return {
      totalContratos: totalContratos || 0,
      totalValue: Math.round(totalValue / 1_000_000), // In Millions
      pendingAlerts: pendingAlerts || 0
    };
  } catch (e) {
    console.error('Error fetching stats:', e);
    return { totalContratos: 0, totalValue: 0, pendingAlerts: 0 };
  }
}

export default async function Home() {
  const stats = await getStats();

  return (
    <main className="min-h-screen bg-slate-950 text-white selection:bg-rose-500/30">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6 overflow-hidden">
        <div className="absolute inset-x-0 top-0 h-[500px] bg-[radial-gradient(circle_at_50%_-20%,#4c0519,transparent_50%)] opacity-50" />
        <div className="max-w-5xl mx-auto relative z-10 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-medium mb-8">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
            </span>
            Vigilancia Activa en Medellín
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 bg-gradient-to-b from-white to-slate-400 bg-clip-text text-transparent">
            Lupa vigila los contratos públicos mientras tú duermes.
          </h1>
          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Auditoría algorítmica en tiempo real sobre el SECOP II Medellín. Detectamos riesgos de contratación y alertamos a la ciudadanía antes de que el dinero desaparezca.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link 
              href="/top10"
              className="px-8 py-4 bg-rose-600 hover:bg-rose-700 text-white font-semibold rounded-xl transition-all hover:scale-105 shadow-[0_0_20px_rgba(225,29,72,0.4)]"
            >
              Ver contratos sospechosos →
            </Link>
            <a 
              href="https://t.me/LupaMedellin" 
              target="_blank"
              className="px-8 py-4 bg-slate-800 hover:bg-slate-700 text-white font-semibold rounded-xl border border-slate-700 transition-all font-mono"
            >
              @LupaMedellin
            </a>
          </div>
        </div>
      </section>

      {/* Counters Section */}
      <section className="py-12 border-y border-slate-800 bg-slate-900/50 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center md:text-left border-b md:border-b-0 md:border-r border-slate-800 pb-8 md:pb-0 md:pr-8">
            <div className="text-4xl font-black text-white mb-1 font-mono">{stats.totalContratos.toLocaleString()}</div>
            <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">Contratos Analizados</div>
          </div>
          <div className="text-center md:text-left border-b md:border-b-0 md:border-r border-slate-800 pb-8 md:pb-0 md:pr-8">
            <div className="text-4xl font-black text-rose-500 mb-1 font-mono">${stats.totalValue.toLocaleString()}M</div>
            <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">Bajo Monitoreo (COP)</div>
          </div>
          <div className="text-center md:text-left">
            <div className="text-4xl font-black text-amber-500 mb-1 font-mono">{stats.pendingAlerts}</div>
            <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">Alertas sin respuesta</div>
          </div>
        </div>
      </section>

      {/* 3 Steps Section */}
      <section className="py-32 px-6">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-20 italic bg-gradient-to-r from-rose-500 to-white bg-clip-text text-transparent">¿Cómo funciona Lupa?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { 
                step: '01', 
                title: 'Ingesta Continua', 
                desc: 'Cada noche a las 3:00 AM, nuestros robots extraen todos los contratos nuevos del SECOP II para Medellín.' 
              },
              { 
                step: '02', 
                title: 'Scoring Algorítmico', 
                desc: 'Aplicamos un sistema de 10 banderas de riesgo (ICD, velocidad, competencia) basado en reglas de transparencia.' 
              },
              { 
                step: '03', 
                title: 'Alerta Ciudadana', 
                desc: 'Los contratos con hallazgos críticos se publican en Telegram y en esta web para veeduría pública.' 
              }
            ].map((item, i) => (
              <div key={i} className="group relative p-10 rounded-3xl bg-slate-900/50 border border-slate-800/50 transition-all hover:bg-slate-900 hover:border-rose-500/30">
                <div className="text-7xl font-black text-slate-950 group-hover:text-rose-500/5 absolute top-4 right-4 transition-colors">
                  {item.step}
                </div>
                <h3 className="text-2xl font-bold mb-4 relative z-10">{item.title}</h3>
                <p className="text-slate-400 leading-relaxed relative z-10 text-lg">
                  {item.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA & Footer Disclaimer */}
      <footer className="py-20 px-6 border-t border-slate-900 bg-black/40">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-slate-900/40 p-10 rounded-[2.5rem] border border-slate-800 mb-16 shadow-2xl">
            <h3 className="text-xl font-bold mb-6 text-slate-200 uppercase tracking-widest">Aviso Legal y Transparencia</h3>
            <p className="text-base text-slate-500 leading-relaxed italic max-w-2xl mx-auto">
              "Este análisis es algorítmico y basado en datos públicos del SECOP II (Sistema Electrónico de Contratación Pública). No representa una acusación legal, no prejuzga responsabilidad, y no tiene sesgo político. Los datos fuente están disponibles en datos.gov.co."
            </p>
          </div>
          <p className="text-slate-600 text-sm font-mono">
            © {new Date().getFullYear()} LUPA — Vibe Coding MVP v1.0 | Medellín
          </p>
        </div>
      </footer>
    </main>
  );
}
