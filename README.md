# demo
create an ec2 instance, setup a demo for data ingestion and analysis

## create the ec2 instance

The playbook `ec2-provision.yml` is able to create an ec2 instance in N. Virginia.
An SSH key pair is created in the specified region and the private key is locally
stored. The inventory file (`hosts`) is automatically configured with the correct
external IP assigned during the creation.
