-- SQLite
SELECT txn_type, category, sub_category, count(*) as count
FROM transactions
group by txn_type, category, sub_category
ORDER BY 4 desc;

-- 1353
SELECT "Categorized" as COUNT_TYPE, count(*) as count
FROM transactions
where txn_type in ('Expense', 'Income', 'Transfer', 'Investment')
UNION
SELECT "Uncategorized" as COUNT_TYPE, count(*) as count
FROM transactions
where txn_type not in ('Expense', 'Income', 'Transfer', 'Investment')
UNION
SELECT "Total" as COUNT_TYPE, count(*) as count
FROM transactions




select * from transactions
where narration = 'WWW ACKO COM             GURGAON'
  and (CAST(REPLACE(txn_amount, ',', '') AS REAL) - 7949.38) < 0.01;

select *, 
  (CAST(REPLACE(txn_amount, ',', '') AS REAL) - 7949.38) as diff
from transactions
where narration = 'WWW ACKO COM             GURGAON';

select * from transactions where txn_source = 'CC2486' and narration = 'NETBANKING TRANSFER (Ref# 00000000000128016172396)';

select * from transactions where txn_date = '2025-01-30';