"use client";

import React from 'react';
import { motion } from 'motion/react';

interface ScoreBarProps {
  score: number;
  showLabel?: boolean;
}

export const ScoreBar: React.FC<ScoreBarProps> = ({ score, showLabel = true }) => {
  // Escala de colores según el score (LUPA Engine)
  const getScoreColor = (s: number) => {
    if (s < 40) return 'bg-emerald-500'; // Bajo
    if (s < 55) return 'bg-yellow-500';  // Medio
    if (s < 70) return 'bg-orange-500';  // Alto
    return 'bg-red-600';                 // Crítico
  };

  const getNivelRiesgo = (s: number) => {
    if (s < 40) return 'BAJO';
    if (s < 55) return 'MEDIO';
    if (s < 70) return 'ALTO';
    return 'CRÍTICO';
  };

  return (
    <div className="w-full space-y-2">
      {showLabel && (
        <div className="flex justify-between items-end">
          <span className="text-xs font-bold text-slate-500 tracking-widest uppercase">
            Riesgo: <span className={getScoreColor(score).replace('bg-', 'text-')}>{getNivelRiesgo(score)}</span>
          </span>
          <span className="text-sm font-black text-slate-200">{score}/100</span>
        </div>
      )}
      <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden border border-white/5">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={`h-full ${getScoreColor(score)} shadow-[0_0_10px_rgba(0,0,0,0.5)]`}
        />
      </div>
    </div>
  );
};

export default ScoreBar;
