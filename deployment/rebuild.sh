docker image rm audit_log:latest
docker image rm storage:latest
docker image rm processing:latest
docker image rm receiver:latest

docker build -t audit_log:latest ~/MicroServices/audit_log
docker build -t storage:latest ~/MicroServices/storage
docker build -t processing:latest ~/MicroServices/processing
docker build -t receiver:latest ~/MicroServices/receiver

