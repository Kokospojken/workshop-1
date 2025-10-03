import json

# read json file
data = json.load(open("network_devices.json", "r", encoding="utf-8"))

# crate variables for text raport
# and a new name to keep the details
report_details = "" 

# variabel for Executive Summary
summary_report = "" 

# variabel for all problem devices
potential_issue_devices = []

# variable for problem devices
problem_devices = [] 

# variable for a device counter
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

# variabel for company-name and last updated
company_name = data["company"]

# data processing and calculations

# loop through the location list 
for location in data["locations"]:
    site_name = location["site"]
    city_name = location["city"]
    
    # get stats for sites
    location_stats[site_name] = {
        "total": 0,
        "online": 0,
        "offline": 0,
        "warning": 0
    }

     # adding sites to the device list
    report_details += "\n" + site_name + "\n"
    report_details += "-" * (len(site_name) + 1) + "\n"

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
        
        # collect all vlans
        if "vlans" in device and isinstance(device["vlans"], list):
            for vlan_id in device["vlans"]:
                if isinstance(vlan_id, (int, str)):
                     vlan_set.add(int(vlan_id))

        # looking for offline and other warnings & update site stats
        location_stats[site_name]["total"] += 1
        if status == "online":
            location_stats[site_name]["online"] += 1
        elif status == "offline":
            location_stats[site_name]["offline"] += 1
            device_issues.append(f"Status: OFFLINE")
        elif status == "warning":
            location_stats[site_name]["warning"] += 1
            device_issues.append(f"Status: VARNING")            
         
        # short uptime, less than 30 days
        uptime = device.get("uptime_days")
        if uptime is not None and 0 < uptime < 30:
            device_issues.append(f"Låg upptid ({uptime} dagar)") 

        # add global view to problem list
        if device_issues:
            # Lägg till i problem enhetslista
            potential_issue_devices.append({
                "site": site_name,
                "hostname": hostname,
                "ip": ip,
                "issues": ", ".join(device_issues)
            })
            # add markings to the site overview
            report_details += f"  {hostname} (PROBLEMENHET: {status.upper()})\n"
        else:
            # adding hostname
            report_details += f"  {hostname}\n"

# generate EXECUTIVE SUMMARY on top of report
# main heading and data
summary_report += f"Företag: {company_name}\n"
summary_report += f"Senast uppdaterad: {data['last_updated']}\n"
summary_report += "=" * 50 + "\n"

summary_report += "\n### EXECUTIVE SUMMARY ###\n"
summary_report += "=" * 50 + "\n"

# count global totals
total_devices = sum(s['total'] for s in location_stats.values())
total_offline = sum(s['offline'] for s in location_stats.values())
total_warning = sum(s['warning'] for s in location_stats.values())
total_problems = len(potential_issue_devices)

# for main statistics
summary_report += f"Totalt antal hanterade enheter: {total_devices}\n"
summary_report += f"Enheter med kända problem (Åtgärd krävs): {total_problems} ({(total_problems / total_devices) * 100:.1f}% av flottan)\n"
summary_report += f"Status: OFFLINE: {total_offline}\n"
summary_report += f"Status: VARNING: {total_warning}\n"

# ports used on devices
if switches_counted > 0:
    port_utilization_percent = (used_ports / total_ports) * 100
    summary_report += f"Total portanvändning för switchar: {port_utilization_percent:.1f}% ({used_ports} av {total_ports})\n"

summary_report += "\n**KRITISKA ENHETER**\n"

if total_offline > 0:
    summary_report += f"🚨 {total_offline} enheter är **OFFLINE** och kräver omedelbar uppmärksamhet. Se problemöversikten.\n"
elif total_problems > 0:
    summary_report += f"⚠️ Nätverket har {total_problems} enheter med **VARNING** eller andra potentiella problem (låg upptid / hög portanvändning).\n"
else:
    summary_report += "✅ Nätverket är **utan problem**. Inga enheter är offline eller har varningar.\n"

summary_report += "\n[Se nedan för detaljerad analys per plats, problem och enhetstyp.]\n"


# generate a detailed report
full_report_output = summary_report

# site overview from loop
full_report_output += "\n### DETALJERAD LISTA - ALLA ENHETER PER PLATS ###\n"
full_report_output += "=" * 50 + "\n"
full_report_output += report_details


            
        



# units with potential problems
full_report_output += "\n\n" + "=" * 50 + "\n"
full_report_output += "### 1. ENHETER MED POTENTIELLA PROBLEM ###\n"
full_report_output += "=" * 50 + "\n"

