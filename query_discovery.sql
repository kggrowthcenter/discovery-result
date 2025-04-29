 SELECT u.id,
 		u.email,
 		u.name,
 		u.phone,
 		u.created_at AS 'register_date',
        CASE WHEN ubr.bundle_id = 1 then 'GI'
        	when ubr.bundle_id =2 then 'LEAN'
        	WHEN ubr.bundle_id =3 then 'ELITE'
        	when ubr.bundle_id =4 then 'Genuine'
        	WHEN ubr.bundle_id =5 then 'Astaka'
        END AS bundle_name,
        t.name AS 'test_name',
        ur.test_result_attribute->>'$[0].name' as typology,
        CASE
	        WHEN ubr.bundle_id = 4 THEN ROUND((ur.total_score / 50) * 100,0)
	        WHEN ubr.bundle_id = 5 THEN ROUND((ur.total_score / 42) *100,0)
	        ELSE ur.total_score
	    END AS 'total_score',
        ubr.result_name as final_result,
        ubr.created_at 'taken_date'
FROM user_results ur
LEFT JOIN tests t ON
    ur.test_id = t.id
JOIN users u ON
    ur.user_id = u.id
JOIN user_bundle_result_user_result ubrur on
	ur.id = ubrur.user_result_id
JOIN user_bundle_results ubr on
	ubrur.user_bundle_result_id = ubr.id
WHERE
	ubr.created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
ORDER BY
	ubr.created_at DESC, id, bundle_name, total_score DESC
