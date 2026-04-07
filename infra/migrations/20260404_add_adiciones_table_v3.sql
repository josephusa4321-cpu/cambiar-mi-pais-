-- Migration: Create adiciones_raw table
-- Description: Table for SECOP II additions with composite PK (numero_contrato, fecha_adicion)
-- Sprint: 3 (Audited)

CREATE TABLE IF NOT EXISTS public.adiciones_raw (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    numero_contrato TEXT NOT NULL,
    tipo_adicion TEXT,
    valor_adicion NUMERIC(20, 2) DEFAULT 0,
    fecha_adicion TIMESTAMP WITH TIME ZONE NOT NULL,
    descripcion TEXT,
    dias_adicionados INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (numero_contrato, fecha_adicion)
);

-- Index for scoring performance
CREATE INDEX IF NOT EXISTS idx_adiciones_contrato ON public.adiciones_raw(numero_contrato);

-- RLS Policy (Read only for public if needed, or service_role only)
ALTER TABLE public.adiciones_raw ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable read/write for service_role" ON public.adiciones_raw
    FOR ALL USING (auth.role() = 'service_role');
