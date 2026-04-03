import { supabase } from '@/lib/supabase';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import { 
  ShieldAlert, 
  ExternalLink, 
  Calendar, 
  DollarSign, 
  Building2, 
  Copy,
  Info,
  CheckCircle2,
  FileText
} from 'lucide-react';
import CopyComplaintButton from '@/components/CopyComplaintButton';
import CommunityComments from '@/components/features/CommunityComments';

interface PageProps {
  params: { id: string };
}

async function getContractDetail(id: string) {
  const { data, error } = await supabase
    .from('contratos_scored')
    .select(`
      id_contrato,
      score_total,
      nivel_riesgo,
      flags_detectadas,
      contratos_raw (*)
    `)
    .eq('id_contrato', id)
    .single();

  if (error || !data) return null;
  return data;
}

export default async function ContractDetailPage({ params }: PageProps) {
  const { id } = await params;
  const contract = await getContractDetail(id);

  if (!contract) {
    notFound();
  }

  // Supabase returns related records as an array [0]
  const raw = Array.isArray(contract.contratos_raw) ? contract.contratos_raw[0] : contract.contratos_raw;
  
  if (!raw) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-10 text-center">
        <div className="space-y-4">
           <h1 className="text-3xl font-bold">Datos incompletos</h1>
           <p className="text-slate-500">No se pudieron encontrar los datos base de este contrato.</p>
           <Link href="/top10" className="text-rose-500 font-bold">Volver al Top 10</Link>
        </div>
      </div>
    );
  }

  const score = contract.score_total;
  const colorClass = score >= 70 ? 'text-rose-500 border-rose-500/30 bg-rose-500/5' : 
                     score >= 40 ? 'text-amber-500 border-amber-500/30 bg-amber-500/5' : 
                     'text-emerald-500 border-emerald-500/30 bg-emerald-500/5';

  const secopUrl = `https://community.secop.gov.co/Public/Tendering/OpportunityDetail/Index?noticeUID=${raw.id_oportunidad || id}`;

  return (
    <main className="min-h-screen bg-slate-950 text-white pb-20">
      {/* Header / Breadcrumb */}
      <div className="border-b border-slate-900 bg-slate-900/20 sticky top-0 z-50 backdrop-blur-md">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/top10" className="text-slate-500 hover:text-white transition-colors text-sm font-bold flex items-center gap-2">
            ← Volver al Listado
          </Link>
          <div className="text-[10px] font-mono text-slate-600 uppercase tracking-widest">{id}</div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 pt-12 space-y-12">
        {/* Profile Card */}
        <section className="bg-slate-900/40 border border-slate-800/50 rounded-[2.5rem] overflow-hidden p-10 shadow-2xl">
          <div className="flex flex-col lg:flex-row gap-12 items-start">
            
            {/* Score Big Indicator */}
            <div className={`p-8 rounded-3xl border-2 flex flex-col items-center justify-center min-w-[220px] ${colorClass} animate-in fade-in zoom-in duration-500`}>
              <div className="text-7xl font-black mb-2">{score}</div>
              <div className="text-xs font-black uppercase tracking-[0.2em] mb-4">Risk Score</div>
              <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
                <div 
                  className={`h-full ${score >= 70 ? 'bg-rose-500 shadow-[0_0_12px_rgba(225,29,72,0.6)]' : score >= 40 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                  style={{ width: `${score}%` }}
                />
              </div>
              <div className="mt-4 text-center font-bold text-sm uppercase px-3 py-1 bg-black/20 rounded-lg">
                {contract.nivel_riesgo}
              </div>
            </div>

            {/* Basic Info */}
            <div className="flex-1 space-y-6">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-rose-500 font-bold text-xs uppercase tracking-widest">
                   <Building2 size={16} /> {raw.nombre_entidad}
                </div>
                <h1 className="text-3xl md:text-4xl font-bold leading-tight">
                  {raw.objeto_del_contrato}
                </h1>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 pt-4">
                <div className="space-y-1">
                  <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2 italic">
                     <DollarSign size={14} /> Valor Adjudicado
                  </div>
                  <div className="text-2xl font-black text-white">${Number(raw.valor_del_contrato).toLocaleString()} <span className="text-sm font-normal text-slate-500">COP</span></div>
                </div>
                <div className="space-y-1">
                  <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2 italic">
                     <Calendar size={14} /> Fecha de Firma
                  </div>
                  <div className="text-2xl font-black text-slate-300">{raw.fecha_de_firma}</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Flag Breakdown */}
        <section className="space-y-6">
           <div className="flex items-center gap-3">
             <ShieldAlert className="text-rose-500" size={24} />
             <h2 className="text-2xl font-bold">Análisis de Banderas</h2>
           </div>
           
           <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {contract.flags_detectadas?.map((flag: string) => (
                <div key={flag} className="p-6 bg-slate-900 border border-slate-800 rounded-2xl flex items-start gap-4">
                  <div className="p-2 bg-rose-500/10 rounded-lg text-rose-500 font-black text-lg">!</div>
                  <div className="space-y-1">
                    <h4 className="font-bold text-slate-200">Alerta de {flag}</h4>
                    <p className="text-sm text-slate-500">Hallazgo detectado automáticamente por patrones de anomalía en el SECOP II.</p>
                  </div>
                </div>
              ))}
              {(!contract.flags_detectadas || contract.flags_detectadas.length === 0) && (
                <div className="col-span-2 p-10 border-2 border-dashed border-slate-900 text-center rounded-3xl text-slate-500">
                   No se detectaron banderas de riesgo específicas.
                </div>
              )}
           </div>
        </section>

        {/* Actions Grid */}
        <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
           {/* Denuncia Box */}
           <div className="bg-rose-600/5 border border-rose-500/20 p-8 rounded-[2rem] space-y-6 relative overflow-hidden group">
              <div className="absolute -top-10 -right-10 w-40 h-40 bg-rose-500/5 blur-3xl group-hover:bg-rose-500/10 transition-all rounded-full" />
              <div className="space-y-4 relative z-10">
                <div className="flex items-center gap-3 text-rose-400">
                  <FileText size={24} />
                  <h3 className="text-xl font-bold">Borrador de Denuncia</h3>
                </div>
                <p className="text-sm text-slate-400">
                  Generamos un texto legalmente neutral basado en los hallazgos algorítmicos. Puedes copiarlo y pegarlo en los canales oficiales de la Contraloría o Personería.
                </p>
              </div>
              <CopyComplaintButton 
                contractId={id} 
                score={score} 
                entidad={raw.nombre_entidad} 
                valor={raw.valor_del_contrato} 
              />
           </div>

           {/* Source Link */}
           <div className="bg-slate-900/50 border border-slate-800 p-8 rounded-[2rem] space-y-6 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="flex items-center gap-3 text-slate-400">
                  <ExternalLink size={24} />
                  <h3 className="text-xl font-bold">Fuente Original</h3>
                </div>
                <p className="text-sm text-slate-500">
                  Verifica estos datos directamente en el SECOP II. Lupa extrae la información de manera fidedigna pero el portal oficial es la fuente primaria de verdad.
                </p>
              </div>
              <a 
                href={secopUrl} 
                target="_blank" 
                className="w-full py-4 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold text-center transition-all border border-slate-700 flex items-center justify-center gap-2"
              >
                Abrir en SECOP II <ExternalLink size={16} />
              </a>
           </div>
        </section>

        {/* Community Feedback Section */}
        <section className="animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300">
           <CommunityComments contractId={id} />
        </section>
      </div>
    </main>
  );
}
