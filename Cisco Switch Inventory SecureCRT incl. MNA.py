#$language = "python"
#$interface = "1.0"

## Instellingen naar behoren aanpassen !!
debug = 0                   # 1 (Ja) of 0 (Nee) opgeven

## Modules importeren
import os.path, re, time
from os.path import expanduser

## Aanmaken van entiteiten
inventory = []
inventoryLine = []
cleaninventory = []

xlocation = ""

objTab = crt.GetScriptTab()
objTab.Screen.Synchronous = True
objTab.Screen.IgnoreEscape = True

#### Functies ####

# Hostname halen
def pickuphost():
    szPrompt = "#"
    szCommandHostname = "show run | i hostname|switchname"
    objTab.Screen.Send("\r\n terminal length 0")
    objTab.Screen.Send("\r\n" + szCommandHostname + "\r\n")
    objTab.Screen.WaitForString(szCommandHostname)
    szResultHostname = objTab.Screen.ReadString(szPrompt)
    szResultHostname = szResultHostname.split()
    xHostname = szResultHostname[1]
    return xHostname

# Inventory halen
def pickupinv():
    szPrompt = xHostname + "#"
    szCommandInventory = "show inventory"
    objTab.Screen.Send("\r\n" + szCommandInventory + "\r\n")
    objTab.Screen.WaitForString(szCommandInventory)
    szResultInventory = objTab.Screen.ReadString(szPrompt)
    szResultInventory = filterinventory(szResultInventory)
    xInventory = szResultInventory
    return xInventory

# Management IP halen
def pickupint(x):
    szPrompt = xHostname + "#"
    szInterface = "sh ip int br " + x
    objTab.Screen.Send("\r\n" + szInterface + "\r\n")
    objTab.Screen.WaitForString(szInterface)
    szResultInterface = objTab.Screen.ReadString(szPrompt)
    xInterface = szResultInterface
    return xInterface

# NAT IP halen
def pickupnat():
    xNat = crt.Session.RemoteAddress
    return xNat

# Tekst filtering Inventory
def filterinventory(x):
    x = x.replace("\r\r\n","")
    x = x.replace("\r\n","")
    x = x.replace('NAME: ' , ', ' )
    x = x.replace("PID: ", ", ")
    x = x.replace("DESCR: ","")
    x = x.replace("VID","")
    x = x.replace("SN: ","")
    x = x.replace('"', '')
    x = x.replace("Cisco Systems, Inc.", "Cisco Systems Inc.")
    x = x.replace("(SFP+)," , "(SFP+)")
    x = x.replace("power supply,", "power supply")
    x = x.replace("Power supply,", "power supply")
    x = x.replace("Processor 3, 400G, XL Scale", "Processor 3 400G XL Scale")
    x = x.replace("Modular FAN, PSU and IM", "Modular FAN PSU and IM")
    x = x.split(",")
    return x

# Duplicates verwijderen
def remove_duplicates(x):
    result = []
    skip_indices = set()

    for i in range(len(x)):
        if i in skip_indices:
            # Eerste in set opnemen
            continue
        for j in range(i + 1, len(x)):
            if x[j][4] == x[i][4] and x[i][4] != '':
                # En tweede verwijderen
                skip_indices.add(j)
                break
        result.append(x[i])
    return result

# Hostname, inventory en NAT IP halen
xHostname = pickuphost()
xInventory = pickupinv()
xNat = pickupnat()


# Management interface halen
szCommandInterface = crt.Dialog.Prompt("Enter the management interface", "Provide management interface", "Lo0")

for loop in range(1): 
    if szCommandInterface == "":
        xInterface = ""
        break
    elif szCommandInterface != "":
        interface = pickupint(szCommandInterface)
        xInterface = interface.split()
        trycounter = 1
        trycounterstr = str(trycounter)
        for i in range(4):
            if szCommandInterface == "":
                xInterface = ""
                break
            elif xInterface[0] == "Interface":
                break
            elif trycounter >= 4:
                crt.Dialog.MessageBox("#### wompwomp ####")
                #trycounter = 5
                xInterface = ""
                break
            elif xInterface[0] == "^":
                    szCommandInterface = crt.Dialog.Prompt("Enter the management interface", "Error, try " + trycounterstr + " of 3", "insert")
                    pickupint(szCommandInterface)
                    xInterface = interface.split()
                    trycounter += 1
                    trycounterstr = str(trycounter)

# Adres halen
szCommandAddress = crt.Dialog.Prompt("Enter the address", "Provide location address", "Straat, Postcode, Plaats")

for loop in range(1): 
    if szCommandAddress == "" or szCommandAddress == "Straat, Postcode, Plaats":
        xlocation = ""
        break
    elif szCommandAddress != "":
        xlocation = szCommandAddress

# Verificatie xInvertface
if xInterface == "" or xInterface[0] == "^":
    xInterface = False
else:
    pass

## Loop door inventory heen
for line in xInventory:
    if line != "":
        if len(inventoryLine)>4:
            inventory.append(inventoryLine)
            inventoryLine = []
            inventoryLine.append(" ".join(line.split()))
        else:
            inventoryLine.append(" ".join(line.split()))

inventory.append(inventoryLine)

# Duplicates wegknallen
cleaninventory = remove_duplicates(inventory)

# Bestanden voorbereiden
moment = time.strftime("%Y%m%d") + "." + time.strftime("%H%M%S")
opslagdir = "D:\Scripts\Python\CMDBcreator\Inventory\\"

if not os.path.exists(opslagdir):
    os.makedirs(opslagdir)

# Debug file wegschrijven wanneer nodig
if debug == 1:
    debugfile = opslagdir + "Debug." + moment + "." + xHostname + ".txt"
    file = open(debugfile, 'w')

    file.write(xHostname)
    file.write('\n')
    file.write(repr(xInventory))
    file.write('\n')
    file.write(repr(cleaninventory))

    file.write('\n\n')
    file.write("===== ===== ===== Na bewerking ===== ====== =====\n")

    for line in xInventory:
        file.write(line)
        file.write('\n')

    file.write('\n')
    file.close()

# Formulier wegschrijven
opslagfile = opslagdir + xHostname + "." + moment + ".csv"
file = open(opslagfile, 'w')

file.write('"Item status",')
file.write('"Serienummer",')
file.write('"Product SC",')
file.write('"Product description",')
file.write('"Adres",')
file.write('"Hostname",')
file.write('"IP Adres",')
file.write('"NAT adres",')
file.write('\n')

hostnamecounter = 0
interfacecounter = 0
natcounter = 0

for line in cleaninventory:
    if len(line) >= 4:
        adres = xlocation

        file.write('"IN USE",')                 ## Item Status
        file.write('"' + line[4] + '",')        ## Serienummer
        file.write('"' + line[2] + '",')        ## Product SC
        file.write('"' + line[1] + '",')        ## Product description
        file.write('"' + adres + '",')          ## Gebouw/adres

        if hostnamecounter == 0:
            file.write('"' + xHostname + '",')  ## Hostname
        elif hostnamecounter > 0:
            hostname = xHostname + '_' + str(hostnamecounter).zfill(2)
            file.write('"' + hostname + '",')   ## Hostname + nummer

        if interfacecounter == 0:               ## Management IP
            if not xInterface:
                file.write('"",') 
                pass
            else:
                file.write('"' + xInterface[7] + '",') 
        else: 
            pass

        if natcounter == 0:                     ## NAT IP
            file.write('"' + xNat + '",')
        else: 
            file.write('"",')
        file.write('\n')

        # Counters
        hostnamecounter += 1
        interfacecounter += 1
        natcounter += 1

file.close()
