import json

# read json file
data = json.load(open("network_devices.json", "r", encoding="utf-8"))

# crate variables for text raport
report = ""

# variabel for all problem devices
potential_issue_devices = []

# listvariabel for all units with problem status (offline/warning)
problem_devices = []

# variabel uptime counter
short_uptime_devices = []

# variabel device counter
device_type_counts = {}

# variabel for port counter for switches
total_ports = 0
used_ports = 0
switches_counted = 0

# variabel to collect all unique vlans
vlan_set = set()

# variables for statics on every site
location_stats = {}

# company-name and last updated
company_name = data["company"]
report += f"Företag: {company_name}\n"
report += f"Senast uppdaterad: {data['last_updated']}\n"
report += "=" * 50 + "\n"

# All units on site
report += "\n### ÖVERSIKT - ALLA ENHETER PER PLATS (ev. problem) ###\n"
report += "=" * 50 + "\n"

# loop through the location list 
for location in data["locations"]:
    site_name = location["site"]
    
    # get stats for sites
    location_stats[site_name] = {
        "total": 0,
        "online": 0,
        "offline": 0,
        "warning": 0
    }
    
    # add the site/'name' of the location to the report
    report += "\n" + site_name + "\n"
    report += "-" * (len(site_name) + 1) + "\n"

    # add a list of the host names of the devices 
    # on the location to the report
    for device in location["devices"]:

 # variabel for loops
        hostname = device["hostname"]
        device_type = device.get("type", "unknown_type")
        status = device["status"].lower()
        ip = device.get("ip_address", "N/A")
        
        # variabel to collect all device issues
        device_issues = []

      # count device types
        device_type_counts[device_type] = device_type_counts.get(device_type, 0) + 1

        # check for high port use
        if device_type == "switch" and "ports" in device:
            total = device["ports"].get("total", 0)
            used = device["ports"].get("used", 0)
            
            # global stats
            total_ports += total
            used_ports += used
            switches_counted += 1 

            # check for high usage
            if total > 0 and (used / total) > 0.8:
                utilization = (used / total) * 100
                device_issues.append(f"Hög portanvändning ({utilization:.1f}%)")         
        
        # device counter
        device_type = device.get("type", "unknown_type")
        device_type_counts[device_type] = device_type_counts.get(device_type, 0) + 1

       # update the numbers of used ports on switch
        if device_type == "switch" and "ports" in device:
            total_ports += device["ports"].get("total", 0)
            used_ports += device["ports"].get("used", 0)
            switches_counted += 1 

            # collect all vlans
        # check for vlan ids
        if "vlans" in device and isinstance(device["vlans"], list):
            # add all vlan to the set
            for vlan_id in device["vlans"]:
                if isinstance(vlan_id, (int, str)):
                     vlan_set.add(int(vlan_id))

          # looking for offline and other warnings
        location_stats[site_name]["total"] += 1
        if status == "online":
            location_stats[site_name]["online"] += 1
        elif status == "offline":
            location_stats[site_name]["offline"] += 1
            device_issues.append(f"Status: OFFLINE")
        elif status == "warning":
            location_stats[site_name]["warning"] += 1
            device_issues.append(f"Status: VARNING")            

         # update site stats
        status = device["status"].lower()
        location_stats[site_name]["total"] += 1
        
        if status == "online":
            location_stats[site_name]["online"] += 1
        elif status == "offline":
            location_stats[site_name]["offline"] += 1
        elif status == "warning":
            location_stats[site_name]["warning"] += 1
          
         
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

     # short uptime, less than 30 days
        uptime = device.get("uptime_days")
        if uptime is not None and 0 < uptime < 30:
            short_uptime_devices.append({
                "site": location["site"],
                "hostname": device["hostname"],
                "uptime": uptime,
            }) 

    # add global view to problem list
        if device_issues:
            # add global view
            report += f"  {hostname} (PROBLEMENHET: {status.upper()})\n"
            
            # add to problem device list
            potential_issue_devices.append({
                "site": site_name,
                "hostname": hostname,
                "ip": ip,
                "issues": ", ".join(device_issues)
            })
        else:
            # add hostname
            report += f"  {hostname}\n"

report += "\n\n" + "=" * 50 + "\n"
report += "### ENHETER MED POTENTIELLA PROBLEM ###\n"
report += "=" * 50 + "\n"

