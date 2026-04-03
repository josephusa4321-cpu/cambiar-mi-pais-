'use client';

import React, { useState } from 'react';
import { Copy, CheckCircle2 } from 'lucide-react';

interface Props {
  contractId: string;
  score: number;
  entidad: string;
  valor: number;
}

export default function CopyComplaintButton({ contractId, score, entidad, valor }: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const text = `
SOLICITUD DE REVISIÓN CIUDADANA - LUPA MEDELLÍN SOS
--------------------------------------------------
ID CONTRATO: ${contractId}
ENTIDAD: ${entidad}
VALOR: $${Number(valor).toLocaleString()} COP
PUNTUACIÓN DE RIESGO ALGORÍTMICO: ${score}/100

MOTIVO DE LA SOLICITUD:
Basado en datos públicos del SECOP II, este contrato presenta indicadores de anomalía estadística (Score ${score}). Se solicita a los organismos de control (Contraloría/Personería) una auditoría especial para verificar el cumplimiento de los principios de transparencia y economía.

AVISO LEGAL:
Este reporte es una alerta ciudadana independiente basada en análisis de datos. No constituye una acusación penal ni prejuzga responsabilidad de funcionarios.

Generado por Lupa Medellín SOS (https://lupa-sos.co)
    `.trim();

    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  return (
    <button 
      onClick={handleCopy}
      className={`w-full py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${
        copied 
        ? 'bg-emerald-500 text-white border-emerald-400' 
        : 'bg-rose-600 hover:bg-rose-700 text-white border-rose-500/50 shadow-lg shadow-rose-900/20'
      } border`}
    >
      {copied ? (
        <>
          <CheckCircle2 size={18} /> Borrador Copiado
        </>
      ) : (
        <>
          <Copy size={18} /> Copiar Borrador de Denuncia
        </>
      )}
    </button>
  );
}
