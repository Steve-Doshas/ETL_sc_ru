#!/bin/bash                                                                                                  
docker container run --rm --name service_sc_ru -v "/media/ProjetBI":/app/data/ -v LOG:/app/log etl_sc_ru:v1 
