import os
import subprocess
import ctypes
import re
import sys
import threading
import tkinter as tk
from tkinter import ttk

ports = []
ipaddr = ""
container_name = "lilypond"
path = 'Dockerfile'


def run_as_admin():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False

    if not is_admin:
        try:
            script = sys.argv[0]
            params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script}" {params}', None, 0
            )
            sys.exit()
        except Exception as e:
            print(f"Error while restarting: {e}")
            return False
    return True


def get_students():
    def submit(event=None):
        user_input = entry.get()
        try:
            value = int(user_input)
            root.valid_value = value
            root.destroy()
        except ValueError:
            entry.configure(style="Invalid.TEntry")

    def cancel():
        root.valid_value = None
        root.destroy()
        sys.exit()

    root = tk.Tk()
    root.title("Teaching LilyPond")
    window_width = 450
    window_height = 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_x = (screen_width - window_width) // 2
    position_y = (screen_height - window_height) // 2 - 100
    root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    root.configure(bg="#f8f9fc")
    root.attributes('-topmost', 1)
    style = ttk.Style()

    style.theme_use("default")
    style.configure("TLabel", font=("Calibri", 14), background="#f8f9fc", foreground="#333333")
    style.configure("TButton", font=("Calibri", 12), background="#007bff", foreground="white", borderwidth=0,
                    focuscolor="none")
    style.map("TButton", background=[("active", "#0056b3")])
    style.configure("TEntry", font=("Calibri", 12), padding=5)
    style.configure("Invalid.TEntry", font=("Calibri", 12), padding=5, fieldbackground="#ffd1d1", bordercolor="red")
    style.configure("TFrame", background="#f8f9fc")

    header = ttk.Label(root, text="How many students do you have?", style="TLabel", anchor="center")
    header.pack(pady=20)

    entry_frame = ttk.Frame(root, style="TFrame")
    entry_frame.pack(pady=20)
    entry = ttk.Entry(entry_frame, style="TEntry", justify="center", width=30)
    entry.pack()

    entry.bind("<Return>", submit)

    button_frame = ttk.Frame(root, style="TFrame")
    button_frame.pack(pady=20)

    submit_button = ttk.Button(button_frame, text="Submit", style="TButton", command=submit)
    submit_button.grid(row=0, column=1, padx=10)

    cancel_button = ttk.Button(button_frame, text="Cancel", style="TButton", command=cancel)
    cancel_button.grid(row=0, column=0, padx=10)

    root.mainloop()

    return root.valid_value


def ask_for_ip():
    global ipaddr

    def is_valid_ipv4(ip):
        pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
        if pattern.match(ip):
            parts = ip.split(".")
            return all(0 <= int(part) <= 255 for part in parts)
        return False

    def submit():
        user_input = entry.get().strip()
        if is_valid_ipv4(user_input):
            root.valid_ip = user_input
            root.destroy()
        else:
            entry.configure(style="Invalid.TEntry")

    root = tk.Tk()
    root.title("Teaching LilyPond")
    window_width = 450
    window_height = 250
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_x = (screen_width - window_width) // 2
    position_y = (screen_height - window_height) // 2 - 100
    root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    root.configure(bg="#f8f9fc")
    root.attributes('-topmost', 1)
    style = ttk.Style()
    style.theme_use("default")
    style.configure("TLabel", font=("Calibri", 14), background="#f8f9fc", foreground="#333333")
    style.configure("TButton", font=("Calibri", 12), background="#007bff", foreground="white", borderwidth=0)
    style.map("TButton", background=[("active", "#0056b3")])
    style.configure("TEntry", font=("Calibri", 12), padding=5)
    style.configure("Invalid.TEntry", font=("Calibri", 12), padding=5, fieldbackground="#ffd1d1", bordercolor="red")
    style.configure("TFrame", background="#f8f9fc")

    header = ttk.Label(root, text="Enter your IP-Address!\nIf you don't know how to find it open showinstructions.exe",
                       style="TLabel", anchor="center", justify="center", wraplength=400)
    header.pack(pady=20)

    entry_frame = ttk.Frame(root, style="TFrame")
    entry_frame.pack(pady=10)
    entry = ttk.Entry(entry_frame, style="TEntry", justify="center", width=30)
    entry.pack()
    entry.bind("<Return>", lambda event: submit())

    button_frame = ttk.Frame(root, style="TFrame")
    button_frame.pack(pady=20)
    submit_button = ttk.Button(button_frame, text="Submit", style="TButton", command=submit)
    submit_button.grid(row=0, column=1, padx=10)
    cancel_button = ttk.Button(button_frame, text="Cancel", style="TButton", command=sys.exit)
    cancel_button.grid(row=0, column=0, padx=10)

    root.mainloop()
    return root.valid_ip


