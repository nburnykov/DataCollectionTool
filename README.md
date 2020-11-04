# network discovery

A lightweight tool to perform network discovery within defined IP range (for example 172.17.11.0/24). It uses a list of predefined log-pass pairs (it's supposed that we need to gather structured info about customer's network, so credentials are well known). Gathered data is parsed and stored in sqlite3 database. 
The overall process can be described in the next several steps:
1. Find an equipment within IP range with opened SSH and Telnet ports
2. Find an appropriate log-pass pair from the list
3. Using decision tree approach determine type and model/OS version of discovered system   
4. Using linked command set for devices of this model/OS version gather all the data and parse it using linked parsers
5. Store parsed data in database

#### TODO
1. requirements.txt