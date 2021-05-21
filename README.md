# Description
This file is an clarifying note for using the "install" software product.
This product is a system for automatic deployment of cloud infrastructure, the main task of which is to install Liferay and integrate it with PostgreSQL from Jenkins and Ansible in Microsoft Azure. 

# The main tasks solved by the product
1. Testing software products in environments: postgreSQL, Jenkins, Liferay (for Testers)
2. To get a ready-made server solution (for system administrators)
3. Creating a simple workspace for generalists (developers, datascientists)
4. For educational and educational tasks (for instructors, lectures, direction curators, timeleads)

# Tasks performed:
1. Makes "update" of the main OS repository
2. Install Python3 and PIP required to start the deployment process
3. Install software components terraform, ansible, azurecli - necessary to automate the process of deploying infrastructure
4. Generates ansible inventory file, depending on the characteristics of the deployment VMs
5. Connects ansible-vars and ansible-roles for automatization deployment of the server component.
6. Establishes connection, basic setup, preparation for using postgreSQL, Jenkins, Liferay servers

# Basic ansible functions:

- Install TomcatXJenkins and setup Jenkins and run PostgreSQL-Liferay-Wildfly deploy pipeline
- Jenkins pipline:
    - Install postgreSQL server:
        - Configuring postgreSQL
        - Creating psql role
- Install liferay+wildfly-bundle and configures Liferay:
    - Downloading postgres.jar and adding liferay config
 
# To get to at the output:
   - Complete Tomcat-Jenkins server, basic Jenkins setup, starting the postgresql-liferay-wildfly deployment process
   - Installation and basic configuration of the postgreSQL server, creating the psql role
   - Install liferay + wildfly-bundle, basic Liferay setup:
   - Downloaded postgres.jar file, adding liferay config

# Authenticating in Azure  using client secrtet 

Create the Service Principal which will have permissions to manage resources in the specified Subscription using the following command:
```
 az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/SUBSCRIPTION_ID"
```
output:
```
{
  "appId": "00000000-0000-0000-0000-000000000000",
  "displayName": "azure-cli-2017-06-05-10-41-15",
  "name": "http://azure-cli-2017-06-05-10-41-15",
  "password": "0000-0000-0000-0000-000000000000",
  "tenant": "00000000-0000-0000-0000-000000000000"
}
```
These values map to the Terraform variables like so:

- ``appId`` is the ``client_id`` defined above.
- ``password`` is the ``client_secret`` defined above.
- ``tenant`` is the ``tenant_id`` defined above.

# Running on the host

Export Azure credentials

```
$ export ARM_CLIENT_ID="00000000-0000-0000-0000-000000000000"
$ export ARM_CLIENT_SECRET="00000000-0000-0000-0000-000000000000"
$ export ARM_SUBSCRIPTION_ID="00000000-0000-0000-0000-000000000000"
$ export ARM_TENANT_ID="00000000-0000-0000-0000-000000000000"
```


Go to **netcracker_edu_project** directory and use the command
```
./install.sh -e [e-mail for Liferay]
```
# Overview
## install.sh
Install python3 and other dependencies.
```
#!/bin/bash

sudo yum update 
sudo yum install -y python3
sudo yum install -y python3-pip
pip3 install --upgrade pip
pip3 install -r requirements.txt
python3 demo.py $@
```
## demo.py
Install all requirements, generates inventory files and ansible variables file, runs ansible-playbook.

Try --help to see which components can be set manually
```
python3 demo.py --help
```
## terraform_azure.tf
Basic terraform functions:

- Creating resource group
- Configuring virtual network (public\private)
- Create security group
- Create 3 virtual machines in Microsoft Azure:
    - 2 virtual machines - Standard_D1_v2
    - 1 virtual machine  - Standard_D2as_v4



