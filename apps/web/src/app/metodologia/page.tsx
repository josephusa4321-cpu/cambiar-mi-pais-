import React from 'react';
import { Target, ShieldAlert, BarChart3, Database, FileSearch, Scale, Info } from 'lucide-react';
import * as motion from 'motion/react-client';
import DisclaimerSlapp from '@/components/ui/DisclaimerSlapp';

export default function MetodologiaPage() {
  const indicators = [
    { id: "A1", category: "Transparencia", title: "Contratación Directa sin Competencia", weight: 12, desc: "Contratos adjudicados bajo modalidad directa cuando la cuantía o el objeto sugieren un proceso competitivo (Art. 2 Ley 1150/2007)." },
    { id: "A2", category: "Competencia", title: "Oferente Único en Proceso Competitivo", weight: 10, desc: "Procesos que, a pesar de ser competitivos (Licitación, Selección Abreviada), solo reciben una oferta habilitada." },
    { id: "A3", category: "Velocidad", title: "Período de Publicación 'Sastre'", weight: 8, desc: "Tiempos entre la publicación del proceso y el cierre de recepción de ofertas inusualmente cortos (Art. 30 Ley 80/1993)." },
    { id: "B1", category: "Legalidad", title: "Proveedor Inhabilitado", weight: 20, desc: "Cruce con la base de datos de la Procuraduría que detecta contratistas con sanciones vigentes (Art. 8 Ley 80/1993)." },
    { id: "B3", category: "Concentración", title: "Concentración de Riesgo", weight: 7, desc: "Proveedores que concentran un porcentaje excesivo del presupuesto de contratación de una misma entidad en 12 meses." },
    { id: "C1", category: "Valores", title: "Adición > 30% del Valor Original", weight: 10, desc: "Contratos cuyo valor final supera significativamente el pactado inicialmente (Art. 40 Ley 80/1993)." },
    { id: "C2", category: "Fraccionamiento", title: "Fraccionamiento Sistemático", weight: 10, desc: "Múltiples contratos de cuantía menor adjudicados al mismo proveedor por el mismo objeto en periodos cortos." },
    { id: "C3", category: "Precios", title: "Precio Cercano al Presupuesto", weight: 5, desc: "Ofertas que coinciden en más de un 99.5% con el presupuesto oficial, sugiriendo fuga de información." },
    { id: "D1", category: "Opacidad", title: "Objeto Vago o Documentos Faltantes", weight: 6, desc: "Descripciones vagas ('servicios varios') o falta de publicación de documentos obligatorios en SECOP II." },
    { id: "D2", category: "Entidad", title: "Entidad con Historial de Abuso Directo", weight: 4, desc: "Entidades que realizan más del 80% de su contratación anual por la vía directa de forma sistemática." },
  ];

  return (
    <div className="container mx-auto px-4 py-24 space-y-16">
      <section className="space-y-6 max-w-4xl">
        <motion.div 
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-4 text-emerald-500"
        >
          <Scale size={40} />
          <h1 className="text-4xl md:text-6xl font-black tracking-tight">Scoring <span className="text-white">Determinista</span></h1>
        </motion.div>
        <p className="text-slate-400 text-xl leading-relaxed">
          Lupa no es una "caja negra" de Inteligencia Artificial. Nuestra metodología es pública, 
          determinista y auditable. Cada contrato recibe un score de 0 a 100 basado en indicadores verificables.
        </p>
      </section>

      {/* Scoring Flow Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div className="card-premium animate-glow-slow relative overflow-hidden p-8 space-y-4">
          <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center border border-blue-500/20 mb-4">
            <Database className="text-blue-500" size={24} />
          </div>
          <h3 className="text-xl font-bold">1. Auditoría ICD</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            Antes de puntuar el riesgo, verificamos la integridad del dato (ICD). 
            Si un contrato oculta información básica, se clasifica como **OPACO** (Score &lt; 40) y no puede ser auditado.
          </p>
        </div>

        <div className="card-premium relative overflow-hidden p-8 space-y-4">
          <div className="w-12 h-12 bg-amber-500/10 rounded-xl flex items-center justify-center border border-amber-500/20 mb-4">
            <Target className="text-amber-500" size={24} />
          </div>
          <h3 className="text-xl font-bold">2. Detección de Banderas</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            Aplicamos 10 detectores algorítmicos deterministas sobre los datos crudos del SECOP II. 
            Cada bandera tiene un peso específico según su impacto histórico en el riesgo.
          </p>
        </div>

        <div className="card-premium relative overflow-hidden p-8 space-y-4">
          <div className="w-12 h-12 bg-rose-500/10 rounded-xl flex items-center justify-center border border-rose-500/20 mb-4">
            <ShieldAlert className="text-rose-500" size={24} />
          </div>
          <h3 className="text-xl font-bold">3. Penalización Sistémica</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            Si un contrato activa más de 3 banderas de categorías diferentes, se aplica un **Bonus Sistémico** de +10 puntos.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <section className="p-8 bg-slate-900/30 border border-white/5 rounded-3xl space-y-4">
          <div className="flex items-center gap-3 text-emerald-500">
            <BarChart3 size={24} />
            <h3 className="text-xl font-bold">Bonus Sistémico (+10 Pts)</h3>
          </div>
          <p className="text-sm text-slate-400 leading-relaxed">
            La co-ocurrencia de múltiples señales de riesgo independientes es exponencialmente más sospechosa. 
            Lupa premia la detección de patrones complejos con un incremento en el score final, 
            topado siempre a un máximo de 100 puntos.
          </p>
        </section>

        <section className="p-8 bg-slate-900/30 border border-white/5 rounded-3xl space-y-4">
          <div className="flex items-center gap-3 text-blue-500">
            <ShieldAlert size={24} />
            <h3 className="text-xl font-bold">Atenuación ACTT (Convenios)</h3>
          </div>
          <p className="text-sm text-slate-400 leading-relaxed">
            Los convenios entre entidades públicas (ej. Municipio + Universidad Pública) no requieren competencia legal. 
            Lupa atenúa el score en un **50%** para estos casos, a menos que se detecten banderas graves de valores o fraccionamiento.
          </p>
        </section>
      </div>

      {/* Indicators List */}
      <div className="space-y-8">
        <div className="flex items-center gap-3 border-b border-white/5 pb-4">
          <Info className="text-slate-500" size={20} />
          <h2 className="text-2xl font-black tracking-tight uppercase">Indicadores Clave (Muestra)</h2>
        </div>
        
        <div className="grid grid-cols-1 gap-4">
          {indicators.map((ind, i) => (
            <motion.div 
              key={ind.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="flex items-center gap-6 p-6 bg-slate-900/30 border border-white/5 rounded-2xl group hover:bg-slate-900/50 transition-all shadow-inner"
            >
              <div className="w-16 h-16 shrink-0 flex items-center justify-center bg-slate-950 rounded-xl border border-white/10 text-xl font-black text-emerald-500 font-mono shadow-lg">
                {ind.id}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-2 py-0.5 bg-slate-800 rounded">{ind.category}</span>
                  <h4 className="text-lg font-bold">{ind.title}</h4>
                </div>
                <p className="text-slate-400 text-sm mt-1 max-w-2xl">{ind.desc}</p>
              </div>
              <div className="text-right hidden md:block">
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Peso</p>
                <p className="text-2xl font-black text-slate-300">+{ind.weight}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Citizen Translation Explain */}
      <section className="bg-gradient-to-br from-slate-900 to-black p-12 rounded-[2rem] border border-white/5 space-y-8 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 blur-[100px] -z-0" />
        <div className="relative z-10 space-y-4">
          <div className="flex items-center gap-3 text-secondary">
            <FileSearch size={32} />
            <h2 className="text-3xl font-black tracking-tight">Traducción Ciudadana</h2>
          </div>
          <p className="text-slate-400 text-lg max-w-3xl leading-relaxed">
            El lenguaje de la contratación pública está diseñado para ser aburrido e impenetrable. 
            Lupa implementa una capa de traducción semántica que explica los riesgos en lenguaje natural:
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 relative z-10">
          <div className="p-6 bg-slate-950 rounded-2xl border border-rose-500/20 border-dashed">
            <p className="text-[10px] font-black text-rose-500/50 uppercase tracking-widest mb-2">Dato Técnico</p>
            <p className="font-mono text-xs text-slate-500 italic">
              "Licitación pública con tiempo de publicación de 3.5 días hábiles, único oferente habilitado en fase de evaluación técnica."
            </p>
          </div>
          <div className="p-6 bg-emerald-500/5 rounded-2xl border border-emerald-500/20">
            <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest mb-2">Traducción Lupa</p>
            <p className="text-sm font-bold text-slate-300">
              "Este proceso se cerró tan rápido que es probable que solo el ganador supiera que existía. Se bloqueó la competencia artificialmente."
            </p>
          </div>
        </div>
      </section>

      <DisclaimerSlapp />
    </div>
  );
}
