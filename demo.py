import argparse
import os
import random
import string
import subprocess
import yaml


from email_validator import validate_email, EmailNotValidError
from getpass import getpass


def gen_random_passwd(strLength=8):

    return ''.join(
        random.choice(
            string.digits + 2 * string.ascii_letters
            ) for i in range(strLength))


def get_rsa_private_key():

    """
    Load rsa private key
    """
    ssh_dir = os.path.expanduser("~/.ssh/")
    with open(ssh_dir + "id_rsa", "r") as ssh_key_file:
        return ''.join(ssh_key_file.readlines())


def nested_var(dictionary):

    for key in dictionary:
        if type(dictionary[key]) == dict:
            nested_var(dictionary[key])
        try:
            dictionary[key] = dictionary[key][-1]
        except KeyError:
            pass


def nested_interactiv_var(dictionary):

    flag = False
    for key in dictionary:
        if type(dictionary[key]) == dict:
            nested_interactiv_var(dictionary[key])
        try:
            if dictionary[key][0]:
                while not flag:
                    value = dictionary[key][2](dictionary[key][1])
                    flag = value
                    if not flag:
                        print("Empty string is not supported: Retry")
                flag = False
                dictionary[key] = value
            else:
                dictionary[key] = dictionary[key][1]
        except KeyError:
            pass


def generate_centOS_cmds():

    cmd_exec = [
        "sudo yum install -y yum-utils",
        "sudo yum -y install epel-release",
        "sudo yum-config-manager --add-repo"
        " https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo",
        "sudo yum -y install terraform",
        "sudo yum -y install jq",
        "sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc",
        "ssh-keygen -q -t rsa -N '' -f ~/.ssh/id_rsa <<<y 2>&1 >/dev/null",
        "terraform init; terraform apply --auto-approve",
        ]
    return cmd_exec


def prepare_os(gen_cmd_func):

    for command in gen_cmd_func():
        subprocess.run(command, shell=True)


def inventory_gen():

    """
    Generate ansible inventory file for runner host and Jenkins worker
    """
    output_first_session = subprocess.check_output(
            "terraform output -json instances_public_ips | jq -r '.[0]'",
            shell=True, encoding='utf-8').strip()
    output_second_session = subprocess.check_output(
            "terraform output -json instances_public_ips | jq -r '.[1]'",
            shell=True, encoding='utf-8').strip()
    output_third_session = subprocess.check_output(
            "terraform output -json instances_public_ips | jq -r '.[2]'",
            shell=True, encoding='utf-8').strip()
    output_first_private_session = subprocess.check_output(
            "terraform output -json vnet_subnets | jq -r '.[1]'",
            shell=True, encoding='utf-8').strip()
    output_second_private_session = subprocess.check_output(
            "terraform output -json vnet_subnets | jq -r '.[2]'",
            shell=True, encoding='utf-8').strip()


    ansible_dir = os.path.dirname(os.path.realpath(__file__)) + "/ansible/"

    with open(ansible_dir + "inventory.ini", "w") as first_inventory:

        first_inventory.write(
            "jenkins ansible_ssh_host="
            + output_first_session
            + " ansible_ssh_user=azureuser"
            + " ansible_ssh_private_key_file=~/.ssh/id_rsa\n"
            )
        first_inventory.write(
            "postgres ansible_ssh_host="
            + output_second_session
            + " ansible_ssh_user=azureuser"
            + " ansible_ssh_private_key_file=~/.ssh/id_rsa\n"
            )
        first_inventory.write(
            "liferay ansible_ssh_host="
            + output_third_session
            + " ansible_ssh_user=azureuser"
            + " ansible_ssh_private_key_file=~/.ssh/id_rsa\n"
            )

    with open(ansible_dir + "Jenkins_inventory.ini", "w") as second_inventory:
        second_inventory.write(
            "postgres ansible_ssh_host="
            + output_first_private_session
            + " ansible_ssh_user=azureuser\n")
        second_inventory.write(
            "liferay ansible_ssh_host="
            + output_second_private_session
            + " ansible_ssh_user=azureuser\n")