if potential_issue_devices:
    report += "Totalt antal enheter med en eller flera problemindikationer: " + str(len(potential_issue_devices)) + "\n\n"
    
    # table headings
    report += f"{'PLATS':<15} | {'HOSTNAME':<20} | {'IP-ADRESS':<15} | {'PROBLEMINDIKATIONER'}\n"
    report += f"{'-'*15}-+-{'-'*20}-+-{'-'*15}-+-{'-'*40}\n"

    for device in potential_issue_devices:
        report += (
            f"{device['site']:<15} | "
            f"{device['hostname']:<20} | "
            f"{device['ip']:<15} | "
            f"{device['issues']}\n"
        )
else:
    report += "Inga enheter rapporterar status 'offline', 'warning', låg upptid eller hög portanvändning .\n"
                    

# overview units per site

report += "\n\n" + "=" * 55 + "\n"
report += "### ÖVERSIKT AV ENHETER PER SITE ###\n"
report += "=" * 55 + "\n"

report += f"{'PLATS':<15} | {'TOTALT':<6} | {'ONLINE':<6} | {'VARNING':<7} | {'OFFLINE'}\n"
report += f"{'-'*15}-+-{'-'*6}-+-{'-'*6}-+-{'-'*7}-+-{'-'*7}\n"

total_online_global = 0
total_offline_global = 0
total_warning_global = 0

for site, stats in location_stats.items():
    total_online_global += stats["online"]
    total_offline_global += stats["offline"]
    total_warning_global += stats["warning"]
    
    report += (
        f"{site:<15} | "
        f"{stats['total']:<6} | "
        f"{stats['online']:<6} | "
        f"{stats['warning']:<7} | "
        f"{stats['offline']}\n"
    )

report += f"{'='*15}-+-{('='*6)*3}-+-{('='*7)}\n"
report += (
    f"{'SUMMA':<15} | "
    f"{sum(s['total'] for s in location_stats.values()):<6} | "
    f"{total_online_global:<6} | "
    f"{total_warning_global:<7} | "
    f"{total_offline_global}\n"
)



# problem units report

report += "\n\n" + "=" * 55 + "\n"
report += "### VARNINGAR OCH PROBLEMSTATUS (OFFLINE/WARNING) ###\n"
report += "=" * 55 + "\n"

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


    # short uptime less than 30 days

report += "\n\n" + "=" * 50 + "\n"
report += "### ENHETER MED KORT UPPTID (< 30 DAGAR) ###\n"
report += "=" * 50 + "\n"

if short_uptime_devices:
    report += "Totalt antal enheter med kort upptid: " + str(len(short_uptime_devices)) + "\n\n"
    
    # table header
    report += f"{'PLATS':<15} | {'HOSTNAME':<20} | {'UPTIME(Dagar)'}\n"
    report += f"{'-'*15}-+-{'-'*20}-+-{'-'*15}-+-{'-'*15}\n"

    for device in short_uptime_devices:
        report += (
            f"{device['site']:<15} | "
            f"{device['hostname']:<20} | "
            f"{device['uptime']:<15}\n"
        )
else:
    report += "Inga enheter har kortare upptid än 30 dagar.\n"

 # report for all vlans

report += "\n\n" + "=" * 50 + "\n"
report += "### ÖVERSIKT - ALLA UNIKA VLAN-ID:N I NÄTVERKET ###\n"
report += "=" * 50 + "\n"

if vlan_set:
    # sort vlans into list
    sorted_vlans = sorted(list(vlan_set))
    
    report += f"Totalt antal unika VLANs: {len(sorted_vlans)}\n\n"
    
    # format the list like csv
    report += "Använda VLAN-ID:n (sorterade):\n"
    
    # split list for better visuality
    vlan_output = ""
    for i, vlan_id in enumerate(sorted_vlans):
        vlan_output += str(vlan_id)
        if i < len(sorted_vlans) - 1:
            vlan_output += ", "
        if (i + 1) % 10 == 0:
            vlan_output += "\n"
            
    report += vlan_output.strip() + "\n"
    
else:
    report += "Ingen VLAN-information hittades i enhetsdatan.\n"
   

 # total port used on every switch
report += "\n\n" + "=" * 50 + "\n"
report += "### TOTAL PORTANVÄNDNING FÖR SWITCHAR ###\n"
report += "=" * 50 + "\n"

if switches_counted > 0:
    # count %
    port_utilization_percent = (used_ports / total_ports) * 100
    
    report += f"Antal switchar inkluderade: {switches_counted}\n\n"
    report += f"Totalt antal portar: {total_ports}\n"
    report += f"Antal använda portar: {used_ports}\n"
    # use :.1f for only one decimal
    report += f"Total portanvändning: {port_utilization_percent:.1f}%\n"
else:
    report += "Inga switchar med portinformation hittades för att beräkna användningen.\n"   


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

   