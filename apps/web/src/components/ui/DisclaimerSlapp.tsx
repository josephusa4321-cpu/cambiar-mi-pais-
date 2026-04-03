import React from 'react';

/**
 * ⚠️ REGLA DE ORO LEGAL (Anti-SLAPP)
 * Este componente está HARDCODED y NO debe ser configurable.
 * Debe aparecer en el footer o en lugares prominentes de la aplicación.
 */
export const DisclaimerSlapp: React.FC = () => {
  return (
    <div className="p-4 my-6 bg-slate-900/50 border border-slate-800 rounded-lg text-sm text-slate-400 leading-relaxed shadow-sm">
      <div className="flex items-start gap-3">
        <span className="text-amber-500 font-bold">⚠️ NOTA LEGAL:</span>
        <p>
          Este sistema utiliza un <strong>modelo de riesgo algorítmico</strong> basado exclusivamente en datos públicos 
          proporcionados por el portal <span className="text-slate-300">datos.gov.co</span> (SECOP II). 
          Los puntajes y alertas generados representan una <strong>probabilidad estadística de irregularidad</strong> y 
          no constituyen una acusación formal de corrupción ni una prueba de ilegalidad. 
          LUPA promueve la veeduría ciudadana técnica y objetiva.
        </p>
      </div>
    </div>
  );
};

export default DisclaimerSlapp;