def create_parser():

    passwords = {key: gen_random_passwd() for
                 key in ("jenkins", "postgresql", "vault")}
    parser = argparse.ArgumentParser(
       description="Core srcipt of netcracker education project",
        )
    parser.add_argument(
       '--jenkins-password', "-jp", 
       required=False, default=passwords["jenkins"],
       dest='jenkins_password',
       help="Password for user admin in Jenkins",
        )
    parser.add_argument(
       '--vault-password', "-av", 
       required=False, default=passwords["vault"],
       dest='vault_password',
       help="Password for encription ansible extra variables file",
        )
    parser.add_argument(
        '--postgresql-user', '-pu', type=str,
        required=False, dest='postgresql_user',
        default='liferay', 
        help="PostgreSQL user name for usage by liferay",
        )
    parser.add_argument(
        "--postgresql-password", '-pp', type=str,
        required=False, dest='postgresql_password',
        default=passwords["postgresql"],
        help="PostgreSQL user password",
        )
    parser.add_argument(
        '--interactive', "-i", action='store_true',
        required=False, dest="interactive",
        help="Configure project in interactive mode",
        )
    parser.add_argument(
        '--admin-email', "-e", type=str,
        required=True, dest="email",
        help="Set liferay emai",
        )
    return parser


def gen_ansible_vars(parser_args):

    """
    Generate python structure for dump 
    to ansible variables file

    """
    variables = {
        "su_user": [
            False, "azureuser"],
        "rsa_private": [
            False, get_rsa_private_key()],
        "jenkins_admin_password": [
            True, "Enter Jenkins admin password: ", getpass,
            parser_args.jenkins_password],
        "liferay": {
            "locale": [False, "en_US"],
            "timezone": [False, "UTC"],
            "email_domain": [
                True, "Enter default email domain (e.g gmail.com): ",
                input, parser_args.email.split("@")[-1],
                ],
            "admin_email_prefix": [
                True,
                "Enter admin email prefix"
                "(e.g. if admin email is demo@tmp.com then prefix is demo): ",
                input, parser_args.email.split("@")[0],
                ],
            "db": {
                "user": [
                    True, "Enter postgreSQL user: ",
                    input, parser_args.postgresql_user,
                    ],
                "password": [
                    True, "Enter db user password: ",
                    getpass, parser_args.postgresql_password,
                    ],
                "name": [False, "liferay_portal"],
            },
        },
        "liferay_admin": {
            "email": [
                True, "Enter admin email: ",
                input, parser_args.email,
                ],
            "name": [
                False,
                "Admin",
                ],
            "surname": [
                False,
                "Admin",
                ]
            }
     }

    if parser_args.interactive:
        print("WARNING: interactive variables"
              " take precedence over passed through cmd")
        nested_interactiv_var(variables)
    else:
        nested_var(variables)

    return variables


def create_vault_password_file(password):
    
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(current_dir + "/vault_password.txt", "w") as fd:
        fd.write(password)
    with open(current_dir + "/vault_password.yaml", "w") as fd:
        fd.write(yaml.safe_dump({'vault_password': password}))


def create_ansible_var_file(variables):

    """
    Dump setup variables to file
    """
    ansible_dir = os.path.dirname(os.path.realpath(__file__))
    with open(ansible_dir + "/ansible/setup_vars.yaml", "w") as fd:
        fd.write(yaml.safe_dump(variables))


if __name__ == "__main__":

    parser = create_parser()
    parser = parser.parse_args()
    try:
        valid = validate_email(parser.email)
    except EmailNotValidError:
        print(f"Invalid email syntax: { parser.email }.\nExit.")
        exit()
    prepare_os(generate_centOS_cmds)
    inventory_gen()
    vars_for_dump = gen_ansible_vars(parser)
    create_ansible_var_file(vars_for_dump)
    create_vault_password_file(parser.vault_password)

    subprocess.run(
        "ansible-vault encrypt --vault-password-file"
        " vault_password.txt ansible/setup_vars.yaml",
        shell=True)

    subprocess.run(
        "ANSIBLE_CONFIG=ansible/ansible.cfg"
        " ansible-playbook -i ansible/inventory.ini"
        " ansible/jenkins_install.yaml"
        " --vault-password-file vault_password.txt"
        " --extra-vars '@vault_password.yaml'"
        " --extra-vars '@ansible/setup_vars.yaml'",
        shell=True)
