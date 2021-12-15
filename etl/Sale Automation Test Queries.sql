use BLM_sales;

select * from sale_info;
select * from leases limit 5;

select count(1) from leases;

select count(1)
from
(
	select s.sale_name, l.grantee
	from sale_info s 
	join leases l on s.id = l.sale_id
) a;


select column_name, column_type
from information_schema.columns
where table_name = 'sale_info';


select column_name, column_type
from information_schema.columns
where table_name = 'leases';

ALTER TABLE sale_info
MODIFY sale_date DATE;

