# CMDB Creator
## SecureCRT script for for generating a .csv containing a Cisco Catalyst switch's inventory data. 

Tested on SecureCRT 9.5.1. and Python 3.12.3

Compatible with any Cisco Catalyst switch. 

# Functions
 - Creates a folder if not present.
  
 - Prompts adhere to the Cisco CLI syntax.

 - Adds the provided interface IP to the .csv

 - Adds the IP address of the connected session. (NAT address) 

 - Duplicates will be deleted. 

# Usage
1. Change the folder location (line 168) if desired.
1. Log into device and run script from SecureCRT.
2. You will be prompted for the management interface. (You'll have 3 attempts for input and you can cancel to skip adding MGMT IP to .csv)
3. Done. 
