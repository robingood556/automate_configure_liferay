# Variables File

variable "resource_group" {
  description = "The name of your Azure Resource Group."
  default     = "Netcracker"
}

variable "address_space" {
  description = "address_space Netcracker"
  default     = "10.0.0.0/16"
}

variable "subnet_prefix" {
  description = "The address prefix to use for the subnet Netcracker"
  default     = "10.0.1.0/24"
}

variable "location" {
  description = "The region"
  default     = "eastus"
}

variable "vm_standart_size" {
  description = "Standart size of the virtual machine."
  default     = "Standard_D1_v2"
}

variable "image_publisher" {
  description = "Name of the publisher of the image"
  default     = "OpenLogic"
}

variable "image_offer" {
  description = "Name of the offer"
  default     = "Centos"
}

variable "image_sku" {
  description = "Image SKU"
  default     = "7.5"
}

variable "image_version" {
  description = "Version of the image"
  default     = "latest"
}

variable "admin_username" {
  description = "Administrator user name"
  default     = "azureuser"
}

variable "vm_big_size" {
  description = "Big size of the virtual machine."
  default     = "Standard_D2as_v4"
}





