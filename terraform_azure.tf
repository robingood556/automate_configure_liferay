terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=2.46.0"
    }
  }
}
provider "azurerm" {
    # The "feature" block is required for AzureRM provider 2.x.
    # If you're using version 1.x, the "features" block is not allowed.
    features {}
}
# Create a resource group if it doesn't exist
resource "azurerm_resource_group" "myterraformgroup" {
    name     = "${var.resource_group}"
    location = "${var.location}"
}

resource "azurerm_virtual_network" "myterraformnetwork" {
 name                = "${var.resource_group}net"
 address_space       = ["${var.address_space}"]
 location            = "${var.location}"
 resource_group_name = azurerm_resource_group.myterraformgroup.name
}

resource "azurerm_subnet" "myterraformsubnet" {
 name                 = "${var.resource_group}sub"
 resource_group_name  = azurerm_resource_group.myterraformgroup.name
 virtual_network_name = azurerm_virtual_network.myterraformnetwork.name
 address_prefixes     = ["${var.subnet_prefix}"]
}

resource "azurerm_public_ip" "myterraformpublicip" {
 count			      = 3
 name                         = "publicIP${count.index}"
 location                     = "${var.location}"
 resource_group_name          = azurerm_resource_group.myterraformgroup.name
 allocation_method            = "Static"
}

resource "azurerm_network_security_group" "myterraformnsg" {
    name                = "${var.resource_group}NetworkSecurityGroup"
    location            = "${var.location}"
    resource_group_name = azurerm_resource_group.myterraformgroup.name

    security_rule {
        name                       = "SSH"
        priority                   = 1001
        direction                  = "Inbound"
        access                     = "Allow"
        protocol                   = "Tcp"
        source_port_range          = "*"
        destination_port_range     = "22"
        source_address_prefix      = "*"
        destination_address_prefix = "*"
    }
    security_rule {
        name                       = "8080port"
        priority                   = 1002
        direction                  = "Inbound"
        access                     = "Allow"
        protocol                   = "Tcp"
        source_port_range          = "*"
        destination_port_range     = "8080"
        source_address_prefix      = "*"
        destination_address_prefix = "*"
    }
}

resource "azurerm_network_interface" "myterraformnic" {
 count               = 3
 name                = "NIC${count.index}"
 location            = "${var.location}"
 resource_group_name = azurerm_resource_group.myterraformgroup.name

 ip_configuration {
   name                          = "NicConfiguration"
   subnet_id                     = azurerm_subnet.myterraformsubnet.id
   private_ip_address_allocation = "Dynamic"
   public_ip_address_id		 = element(azurerm_public_ip.myterraformpublicip.*.id, count.index)
 }
}


# Connect the security group to the network interface
resource "azurerm_network_interface_security_group_association" "securitygroup"{
    count 		      = length(azurerm_network_interface.myterraformnic.*.id)
    network_interface_id      = element(azurerm_network_interface.myterraformnic.*.id, count.index)
    network_security_group_id = azurerm_network_security_group.myterraformnsg.id
}


resource "azurerm_linux_virtual_machine" "myterraformvm" {
 count                 = 2
 name                  = "${var.resource_group}VM${count.index}"
 location              = "${var.location}"
 resource_group_name   = azurerm_resource_group.myterraformgroup.name
 network_interface_ids = [element(azurerm_network_interface.myterraformnic.*.id, count.index)]
 size                  = "${var.vm_standart_size}"
 admin_username	       = "${var.admin_username}"

 disable_password_authentication = true

 # Uncomment this line to delete the OS disk automatically when deleting the VM
 # delete_os_disk_on_termination = true

 # Uncomment this line to delete the data disks automatically when deleting the VM
 # delete_data_disks_on_termination = true

 source_image_reference {
   publisher = "${var.image_publisher}"
   offer     = "${var.image_offer}"
   sku       = "${var.image_sku}"
   version   = "${var.image_version}"
 }

 os_disk {
   name              = "myosdisk${count.index}"
   caching           = "ReadWrite"
   storage_account_type = "Standard_LRS"
}

 admin_ssh_key {
	username       = "${var.admin_username}"
        public_key     = file("~/.ssh/id_rsa.pub")
 }

 tags = {
   environment = "staging"
 }
}

resource "azurerm_linux_virtual_machine" "myterraformvms" {
 name                  = "${var.resource_group}VMbig"
 location              = "${var.location}"
 resource_group_name   = azurerm_resource_group.myterraformgroup.name
 network_interface_ids = [azurerm_network_interface.myterraformnic[2].id]
 size                  = "${var.vm_big_size}"
 admin_username	       = "${var.admin_username}"

 disable_password_authentication = true

 # Uncomment this line to delete the OS disk automatically when deleting the VM
 # delete_os_disk_on_termination = true

 # Uncomment this line to delete the data disks automatically when deleting the VM
 # delete_data_disks_on_termination = true

 source_image_reference {
   publisher = "${var.image_publisher}"
   offer     = "${var.image_offer}"
   sku       = "${var.image_sku}"
   version   = "${var.image_version}"
 }

 os_disk {
   name              = "myosdiskforbigvm"
   caching           = "ReadWrite"
   storage_account_type = "Standard_LRS"
}

 admin_ssh_key {
	username       = "${var.admin_username}"
        public_key     = file("~/.ssh/id_rsa.pub")
 }
}
