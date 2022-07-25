# Web Based cRF Calculator

Simple web based cRF calculator based on NHSBT ODT 10,000 donor datasets (2006/2016), replacing the slow Excel VBA based calculator. 

Please note This only calculates cRF, no other functions such as those in the latest (2016 version) [hla-mm-and-crf.xlsb](https://www.odt.nhs.uk/transplantation/tools-policies-and-guidance/calculators/). 

## Docker image from Dockerfile
```c
/* Building Docker Image */
docker build -t crfcalc:latest .

/* Running Docker container mapping port 80 to external port 4000 */
docker run -d -p 4000:80 --restart always crfcalc
```

## Docker image from DockerHub

```c
/* Pulling the image */
docker pull machnine/crfcalc

/* Running Docker container mapping port 80 to external port 4000 */
docker run -d -p 4000:80 --restart always crfcalc
```

