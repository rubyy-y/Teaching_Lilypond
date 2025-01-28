import os
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import font
import ctypes
import sys

state = []


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


def run_docker_prune():
    try:
        result = subprocess.run(
            ["docker", "system", "prune", "-a", "-f"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode == 0:
            print("Docker system prune -a completed successfully.")
            print(result.stdout)
        else:
            print("Error during docker system prune -a.")
            print(result.stderr)

    except Exception as e:
        print(f"An error occurred: {e}")


def check_lilypond_status():
    global state

    try:
        firewall_output = subprocess.run(
            'netsh advfirewall firewall show rule name="lilypond"',
            capture_output=True,
            text=True,
            encoding="cp850"
        ).stdout.lower()

        not_found_phrases = [
            "no rules match",
            "keine regeln",
            "keine übereinstimmenden",
            "does not exist",
            "existiert nicht"
        ]

        return not any(phrase in firewall_output for phrase in not_found_phrases)

    except Exception as e:
        print(f"Error while trying to get firewall rules: {e}")
        firewall_output = False

    print(firewall_output)
    firewall_rule_exists = not ("no rules match" in firewall_output or "keine regeln" in firewall_output)

    container_exists = bool(os.popen('docker ps -a --filter "name=lilypond" --format "{{.ID}}"').read().strip())
    image_exists = bool(os.popen('docker images --filter "reference=lilypond_image" --format "{{.ID}}"').read().strip())

    return firewall_rule_exists or container_exists or image_exists


def delete_firewall_rule():
    try:
        rule_name = 'lilypond'
        command = f'netsh advfirewall firewall delete rule name="{rule_name}"'
        os.system(command)

    except Exception as e:
        print(f"An error occurred: {e}")


def delete_container_and_image():
    container_command = 'docker ps -a --filter "name=lilypond" --format "{{.ID}}"'
    container_ids = os.popen(container_command).read().strip().splitlines()
    for container_id in container_ids:
        os.system(f"docker rm -f {container_id}")

    image_command = 'docker images --filter "reference=lilypond_image" --format "{{.ID}}"'
    image_ids = os.popen(image_command).read().strip().splitlines()
    os.system(f"docker rmi -f {image_ids[0]}")


def clean_up():
    try:
        delete_firewall_rule()
    except Exception as e:
        print(e)
    try:
        delete_container_and_image()
    except Exception as e:
        print(e)

    try:
        run_docker_prune()
    except Exception as e:
        print(e)

    root = tk.Tk()
    root.title("Teaching Lilypond")
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
    style.configure("TFrame", background="#f8f9fc")

    bold_font = font.Font(family="Calibri", size=14, weight="bold")

    header = ttk.Label(root, text="LilyPond Server has shut down!", anchor="center", wraplength=400)
    header.pack(pady=30)
    header.configure(font=bold_font)

    button_frame = ttk.Frame(root, style="TFrame")
    button_frame.pack(pady=20)

    cancel_button = ttk.Button(button_frame, text="OK", style="TButton", command=sys.exit)
    cancel_button.pack(pady=10)

    root.mainloop()


def cancel():
    root.destroy()
    sys.exit()


if __name__ == "__main__":
    run_as_admin()

    if check_lilypond_status():
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
        style.configure("TButton", font=("Calibri", 12), background="#007bff", foreground="white", borderwidth=0,
                        focuscolor="none")
        style.map("TButton", background=[("active", "#0056b3")])
        style.configure("Red.TButton", font=("Calibri", 12), background="#dc3545", foreground="white", borderwidth=0,
                        focuscolor="none")
        style.map("Red.TButton", background=[("active", "#a71d2a")])
        style.configure("TFrame", background="#f8f9fc")

        bold_font = font.Font(family="Calibri", size=14, weight="bold")

        header = ttk.Label(root, text="Are you sure you want to shut down LilyPond?", anchor="center", wraplength=400)
        header.pack(pady=20)
        header.configure(font=bold_font)

        subtext = ttk.Label(root,
                            text="If you continue, the LilyPond server will be shut down and all files are going to be deleted. "
                                 "Make sure you execute \"getFolders.exe\" before, to save all files.", style="TLabel",
                            anchor="center",
                            wraplength=400)
        subtext.pack(pady=10)

        button_frame = ttk.Frame(root, style="TFrame")
        button_frame.pack(pady=20)

        cancel_button = ttk.Button(button_frame, text="Cancel", style="TButton",
                                   command=lambda: (root.destroy(), sys.exit()))
        cancel_button.grid(row=0, column=0, padx=10)

        shut_down_button = ttk.Button(button_frame, text="Shut Down", style="Red.TButton",
                                      command=lambda: (root.destroy(), clean_up()))
        shut_down_button.grid(row=0, column=1, padx=10)

        root.mainloop()

    else:
        root = tk.Tk()
        root.title("Teaching Lilypond")
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
        style.configure("TFrame", background="#f8f9fc")

        bold_font = font.Font(family="Calibri", size=14, weight="bold")

        header = ttk.Label(root, text="LilyPond Server already shut down!", anchor="center", wraplength=400)
        header.pack(pady=30)
        header.configure(font=bold_font)

        button_frame = ttk.Frame(root, style="TFrame")
        button_frame.pack(pady=20)

        cancel_button = ttk.Button(button_frame, text="OK", style="TButton", command=sys.exit)
        cancel_button.pack(pady=10)

        root.mainloop()
