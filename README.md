# demo
Create an ec2 instance, setup a demo for data ingestion and analysis

## notes

This is just a demo, use carefully.

## install requirements

All needed requirements (Ansible 2.4, Boto library to handle AWS resources) can
be installed through:
```
pip install -r requirements.txt
```

## create the ec2 instance

The playbook `ec2-provision.yml` is able to create an ec2 instance in N. Virginia.
An SSH key pair is created in the specified region and the private key is locally
stored. The inventory file (`hosts`) is automatically configured with the correct
external IP assigned during the creation.

Once the instance is created, try to login:
```
ssh ubuntu@<generated-ip> -i <generated-key>-private.pem
```

## setup the demo

The demo contains:
* an ingestion service that load data to a PostgreSQL db
* a confgured PostgreSQL db (`postgresql` Ansible role)
* a webserver service able to query the db

The playbook `provision_demo.yml` is used to install and configure services and
scripts, running
```
ansible-playbook -i ./hosts provision_demo.yml -l demoserver --private-key=<generated-key>-private.pem
```

## query the db

The demo configure a Webserver service able to query the DB. The server listens
port 80, and queries can be submitted with the following endpoint:

* first_query/
```
WITH dev AS (
    SELECT device,
           count(*) AS count
      FROM sessions
    GROUP BY device)
SELECT device,
       max(count) OVER (PARTITION BY device)
  FROM dev LIMIT 1;
```

* second_query/
```
SELECT sessionid,
       mouse_distance
  FROM mouse_moves
ORDER BY mouse_distance DESC
  LIMIT 1;
```

* third_query/
```
SELECT CASE WHEN device = 0 THEN 'desktop'
            WHEN device = 1 THEN 'mobile'
            WHEN device = 2 THEN 'tablet'
       END,
       round(avg_resp_clicks, 2)
  FROM (
      SELECT count(a.sessionid) OVER w AS count,
             b.device AS device,
             avg(resp_clicks) OVER w AS avg_resp_clicks
        FROM clicks a INNER JOIN sessions b ON (a.sessionid = b.sessionid)
        WINDOW w AS (PARTITION BY a.sessionid) ) AS foo
  WHERE count > 1
  ORDER BY avg_resp_clicks DESC;
```

Ex. 
```
$ curl -X GET http://<generated-ip>/first_query


  The most used devise (271 times) is desktop
```