def update_dockerfile(path, students, ports, ip):
    for i in range(students):
        ports.append(8081 + i)

    with open(path, 'r') as file:
        content = file.read()

    expose_line = f"EXPOSE {' '.join(map(str, ports))}"

    if re.search(r'^EXPOSE.*$', content, flags=re.MULTILINE):
        content = re.sub(r'^EXPOSE.*$', expose_line, content, flags=re.MULTILINE)
    else:
        content += f"\n{expose_line}\n"

    content = re.sub(r"CN=[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+", f"CN={ip}", content)
    content = re.sub(r"IP:[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+", f"IP:{ip}", content)

    with open(f'{path}', 'w') as file:
        file.write(content)

    print(f"Dockerfile updated! Following ports added: {ports}")


def start_container():
    subprocess.run(f"start /wait cmd /c docker build -t {container_name}_image .", shell=True, check=True)
    subprocess.run(f'attrib +h "{path}"', shell=True, check=True)
    args = "-p 8080:8080 "
    for i in ports:
        args += f"-p {i}:{i} "

    subprocess.run(f"docker run -d --name {container_name} {args} {container_name}_image", capture_output=True,
                   text=True)

    result = subprocess.run(["docker", "ps"], capture_output=True, text=True, shell=False, check=True)

    if not ("lilypond" in result.stdout):
        print("Error: Container could not be started.")
    else:
        print("Container up and running.")
        os.system(
            f"netsh advfirewall firewall add rule name=\"lilypond\" dir=in action=allow protocol=TCP localport={ports[0]}-{ports[-1]}")

    return "lilypond" in result.stdout


def start_code_server_instances():
    for p in ports:
        os.system(f'docker exec -d {container_name} code-server --port {p}')

def create_folders():
    os.system(f'docker exec -d {container_name} mkdir /home/coder/lily/students')

    for studentID in ports:
        os.system(f'docker exec -d {container_name} mkdir /home/coder/lily/students/{studentID}')

    print("Studentfolders created.")


def create_cert_batch(ip):
    container_path = "/home/coder/lily/runAsAdmin/"
    bat_file = "remove_cert.bat"
    with open(bat_file, "w") as file:
        file.write(f"""@echo off
    echo Removing Certificate with following IP: {ip}

    powershell -Command "Get-ChildItem -Path Cert:\\LocalMachine\\Root | Where-Object {{ $_.Subject -match '{ip}' }} | Remove-Item -Force"

    powershell -Command "Get-ChildItem -Path Cert:\\CurrentUser\\Root | Where-Object {{ $_.Subject -match '{ip}' }} | Remove-Item -Force"

    echo Certificate {ip} was removed!
    pause
    """)

    print(f"Batch file '{bat_file}' was created!")


    os.system(f'docker exec -d {container_name} sudo /home/coder/generateBat.sh')
    copy_command = f"docker cp {bat_file} {container_name}:{container_path}{bat_file}"
    process = subprocess.run(copy_command, shell=True)

    if process.returncode == 0:
        print(f"Successfully copied file in container '{container_name}' in path '{container_path}'!")
        os.remove(bat_file)
    else:
        print("Error while coping Batch file to container.")


def run_docker_tasks_in_background(path, students, ports, ip, root):
    update_dockerfile(path, students, ports, ip)

    if start_container():
        create_folders()
        start_code_server_instances()
        create_cert_batch(ip)
    else:
        print("Couldn't start Lilypond Server! Please retry!")
        root.destroy()
        sys.exit(1)

    root.destroy()


