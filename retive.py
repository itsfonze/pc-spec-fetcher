import platform
import psutil
import socket
import smtplib
import wmi
import GPUtil
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

    # GPU
    gpus = GPUtil.getGPUs()
    if gpus:
        for idx, gpu in enumerate(gpus):
            info[f"GPU {idx + 1} Name"] = gpu.name
            info[f"GPU {idx + 1} VRAM"] = f"{round(gpu.memoryTotal)} MB"
    else:
        info["GPU"] = "No discrete GPU detected"

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
