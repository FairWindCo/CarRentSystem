DUMP BASE DATA
dumpdata balance car_management car_rent -o new_data.json -e car_rent.carinrentpage -e car_rent.returncarrentpage -e car_rent.adddepositcarrentpage -e car_rent.penaltydepositcarrentpage -e car_rent.returncarrentadmin_model




select sum(bank_amount), sum(many_in_cash) from carmanagment_taxitrip
where timestamp > date('2021-12-10') and timestamp <  date('2021-12-11')

union select sum(bank_amount), sum(amount-many_in_cash) from carmanagment_taxitrip
where timestamp > date('2021-12-10') and timestamp <  date('2021-12-11')

union select sum(bank_amount), sum(amount) from carmanagment_taxitrip
where timestamp > date('2021-12-10') and timestamp <  date('2021-12-11')