# Outputs File

output "instances_public_ips" {
  value       = "${azurerm_public_ip.myterraformpublicip.*.ip_address}"
}

output "vnet_subnets" {
  value       = azurerm_network_interface.myterraformnic.*.private_ip_address
}


