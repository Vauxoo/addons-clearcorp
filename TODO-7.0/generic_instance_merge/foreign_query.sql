SELECT A.relname AS tabla, C.attname AS columna, B.relname AS tabla_foranea, D.attname AS columna_foranea
            FROM pg_catalog.pg_constraint, pg_catalog.pg_class AS A, pg_catalog.pg_class AS B, pg_catalog.pg_attribute C, pg_catalog.pg_attribute D 
            WHERE contype = 'f'
            AND conrelid = A.oid 
            AND confrelid = B.oid 
            AND conrelid = C.attrelid 
            AND confrelid = D.attrelid 
            AND C.attnum = pg_catalog.pg_constraint.conkey[1] 
            AND D.attnum = pg_catalog.pg_constraint.confkey[1] 
--            AND B.relname =''
--          AND D.attname ='id'
            ORDER BY tabla, columna, tabla_foranea, columna_foranea; 
