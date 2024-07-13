CREATE TABLE IF NOT EXISTS public.dimension_finance (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR NOT NULL UNIQUE,
    budget FLOAT NOT NULL
);

INSERT INTO public.dimension_finance (category_name, budget) VALUES
('final de semana', 1000),
('mercado' , 500);


CREATE TABLE IF NOT EXISTS public.fact_finance (

    transaction_id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES public.dimension_finance(category_id),
    tag VARCHAR NOT NULL,
    datetime_transaction TIMESTAMP NOT NULL,
    credit_card VARCHAR NOT NULL,
    amount FLOAT NOT NULL 

)
