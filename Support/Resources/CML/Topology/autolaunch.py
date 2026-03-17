#!/usr/bin/env python3

from virl2_client import ClientLibrary

host = "https://localhost" 
cl = ClientLibrary(f"{host}", "admin", "C1sco12345#", ssl_verify=False)

# Start the first lab
lab1 = cl.join_existing_lab("eb4a2a2a-539c-48f0-852a-2e729d515e4f") 
lab1.start(wait=False)

# Wait for the first lab to converge and get its node
lab1.wait_until_lab_converged()
result1 = lab1.get_node_by_label("c9000v-2")
print(f"First Lab Node: {result1}")

# Start the second lab
lab2 = cl.join_existing_lab("3ffc8381-c612-4fa1-94ba-ece9c0d8cda7") 
lab2.start(wait=False)

# Wait for the second lab to converge and get its node
lab2.wait_until_lab_converged()
result2 = lab2.get_node_by_label("leaf2")
print(f"Second Lab Node: {result2}")
