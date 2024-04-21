terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
  backend "s3" {
    endpoint = "https://storage.yandexcloud.net"
    bucket = "dwpf-storage-terraform"
    region = "ru-central1"
    key    = "states/state.tfstate"

    skip_region_validation      = true
    skip_credentials_validation = true
#    skip_requesting_account_id  = true # Необходимая опция Terraform для версии 1.6.1 и старше.
#    skip_s3_checksum            = true # Необходимая опция при описании бэкенда для Terraform версии 1.6.3 и старше.

  }
  required_version = ">= 0.13"
}

provider "yandex" {
  zone = "ru-central1-a"
#  service_account_key_file = "${var.key}"
}

data "yandex_compute_image" "container-optimized-image" {
  family = "container-optimized-image"
}


#variable "key" { type= string }

#resource "yandex_compute_disk" "boot-disk-1" {
#  name     = "boot-disk"
#  type     = "network-hdd"
#  zone     = "ru-central1-a"
#  size     = "20"
##  image_id = "fd87va5cc00gaq2f5qfb"
#}


resource "yandex_compute_instance" "vm-1" {
  name = "fb"

  resources {
    cores  = 2
    memory = 2
  }

#  boot_disk {
#    disk_id = yandex_compute_disk.boot-disk-1.id
#  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.container-optimized-image.id
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.subnet-1.id
    nat       = true
  }

#  metadata = {
#    ssh-keys = "ubuntu:${file("~/.ssh/terrakey.pub")}"
#  }

  metadata = {
    docker-container-declaration = file("${path.module}/declaration.yaml")
    user-data = file("${path.module}/cloud_config.yaml")
  }
}

resource "yandex_vpc_network" "network-1" {
  name = "network1"
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



#output "external_ip" {
#  value = yandex_compute_instance.instance-based-on-coi.network_interface.0.nat_ip_address
#}