terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
  backend "s3" {
     endpoints = {
      s3 = "https://storage.yandexcloud.net"
    }
    bucket = "dwpf-storage-terraform"
    region = "ru-central1"
    key    = "states/state.tfstate"

    skip_region_validation      = true
    skip_credentials_validation = true
    skip_requesting_account_id  = true
    skip_s3_checksum            = true

  }
  required_version = ">= 0.13"
}

provider "yandex" {
  zone = "ru-central1-a"
}

data "yandex_compute_image" "container-optimized-image" {
  family = "container-optimized-image"
}

locals {
  storage_id = "fhmpfo86rchd9f43oklc"
}

#resource "yandex_compute_disk" "empty-disk" {
#  name       = "empty-disk"
#  type       = "network-hdd"
#  size       = 20
#}

resource "yandex_compute_instance" "vm-1" {
  name = "fb"

  resources {
    cores  = 2
    memory = 1
    core_fraction = 5
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.container-optimized-image.id
    }
  }

  secondary_disk {
#    disk_id = yandex_compute_disk.empty-disk.id
    disk_id = local.storage_id
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.subnet-1.id
    nat       = true
    nat_ip_address = yandex_vpc_address.addr.external_ipv4_address[0].address
  }

  service_account_id = "ajen1tae40l1m54cklch"

  metadata = {
#    docker-container-declaration = file("${path.module}/declaration.yaml")
    docker-compose = file("${path.module}/docker-compose.yaml")
    user-data = file("${path.module}/cloud_config.yaml")
  }
}

resource "yandex_vpc_network" "network-1" {
  name = "network1"
}

resource "yandex_vpc_address" "addr" {
  name = "dwpf-adress"

  external_ipv4_address {
    zone_id = "ru-central1-a"
  }
}

output "external_ip_address_static" {
  value = yandex_vpc_address.addr.external_ipv4_address
}

resource "yandex_vpc_subnet" "subnet-1" {
  name           = "subnet1"
  zone           = "ru-central1-a"
  network_id     = yandex_vpc_network.network-1.id
  v4_cidr_blocks = ["192.168.10.0/24"]
}

output "external_ip_address_vm_1" {
  value = yandex_compute_instance.vm-1.network_interface.0.nat_ip_address
}

resource "yandex_dns_zone" "zone1" {
  name        = "footballbotzone"
  description = "..."

  zone             = "doweplayfootball.ru."
  public           = true
  private_networks = [yandex_vpc_network.network-1.id]
}

resource "yandex_dns_recordset" "webset1" {
  zone_id = yandex_dns_zone.zone1.id
  name    = "doweplayfootball.ru."
  type    = "A"
  ttl     = 200
  data    = [yandex_compute_instance.vm-1.network_interface.0.nat_ip_address]
}

resource "yandex_dns_recordset" "webset2" {
  zone_id = yandex_dns_zone.zone1.id
  name    = "www.doweplayfootball.ru."
  type    = "A"
  ttl     = 200
  data    = [yandex_compute_instance.vm-1.network_interface.0.nat_ip_address]
}

#resource "yandex_logging_group" "botlogs" {
#  name             = "botlogs"
#  folder_id        = "b1g6s7qrbeu4ndif5p99"
#  retention_period = "5h"
#}


#output "external_ip" {
#  value = yandex_compute_instance.instance-based-on-coi.network_interface.0.nat_ip_address
#}