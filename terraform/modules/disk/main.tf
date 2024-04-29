#resource "yandex_compute_disk" "main_storage" {
#  name     = "main_storage"
#  type     = "network-hdd"
#  zone     = "ru-central1-a"
#  size = 20
#
#  labels = {
#    environment = "test"
#  }
#}
#
#output "disk_id" {
#  value = yandex_compute_disk.main_storage.id
#}