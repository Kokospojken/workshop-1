import json

# read json file
data = json.load(open("network_devices.json", "r", encoding="utf-8"))

# crate variable for text raport
report = ""

# list for all units with problem status (offline/warning)
problem_devices = []

# device counter
device_type_counts = {}

# company-name and last updated
company_name = data["company"]
report += f"Företag: {company_name}\n"
report += f"Senast uppdaterad: {data['last_updated']}\n"
report += "=" * 50 + "\n"

# All units on site
report += "\n### ÖVERSIKT - ALLA ENHETER PER PLATS ###\n"
report += "=" * 50 + "\n"

# loop through the location list 
for location in data["locations"]:
    # add the site/'name' of the location to the report
    report += "\n" + location["site"] + "\n"
    report += "-" * (len(location["site"]) + 1) + "\n"

    # add a list of the host names of the devices 
    # on the location to the report
    for device in location["devices"]:
        
        # device counter
        device_type = device.get("type", "unknown_type")
        device_type_counts[device_type] = device_type_counts.get(device_type, 0) + 1

        # device status is "offline" or "warning"
        if device["status"].lower() in ["offline", "warning"]:
            problem_devices.append({
                "site": location["site"],
                "hostname": device["hostname"],
                "status": device["status"],
            })
            # add hostname and status
            report += f"  {device['hostname']} (Status: {device['status'].upper()})\n"
        else:
            # add hostname
            report += f"  {device['hostname']}\n"


# problem units

report += "\n\n" + "=" * 50 + "\n"
report += "### VARNINGAR OCH PROBLEMSTATUS (OFFLINE/WARNING) ###\n"
report += "=" * 50 + "\n"

if problem_devices:
    report += "Totalt antal enheter med problem: " + str(len(problem_devices)) + "\n\n"
    
    # table header
    report += f"{'PLATS':<15} | {'HOSTNAME':<20} |  {'STATUS'}\n"
    report += f"{'-'*15}-+-{'-'*20}-+-{'-'*8}\n"

    for device in problem_devices:
        report += (
            f"{device['site']:<15} | "
            f"{device['hostname']:<20} | "
            f"{device['status'].upper()}\n"
        )
else:
    report += "Inga enheter rapporterar status 'offline' eller 'warning'. Allt är online! :)\n"


# total devices and type

report += "\n\n" + "=" * 50 + "\n"
report += "### TOTALT ANTAL ENHETER PER TYP ###\n"
report += "=" * 50 + "\n"

if device_type_counts:
    # sorted counts for better visuality
    sorted_counts = sorted(device_type_counts.items(), key=lambda item: item[1], reverse=True)
    
    total_devices = sum(device_type_counts.values())
    report += f"Totalt antal hanterade nätverksenheter: {total_devices}\n\n"
    
    report += f"{'ENHETSTYP':<20} | {'ANTAL'}\n"
    report += f"{'-'*20}-+-{'-'*5}\n"

    for device_type, count in sorted_counts:
        report += f"{device_type.replace('_', ' ').title():<20} | {count}\n"
else:
    report += "Kunde inte räkna några enhetstyper.\n" 


# write the report to text file
with open('report.txt', 'w', encoding='utf-8') as f:
    f.write(report)

    print (report)