@echo off
FOR /f "tokens=*" %%i IN ('docker images --filter "dangling=true" --format "{{.ID}}"') DO docker rmi %%i
docker build -t crfcalc:latest .
docker run -d -p 4000:80 crfcalc
@echo on
