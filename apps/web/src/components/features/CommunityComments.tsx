'use client';

import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { Button } from '@/components/ui';
import { MessageSquare, ShieldCheck, User } from 'lucide-react';

interface Comment {
  id_denuncia: string;
  codigo_lupa: string;
  descripcion: string;
  fecha_creacion: string;
}

export default function CommunityComments({ contractId }: { contractId: string }) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    async function fetchComments() {
      const { data, error } = await supabase
        .from('denuncias_anonimas')
        .select('*')
        .eq('id_contrato', contractId)
        .order('fecha_creacion', { ascending: false });

      if (data) setComments(data);
    }
    fetchComments();
  }, [contractId, supabase]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setIsSubmitting(true);
    const randomCode = `LUPA-${Math.random().toString(36).substring(2, 8).toUpperCase()}`;

    const { error } = await supabase.from('denuncias_anonimas').insert({
      id_contrato: contractId,
      descripcion: newComment,
      codigo_lupa: randomCode,
    });

    if (!error) {
      setComments([{
        id_denuncia: Math.random().toString(),
        codigo_lupa: randomCode,
        descripcion: newComment,
        fecha_creacion: new Date().toISOString()
      }, ...comments]);
      setNewComment('');
    }
    setIsSubmitting(false);
  };

  return (
    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 backdrop-blur-sm">
      <div className="flex items-center gap-3 mb-6">
        <MessageSquare className="text-blue-400" size={20} />
        <h3 className="text-xl font-bold font-outfit text-white">Observaciones Ciudadanas</h3>
        <span className="bg-blue-500/10 text-blue-400 text-xs px-2 py-1 rounded-full border border-blue-500/20">
          Privado & Anónimo
        </span>
      </div>

      <form onSubmit={handleSubmit} className="mb-8">
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="¿Viste algo inusual en este contrato? Tu reporte es 100% anónimo..."
          className="w-full bg-slate-950/50 border border-slate-800 rounded-lg p-4 text-slate-300 focus:ring-2 focus:ring-blue-500/50 outline-none min-h-[100px] transition-all"
        />
        <div className="flex justify-between items-center mt-3">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <ShieldCheck size={14} className="text-emerald-500" />
            No guardamos tu IP según Regla de Privacidad v1.0
          </div>
          <Button 
            disabled={isSubmitting || !newComment.trim()}
            className="bg-blue-600 hover:bg-blue-500 text-white font-bold px-6"
          >
            {isSubmitting ? 'Enviando...' : 'Publicar Observación'}
          </Button>
        </div>
      </form>

      <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
        {comments.length === 0 ? (
          <p className="text-center text-slate-500 py-4 italic">Aún no hay observaciones ciudadanas.</p>
        ) : (
          comments.map((comment) => (
            <div key={comment.id_denuncia} className="bg-slate-950/40 border border-slate-800/50 rounded-lg p-4 transition-all hover:border-slate-700">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 text-slate-400 text-xs font-mono">
                  <User size={12} />
                  {comment.codigo_lupa}
                </div>
                <div className="text-slate-500 text-[10px]">
                  {new Date(comment.fecha_creacion).toLocaleDateString()}
                </div>
              </div>
              <p className="text-slate-300 text-sm leading-relaxed">
                {comment.descripcion}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
