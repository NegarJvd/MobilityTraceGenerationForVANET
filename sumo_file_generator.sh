#!/bin/bash

# Check if the user provided enough arguments (insertion_density)
if [ $# -lt 1 ]; then
    echo -e "\e[31mUsage: $0 <insertion_density>\e[0m"
    exit 1
fi

# Get the insertion_density
insertion_density=$1

# Ensure the insertion_density is a positive integer
if ! [[ "$insertion_density" =~ ^[0-9]+$ ]]; then
    echo -e "\e[31mError: <insertion_density> must be a positive integer.\e[0m"
    exit 1
fi

generated_file_name="mobility_$insertion_density.tcl"

cd /home/negar/workspace/ns-allinone-3.38/ns-3.38/metalearn_vanet_clustering_2023_results/sumo
python /usr/share/sumo/tools/randomTrips.py -n map.net.xml -r map.rou.xml -b 0 -e 600 --insertion-density $insertion_density
sumo -c config.sumocfg --fcd-output map.fcd.xml
python /usr/share/sumo/tools/traceExporter.py -i map.fcd.xml -n map.net.xml --ns2mobility-output $generated_file_name

python3 plot.py

chmod u+w "$generated_file_name"
mv "$generated_file_name" /home/negar/workspace/ns-allinone-3.38/ns-3.38/scratch/metalearn_vanet_clustering_2023/

echo -e "\e[32mSumo file generated for $insertion_density\e[0m"