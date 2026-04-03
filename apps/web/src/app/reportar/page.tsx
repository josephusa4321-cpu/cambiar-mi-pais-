'use client';

import React, { useState } from 'react';
import { Send, ShieldAlert, CheckCircle2, Copy, AlertCircle, FileText, Lock } from 'lucide-react';
import * as motion from 'motion/react-client';
import DisclaimerSlapp from '@/components/ui/DisclaimerSlapp';

export default function ReportarPage() {
  const [formData, setFormData] = useState({
    entidad_reportada: '',
    descripcion: '',
    numero_contrato: '',
    archivo_url: ''
  });
  const [status, setStatus] = useState<'IDLE' | 'LOADING' | 'SUCCESS' | 'ERROR'>('IDLE');
  const [reference, setReference] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.descripcion.length < 50) return;
    
    setStatus('LOADING');
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    try {
      const res = await fetch(`${apiUrl}/api/reportar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      
      if (res.ok) {
        const data = await res.json();
        setReference(data.codigo_referencia);
        setStatus('SUCCESS');
      } else {
        setStatus('ERROR');
      }
    } catch (err) {
      console.error(err);
      setStatus('ERROR');
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="container mx-auto px-4 py-24 max-w-4xl min-h-screen">
      <div className="space-y-8">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-4"
        >
          <div className="w-20 h-20 bg-rose-500/10 rounded-3xl flex items-center justify-center border border-rose-500/20 mx-auto mb-6">
            <ShieldAlert size={40} className="text-rose-500" />
          </div>
          <h1 className="text-4xl md:text-5xl font-black tracking-tight">Reporte <span className="text-white">Anónimo</span> SOS</h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto leading-relaxed">
            Si tienes evidencia de riesgos en un contrato en Medellín, repórtalo aquí. 
            **No guardamos tu IP, correo ni identidad.** Tu seguridad es nuestra prioridad.
          </p>
        </motion.div>

        {status === 'SUCCESS' ? (
          <motion.div 
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="card-premium p-12 text-center space-y-8 bg-emerald-500/5 border-emerald-500/20"
          >
            <CheckCircle2 size={64} className="text-emerald-500 mx-auto" />
            <div className="space-y-2">
              <h2 className="text-3xl font-black">Reporte Recibido</h2>
              <p className="text-slate-400">Guarda tu código de seguimiento anónimo:</p>
            </div>
            
            <div className="flex items-center justify-center gap-4 bg-slate-950 p-6 rounded-2xl border border-white/5 shadow-inner group">
              <span className="text-4xl font-black text-emerald-400 tracking-wider font-mono">{reference}</span>
              <button 
                onClick={() => reference && copyToClipboard(reference)}
                className="p-3 bg-slate-900 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all active:scale-95"
              >
                <Copy size={20} />
              </button>
            </div>
            
            <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl flex gap-4 text-left">
              <AlertCircle className="text-amber-500 shrink-0" size={24} />
              <p className="text-xs text-amber-200/70 leading-relaxed font-medium">
                IMPORTANT: No hay forma de recuperar este código si lo pierdes. Lupa no almacena identidades y no puede relacionarte con este reporte.
              </p>
            </div>

            <button 
              onClick={() => { setStatus('IDLE'); setFormData({ entidad_reportada: '', descripcion: '', numero_contrato: '', archivo_url: '' }); }}
              className="px-8 py-3 bg-slate-800 text-slate-200 font-bold rounded-xl border border-white/5 hover:bg-slate-700 transition-all"
            >
              Realizar otro reporte
            </button>
          </motion.div>
        ) : (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <form onSubmit={handleSubmit} className="card-premium p-8 md:p-12 space-y-8 bg-slate-900/50">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-3">
                  <label className="text-[10px] uppercase font-black tracking-widest text-slate-500 ml-1">Entidad Reportada *</label>
                  <input 
                    required
                    type="text"
                    placeholder="Ej: Alcaldía de Medellín / INDER"
                    className="w-full bg-slate-950 border border-white/10 rounded-xl px-5 py-4 focus:border-primary focus:ring-1 focus:ring-primary transition-all outline-none text-white font-medium"
                    value={formData.entidad_reportada}
                    onChange={e => setFormData({...formData, entidad_reportada: e.target.value})}
                  />
                </div>
                <div className="space-y-3">
                  <label className="text-[10px] uppercase font-black tracking-widest text-slate-500 ml-1">Número de Contrato (Opcional)</label>
                  <input 
                    type="text"
                    placeholder="Ej: CO1.PCCNTR.4321..."
                    className="w-full bg-slate-950 border border-white/10 rounded-xl px-5 py-4 focus:border-primary focus:ring-1 focus:ring-primary transition-all outline-none text-white font-medium"
                    value={formData.numero_contrato}
                    onChange={e => setFormData({...formData, numero_contrato: e.target.value})}
                  />
                </div>
              </div>

              <div className="space-y-3">
                <label className="text-[10px] uppercase font-black tracking-widest text-slate-500 ml-1">Descripción del Riesgo *</label>
                <textarea 
                  required
                  placeholder="Explica qué está mal en este contrato... (Mínimo 50 caracteres)"
                  className="w-full bg-slate-950 border border-white/10 rounded-xl px-5 py-4 min-h-[180px] focus:border-primary focus:ring-1 focus:ring-primary transition-all outline-none text-white font-medium resize-none leading-relaxed"
                  value={formData.descripcion}
                  onChange={e => setFormData({...formData, descripcion: e.target.value})}
                />
                <div className="flex justify-between items-center px-1">
                  <p className={`text-[10px] font-bold ${formData.descripcion.length >= 50 ? 'text-emerald-500' : 'text-slate-600'}`}>
                    CARACTERES: {formData.descripcion.length} / 50
                  </p>
                  {formData.descripcion.length > 0 && formData.descripcion.length < 50 && (
                    <p className="text-[10px] font-black text-rose-500 uppercase tracking-tight">Faltan {50 - formData.descripcion.length} caracteres</p>
                  )}
                </div>
              </div>

              <div className="flex items-start gap-4 p-6 bg-blue-500/5 rounded-2xl border border-blue-500/20 shadow-inner">
                <Lock className="text-blue-500 shrink-0" size={20} />
                <div className="space-y-1">
                  <h4 className="text-sm font-bold text-blue-100">Cifrado y Privacidad Garantizada</h4>
                  <p className="text-xs text-blue-200/50 leading-relaxed">
                    Al enviar este formulario, tu IP ({status === 'LOADING' ? '0.0.0.0' : '---.---.---.---'}) no es capturada. 
                    El endpoint de backend está auditado para ignorar metadatos de conexión.
                  </p>
                </div>
              </div>

              <button 
                disabled={status === 'LOADING' || formData.descripcion.length < 50}
                className="w-full py-5 bg-primary text-white font-black rounded-2xl shadow-xl shadow-primary/20 hover:bg-primary/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98] flex items-center justify-center gap-3 text-lg"
              >
                {status === 'LOADING' ? (
                  <span className="w-6 h-6 border-4 border-white/20 border-t-white rounded-full animate-spin" />
                ) : (
                  <>Enviar Reporte SOS <Send size={20} /></>
                )}
              </button>
            </form>
          </motion.div>
        )}
      </div>

      <DisclaimerSlapp />
    </div>
  );
}
