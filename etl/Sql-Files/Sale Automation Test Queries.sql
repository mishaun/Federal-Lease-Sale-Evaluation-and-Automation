use BLM_sales;

show tables;

select * from sale_info;
select * from leases limit 5;

select count(1) from new_prod;
select * from new_prod;

select s.sale_name, n.* 
from new_prod n
join sale_info s 
on s.id = n.sale_id
where s.sale_name = 'BLM WY 3-24-20'
and tract_id = 40;



SELECT id 
    FROM sale_info
    WHERE sale_name = 'BLM MT 9-22-20';

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

