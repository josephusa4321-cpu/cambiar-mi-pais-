import React from 'react';
import Link from 'next/link';
import { Eye, Github, Twitter, Send } from 'lucide-react';
import DisclaimerSlapp from '@/components/ui/DisclaimerSlapp';

export default function Footer() {
  return (
    <footer className="w-full bg-slate-950 pt-12 pb-8 border-t border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Anti-SLAPP Disclaimer (Mandatorio por GEMINI.MD) */}
        <DisclaimerSlapp />

        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mt-12 mb-12">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2 space-y-4">
            <div className="flex items-center gap-2">
              <Eye className="text-primary" size={20} />
              <span className="text-lg font-black tracking-tighter text-white">LUPA</span>
            </div>
            <p className="text-slate-400 text-sm max-w-xs leading-relaxed">
              Tecnología ciudadana para la transparencia en Medellín. 
              Monitoreo determinista de contratación pública mediante algoritmos de riesgo.
            </p>
            <div className="flex gap-4 pt-2">
              <Link href="#" className="p-2 bg-slate-900 rounded-lg text-slate-400 hover:text-white transition-colors">
                <Github size={18} />
              </Link>
              <Link href="#" className="p-2 bg-slate-900 rounded-lg text-slate-400 hover:text-white transition-colors">
                <Twitter size={18} />
              </Link>
              <Link href="#" className="p-2 bg-slate-900 rounded-lg text-slate-400 hover:text-white transition-colors">
                <Send size={18} />
              </Link>
            </div>
          </div>

          {/* Links 1 */}
          <div>
            <h4 className="text-white font-bold text-sm mb-4 uppercase tracking-wider">Explorar</h4>
            <ul className="space-y-2">
              <li><Link href="/top10" className="text-slate-400 hover:text-primary text-sm transition-colors">Top 10 Riesgo</Link></li>
              <li><Link href="/opacos" className="text-slate-400 hover:text-primary text-sm transition-colors">Convenios Opacos</Link></li>
              <li><Link href="/impunidad" className="text-slate-400 hover:text-primary text-sm transition-colors">Línea de Impunidad</Link></li>
            </ul>
          </div>

          {/* Links 2 */}
          <div>
            <h4 className="text-white font-bold text-sm mb-4 uppercase tracking-wider">Recursos</h4>
            <ul className="space-y-2">
              <li><Link href="/metodologia" className="text-slate-400 hover:text-primary text-sm transition-colors">Metodología LUPA</Link></li>
              <li><Link href="/datos" className="text-slate-400 hover:text-primary text-sm transition-colors">Fuentes de Datos</Link></li>
              <li><Link href="/contacto" className="text-slate-400 hover:text-primary text-sm transition-colors">Contacto Veeduría</Link></li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-xs text-slate-500 font-medium italic">
            © {new Date().getFullYear()} Proyecto LUPA — Medellín, Colombia. 
            Sin afiliación gubernamental.
          </p>
          <div className="flex gap-6">
            <Link href="/privacidad" className="text-xs text-slate-600 hover:text-slate-400 font-medium uppercase tracking-widest">Privacidad</Link>
            <Link href="/legal" className="text-xs text-slate-600 hover:text-slate-400 font-medium uppercase tracking-widest">Términos Legales</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
