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
* an HTTP endpoint service able to query the db

The playbook `provision_demo.yml` is used to install and configure the three
services, running
```
ansible-playbook -i ./hosts provision_demo.yml -l demoserver --private-key=<generated-key>-private.pem
```
