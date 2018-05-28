-- Drop the table if it exists
DROP TABLE IF EXISTS batch_test;

-- Create sample table
CREATE TABLE batch_test (id serial unique, number int default null, date timestamp with time zone default null);

-- Add some rows
INSERT INTO batch_test (number, date)
SELECT generate_series, null
FROM generate_series(1, 1000);
