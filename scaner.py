import requests
import json
import socket
import uuid
from tkinter import messagebox, filedialog
import tkinter as tk
import psutil


def get_mac():
    # Barcha tarmoq interfeyslarini olish
    interfaces = psutil.net_if_addrs()

    # Eng birinchi non-lokal tarmoq interfeysini tanlash
    for interface in interfaces.keys():
        if interface != 'lo':
            for addr in interfaces[interface]:
                if addr.family == psutil.AF_LINK:
                    return addr.address
    return None


def get_location_info(ip_address, start_port, end_port):
    try:
        # Ma'lumotlarni olish
        response = requests.get(f"https://ipinfo.io/{ip_address}/json")
        if response.status_code == 200:
            data = response.json()

            # Mamlakatni qaytarish
            country = data.get('country', 'Noma`lum')
            city = data.get('city', 'Noma`lum')
            region = data.get('region', 'Noma`lum')

            # Ochiq portlarni qaytarish
            open_ports = []
            for port in range(start_port, end_port + 1):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        s.settimeout(0.1)
                        result = s.connect_ex((ip_address, port))
                        if result == 0:
                            open_ports.append(port)
                    except:
                        pass

            # MAC manzilini olish
            mac = get_mac()

            # IP manzilini DNS orqali domen nomiga aylantirish
            domain = ip_to_domain(ip_address)

            return country, city, region, open_ports, mac, domain
        else:
            messagebox.showerror("Xatolik", f"HTTP xato: {response.status_code}")
            return None, None, None, [], None, None
    except Exception as e:
        messagebox.showerror("Xatolik", str(e))
        return None, None, None, [], None, None


# Qolgan kodni o'zgartirishni davom ettirishingiz mumkin

def get_provider_info(ip_address):
    try:
        # Ma'lumotlarni olish
        response = requests.get(f"https://ipinfo.io/{ip_address}/json")
        if response.status_code == 200:
            data = response.json()

            # Pravayder ma'lumotlarini qaytarish
            provider = data.get('org', 'Noma`lum')

            return provider
        else:
            messagebox.showerror("Xatolik", f"HTTP xato: {response.status_code}")
            return None
    except Exception as e:
        messagebox.showerror("Xatolik", str(e))
        return None

def ip_to_domain(ip_address):
    try:
        # IP manzilini DNS orqali domen nomiga aylantirish
        domain = socket.gethostbyaddr(ip_address)[0]
        return domain
    except Exception as e:
        print("Xatolik:", e)
        return None

def save_scan_results(ip_address, country, city, region, open_ports, mac, domain, provider):
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(f"IP manzili: {ip_address}\n")
            file.write(f"Mamlakat: {country}\n")
            file.write(f"Shahar: {city}\n")
            file.write(f"Viloyat: {region}\n")
            file.write("Ochiq portlar:\n")
            for port in open_ports:
                file.write(f"{port}\n")
            file.write(f"MAC manzili: {mac}\n")
            file.write(f"Domen nomi: {domain}\n")
            file.write(f"Pravayder: {provider}\n")
        messagebox.showinfo("Oxirgi qadam", f"Skanerlash natijalari faylga saqlandi: {file_path}")


# start_scan funktsiyasini avval o'zgartiramiz
def start_scan():
    ip_address = entry_ip.get()
    port_input = entry_port.get()  # Portlarni olish
    ports = [int(port.strip()) for port in port_input.split(',')]  # Vergul orqali ajratilgan portlarni ro'yxatga olish
    
    country, city, region, open_ports, mac, domain = get_location_info(ip_address, min(ports), max(ports))
    provider = get_provider_info(ip_address)
    if country:
        label_country.config(text=f"Mamlakat: {country}, Shahar: {city}, Viloyat: {region}", fg="white", bg="darkblue")
    else:
        label_country.config(text="Mamlakat aniqlanmadi.", fg="white", bg="darkblue")

    if open_ports:
        port_text = "\n".join(str(port) for port in open_ports)
        label_ports.config(text=f"Ochiq portlar:\n{port_text}", fg="white", bg="darkblue")
    else:
        label_ports.config(text="Ochiq portlar topilmadi.", fg="white", bg="darkblue")

    if mac:
        label_mac.config(text=f"MAC manzili: {mac}", fg="white", bg="darkblue")
    else:
        label_mac.config(text="MAC manzili aniqlanmadi.", fg="white", bg="darkblue")

    if domain:
        label_domain.config(text=f"Hostnomi: {domain}", fg="white", bg="darkblue")
    else:
        label_domain.config(text="Hostnomi aniqlanmadi.", fg="white", bg="darkblue")

    if provider:
        label_provider.config(text=f"Pravayder: {provider}", fg="white", bg="darkblue")
    else:
        label_provider.config(text="Pravayder aniqlanmadi.", fg="white", bg="darkblue")

    # Fayl saqlash tugmasini ko'rsatish
    save_button.config(command=lambda: save_scan_results(ip_address, country, city, region, open_ports, mac, domain, provider),
                       fg="white", bg="darkblue")
    save_button.grid(row=8, column=0, columnspan=2, padx=5, pady=5)


# Asosiy tkinter oynasi
root = tk.Tk()
root.title("IP ma'lumotlari")
root.configure(bg="darkblue")

# Foydalanuvchi uchun kiritish qatori
label_ip = tk.Label(root, text="IP manzili:", bg="darkblue", fg="white")
label_ip.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
entry_ip = tk.Entry(root)
entry_ip.grid(row=0, column=1, padx=5, pady=5)

# Portlarni o'qib olish uchun qatorlar
label_port = tk.Label(root, text="Portlar (vergul orqali ajratilgan):", bg="darkblue", fg="white")
label_port.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
entry_port = tk.Entry(root)
entry_port.grid(row=1, column=1, padx=5, pady=5)

# Ma'lumotlarni ko'rsatish uchun tugma
button_show = tk.Button(root, text="Skanerlash", command=start_scan, fg="white", bg="darkblue")
button_show.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Mamlakat, ochiq portlar, MAC manzili, domen nomi va pravayder ma'lumotlarini ko'rsatish uchun joylar
label_country = tk.Label(root, text="", bg="darkblue", fg="white")
label_country.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
label_ports = tk.Label(root, text="", bg="darkblue", fg="white")
label_ports.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
label_mac = tk.Label(root, text="", bg="darkblue", fg="white")
label_mac.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
label_domain = tk.Label(root, text="", bg="darkblue", fg="white")
label_domain.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
label_provider = tk.Label(root, text="", bg="darkblue", fg="white")
label_provider.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

# Fayl saqlash tugmasi
save_button = tk.Button(root, text="Saqlash", command=save_scan_results, fg="white", bg="darkblue")

root.mainloop()
