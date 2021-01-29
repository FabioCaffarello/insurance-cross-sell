SELECT u.id
                        ,u.gender
                        ,u.age
                        ,u.region_code
                        ,u.policy_sales_channel
                        ,v.driving_license
                        ,v.vehicle_age
                        ,v.vehicle_damage
                        ,i.previously_insured
                        ,i.annual_premium
                        ,i.vintage
                        ,i.response
               FROM pa004.users AS u 
               INNER JOIN pa004.vehicle AS v ON u.id = v.id 
               INNER JOIN pa004.insurance AS i ON u.id = i.id