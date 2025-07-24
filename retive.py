import platform
import psutil
import socket
import smtplib
import wmi
import winreg
from email.message import EmailMessage

# ✅ Accurate CPU name via registry
def get_cpu_name():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        cpu_name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
        return cpu_name
    except:
        return "Unknown CPU"

# ✅ Better storage info using WMI
def get_drive_info():
    c = wmi.WMI()
    drives = c.Win32_DiskDrive()
    info = []
    for drive in drives:
        model = drive.Model.strip()
        size = round(int(drive.Size) / (1024**3), 2)
        interface_type = drive.InterfaceType.strip()
        media_type = getattr(drive, 'MediaType', 'Unknown')
        info.append(f"{model} | {interface_type} | {media_type} | {size} GB")
    return info

# ✅ New GPU info using WMI (discrete vs integrated)
def get_gpu_info():
    c = wmi.WMI()
    gpus = c.Win32_VideoController()
    gpu_info = []
    for gpu in gpus:
        name = gpu.Name.strip()
        vendor = gpu.AdapterCompatibility.strip() if gpu.AdapterCompatibility else "Unknown"
        vram = int(gpu.AdapterRAM) / (1024 ** 2) if gpu.AdapterRAM else 0
        is_discrete = vram > 512  # Simple threshold to separate discrete vs integrated
        gpu_info.append({
            "Name": name,
            "Vendor": vendor,
            "VRAM_MB": round(vram),
            "Type": "Discrete" if is_discrete else "Integrated"
        })
    return gpu_info

# 🔍 Main system info collector
def get_system_info():
    c = wmi.WMI()
    info = {}

    # OS
    info["OS"] = f"{platform.system()} {platform.release()}"

    # Hostname and IP
    info["Hostname"] = socket.gethostname()
    try:
        info["IP Address"] = socket.gethostbyname(socket.gethostname())
    except:
        info["IP Address"] = "Unavailable"

    # CPU
    info["CPU"] = get_cpu_name()
    info["Cores (Logical)"] = psutil.cpu_count()
    info["Cores (Physical)"] = psutil.cpu_count(logical=False)

    # RAM
    info["RAM"] = f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB"

    # GPU Info
    gpus = get_gpu_info()
    if gpus:
        for idx, gpu in enumerate(gpus):
            label = f"GPU {idx + 1} ({gpu['Type']})"
            info[f"{label} Name"] = gpu["Name"]
            info[f"{label} Vendor"] = gpu["Vendor"]
            info[f"{label} VRAM"] = f"{gpu['VRAM_MB']} MB"
    else:
        info["GPU"] = "No GPU detected"

    # BIOS + Motherboard
    try:
        for bios in c.Win32_BIOS():
            info["BIOS Vendor"] = bios.Manufacturer.strip()
            info["BIOS Version"] = bios.SMBIOSBIOSVersion.strip()
        for board in c.Win32_BaseBoard():
            info["Motherboard"] = board.Product.strip()
    except:
        info["BIOS"] = "Unavailable"

    # Storage drives
    drives = get_drive_info()
    for i, disk in enumerate(drives):
        info[f"Disk {i+1} Info"] = disk

    return info

# 📧 Email sender
def send_email(info):
    msg = EmailMessage()
    msg.set_content("\n".join([f"{k}: {v}" for k, v in info.items()]))
    msg['Subject'] = '⚙️ Full System Info Report'
    msg['From'] = 'johan.manojp@gmail.com'
    msg['To'] = 'johan.manojp@gmail.com'

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('johan.manojp@gmail.com', 'vccb xjpv fkvd eink')
            smtp.send_message(msg)
        print("✅ Email sent successfully.")
    except Exception as e:
        print("❌ Failed to send email:", e)

# 🧠 Main execution
if __name__ == "__main__":
    sysinfo = get_system_info()
    send_email(sysinfo)