def run_lilypond():
    global ipaddr

    if not os.path.exists(path):
        root = tk.Tk()
        root.title("Teaching LilyPond")

        window_width = 450
        window_height = 250
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        position_x = (screen_width - window_width) // 2
        position_y = (screen_height - window_height) // 2 - 100
        root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

        root.configure(bg="#f8f9fc")
        root.attributes('-topmost', 1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Header.TLabel", font=("Calibri", 18, "bold"), background="#f8f9fc", foreground="#dc3545")
        style.configure("TLabel", font=("Calibri", 14), background="#f8f9fc", foreground="#333333")
        style.configure("TButton", font=("Calibri", 12), background="#007bff", foreground="white", borderwidth=0,
                        focuscolor="none")
        style.map("TButton", background=[("active", "#0056b3")])
        style.configure("TFrame", background="#f8f9fc")

        header_label = ttk.Label(root, text="Error!", style="Header.TLabel", anchor="center", foreground="#dc3545")
        header_label.pack(pady=20)

        result_label = ttk.Label(
            root, text="Dockerfile not found!\nPlease ensure that Dockerfile exists in the correct path.",
            style="TLabel", anchor="center", wraplength=400, justify="center"
        )
        result_label.pack(expand=True, pady=10)

        button_frame = ttk.Frame(root, style="TFrame")
        button_frame.pack(pady=20)

        cancel_button = ttk.Button(button_frame, text="Cancel", style="TButton", command=lambda: sys.exit(0))
        cancel_button.grid(row=0, column=0, padx=10)

        root.mainloop()
        sys.exit()

    subprocess.run(f'attrib -h "{path}"', shell=True, check=True)

    ip = ask_for_ip()
    ipaddr = ip
    students = get_students()

    if students and ip:
        root = tk.Tk()
        root.title("Teaching LilyPond")
        window_width = 500
        window_height = 200
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        position_x = (screen_width - window_width) // 2
        position_y = (screen_height - window_height) // 2 - 100
        root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

        root.configure(bg="#f8f9fc")
        root.attributes('-topmost', 1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TLabel", font=("Calibri", 12), background="#f8f9fc", foreground="#333333")
        style.configure("Header.TLabel", font=("Calibri", 16, "bold"), background="#f8f9fc", foreground="#000000")

        header = ttk.Label(root, text="LilyPond Server is starting ...", style="Header.TLabel", anchor="center")
        header.pack(pady=10)

        message = ttk.Label(root, text="This could take up to a minute ...\nGo grab a coffee!", style="TLabel",
                            anchor="center", justify="center")
        message.pack(pady=10)

        docker_thread = threading.Thread(
            target=run_docker_tasks_in_background, args=(path, students, ports, ip, root), daemon=False
        )
        docker_thread.start()

        root.mainloop()
    sys.exit()


def is_docker_running():
    try:
        result = subprocess.run(
            ["docker", "info"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


if __name__ == "__main__":
    run_as_admin()

    if is_docker_running():
        run_lilypond()

    else:
        root = tk.Tk()
        root.title("Teaching LilyPond")

        window_width = 450
        window_height = 250
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        position_x = (screen_width - window_width) // 2
        position_y = (screen_height - window_height) // 2 - 100
        root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

        root.configure(bg="#f8f9fc")
        root.attributes('-topmost', 1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Header.TLabel", font=("Calibri", 18, "bold"), background="#f8f9fc", foreground="#dc3545")
        style.configure("TLabel", font=("Calibri", 14), background="#f8f9fc", foreground="#333333")
        style.configure("TButton", font=("Calibri", 12), background="#007bff", foreground="white", borderwidth=0,
                        focuscolor="none")
        style.map("TButton", background=[("active", "#0056b3")])
        style.configure("TFrame", background="#f8f9fc")

        header_label = ttk.Label(root, text="Error!", style="Header.TLabel", anchor="center")
        header_label.pack(pady=20)

        message_label = ttk.Label(
            root,
            text="Docker Desktop is not running!\n Please start Docker Desktop before you continue.",
            style="TLabel",
            anchor="center",
            wraplength=400,
            justify="center"
        )
        message_label.pack(expand=True, pady=10)

        button_frame = ttk.Frame(root, style="TFrame")
        button_frame.pack(pady=20)

        cancel_button = ttk.Button(button_frame, text="Exit", style="TButton", command=sys.exit)
        cancel_button.pack(pady=10)

        root.mainloop()
