terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
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

resource "yandex_dns_recordset" "webset1" {
  zone_id = dns8ljpdc8tj9l3au8pe
  name    = "doweplayfootball.ru."
  type    = "A"
  ttl     = 200
  data    = [yandex_compute_instance.vm-1.network_interface.0.nat_ip_address]
}

resource "yandex_dns_recordset" "webset2" {
  zone_id = dns8ljpdc8tj9l3au8pe
  name    = "www.doweplayfootball.ru."
  type    = "A"
  ttl     = 200
  data    = [yandex_compute_instance.vm-1.network_interface.0.nat_ip_address]
}



#output "external_ip" {
#  value = yandex_compute_instance.instance-based-on-coi.network_interface.0.nat_ip_address
#}