if potential_issue_devices:
    full_report_output += "Totalt antal enheter med en eller flera problemindikationer: " + str(total_problems) + "\n\n"
    
    # table headings
    full_report_output += f"{'PLATS':<15} | {'HOSTNAME':<20} | {'IP-ADRESS':<15} | {'PROBLEMINDIKATIONER'}\n"
    full_report_output += f"{'-'*15}-+-{'-'*20}-+-{'-'*15}-+-{'-'*50}\n"

    for device in potential_issue_devices:
        full_report_output += (
            f"{device['site']:<15} | "
            f"{device['hostname']:<20} | "
            f"{device['ip']:<15} | "
            f"{device['issues']}\n"
        )
else:
    full_report_output += "Inga enheter rapporterar status 'offline', 'warning', låg upptid eller hög portanvändning.\n"
                    

# overview of divices per site
full_report_output += "\n\n" + "=" * 50 + "\n"
full_report_output += "### 2. ÖVERSIKT AV ENHETER PER SITE ###\n"
full_report_output += "=" * 50 + "\n"

full_report_output += f"{'PLATS':<15} | {'TOTALT':<6} | {'ONLINE':<6} | {'VARNING':<7} | {'OFFLINE'}\n"
full_report_output += f"{'-'*15}-+-{'-'*6}-+-{'-'*6}-+-{'-'*7}-+-{'-'*7}\n"

total_online_global = 0

for site, stats in location_stats.items():
    total_online_global += stats["online"]
    
    full_report_output += (
        f"{site:<15} | "
        f"{stats['total']:<6} | "
        f"{stats['online']:<6} | "
        f"{stats['warning']:<7} | "
        f"{stats['offline']}\n"
    )

full_report_output += f"{'='*15}-+-{('='*6)*3}-+-{('='*7)}\n"
full_report_output += (
    f"{'SUMMA':<15} | "
    f"{total_devices:<6} | "
    f"{total_online_global:<6} | "
    f"{total_warning:<7} | "
    f"{total_offline}\n"
)


# list all the vlans in the network
full_report_output += "\n\n" + "=" * 50 + "\n"
full_report_output += "### 3. ÖVERSIKT - ALLA UNIKA VLAN-ID:N I NÄTVERKET ###\n"
full_report_output += "=" * 50 + "\n"

if vlan_set:
    # sort vlans into list
    sorted_vlans = sorted(list(vlan_set))
    
    full_report_output += f"Totalt antal unika VLANs: {len(sorted_vlans)}\n\n"
    
    full_report_output += "Använda VLAN-ID:n (sorterade):\n"
    
    # split list for better visuality
    vlan_output = ""
    for i, vlan_id in enumerate(sorted_vlans):
        vlan_output += str(vlan_id)
        if i < len(sorted_vlans) - 1:
            vlan_output += ", "
        if (i + 1) % 10 == 0:
            vlan_output += "\n"
            
    full_report_output += vlan_output.strip() + "\n"
    
else:
    full_report_output += "Ingen VLAN-information hittades i enhetsdatan.\n"
   

# total usage of ports in switches
full_report_output += "\n\n" + "=" * 50 + "\n"
full_report_output += "### 4. TOTAL PORTANVÄNDNING FÖR SWITCHAR ###\n"
full_report_output += "=" * 50 + "\n"

if switches_counted > 0:
    full_report_output += f"Antal switchar inkluderade: {switches_counted}\n\n"
    full_report_output += f"Totalt antal portar: {total_ports}\n"
    full_report_output += f"Antal använda portar: {used_ports}\n"
    full_report_output += f"Total portanvändning: {port_utilization_percent:.1f}%\n"
else:
    full_report_output += "Inga switchar med portinformation hittades för att beräkna användningen.\n"   


# total units per type
full_report_output += "\n\n" + "=" * 50 + "\n"
full_report_output += "### 5. TOTALT ANTAL ENHETER PER TYP ###\n"
full_report_output += "=" * 50 + "\n"

if device_type_counts:
    # sorted counts for better visuality
    sorted_counts = sorted(device_type_counts.items(), key=lambda item: item[1], reverse=True)
    
    full_report_output += f"Totalt antal hanterade nätverksenheter: {total_devices}\n\n"
    
    full_report_output += f"{'ENHETSTYP':<20} | {'ANTAL'}\n"
    full_report_output += f"{'-'*20}-+-{'-'*5}\n"

    for device_type, count in sorted_counts:
        full_report_output += f"{device_type.replace('_', ' ').title():<20} | {count}\n"
else:
    full_report_output += "Kunde inte räkna några enhetstyper.\n" 


# write the report to text file
with open('report.txt', 'w', encoding='utf-8') as f:
    f.write(full_report_output)