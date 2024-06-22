CREATE TABLE IF NOT EXISTS public.dimension_finance (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR NOT NULL,
    budget FLOAT NOT NULL
);

INSERT INTO public.dimension_finance (category_name, budget) VALUES
('final de semana', 1000),
('mercado' , 500);

