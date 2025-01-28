import tkinter as tk
from tkinter import ttk
import subprocess
import re


def extract_ports_from_dockerfile():
    try:
        with open("Dockerfile", "r") as file:
            content = file.read()

        match = re.search(r"EXPOSE\s+([\d\s]+)", content)
        if match:
            ports = match.group(1).split()
            return ports
    except FileNotFoundError:
        print("Dockerfile not found.")
        return []

    return []


def show():
    ports = extract_ports_from_dockerfile()
    student_ports = ", ".join(ports) if ports else "No ports found"

    subprocess.Popen("start cmd /k ipconfig", shell=True)

    main_window = tk.Tk()
    main_window.title("Teaching LilyPond")
    window_width = 600
    window_height = 545
    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()
    position_x = (screen_width - window_width) // 2
    position_y = (screen_height - window_height) // 2 - 100
    main_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    main_window.configure(bg="#f8f9fc")
    main_window.attributes('-topmost', 1)

    style = ttk.Style()
    style.configure("TLabel", font=("Calibri", 12), background="#f8f9fc", foreground="#333333")
    style.configure("Header.TLabel", font=("Calibri", 16, "bold"), background="#f8f9fc", foreground="#000000")

    header = ttk.Label(main_window, text="Thank you for using \"Teaching LilyPond\"", style="Header.TLabel",
                       anchor="center")
    header.pack(pady=20)

    instructions = (
        "If Lilypond Server is active, you will need to rerun this instruction window to show the correct student ports.\n\n"
        "Instructions:\n"
        "1) A cmd window should have appeared.\n"
        "2) Search for the WLAN/Wi-Fi or LAN-Section.\n"
        "3) You will find YOUR_NOTEBOOK_IP next to \"IPv4-Address\": xxx.xxx.xxx.xxx\n"
        "4) Your students can use Lilypond by opening their browsers and entering:\n"
        "     https://<YOUR_NOTEBOOK_IP>:<STUDENT_PORT>\n\n"
        f"Available Student Ports: {student_ports}\n"
        "\nEach student must use a different port number. "
        "Consider writing down which student has which port."
        "To view on your own machine, you can open a browser and enter \"localhost:8080\"."
        
        "\n\nImportant: At first start, certificate \"install_cert.bat\" inside \"_runAsAdmin\" must to be downloaded and executed as Admin for each machine.\n"
        "\nIn case the certificate has newly been installed, browser needs to be restarted. After the application is not needed anymore, the certificates can be removed by executing \"remove_cert.bat\"."
    )

    content = ttk.Label(main_window, text=instructions, style="TLabel", anchor="w", justify="left", wraplength=550)
    content.pack(pady=10, padx=20)

    main_window.mainloop()


if __name__ == "__main__":
    show()