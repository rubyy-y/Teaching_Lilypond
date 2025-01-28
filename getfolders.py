import os
import subprocess
import tkinter as tk
from tkinter import ttk
import ctypes
import sys
import shutil

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

def copy_folder_from_docker(container_name, container_path):
    current_dir = os.getcwd()

    target_path = os.path.join(current_dir, os.path.basename(container_path.strip('/')))

    if os.path.exists(target_path):
        shutil.rmtree(target_path)

    try:
        subprocess.run(
            ["docker", "cp", f"{container_name}:{container_path}", target_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True, f"The folder was successfully copied to '{target_path}'."
    except subprocess.CalledProcessError as e:
        return False, f"Error copying folder: {e.stderr.decode('utf-8').strip()}"


def main():
    container_name = "lilypond"
    container_path = "/home/coder/lily/students/"

    success, message = copy_folder_from_docker(container_name, container_path)

    root = tk.Tk()
    root.title("Teaching Lilypond")
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
    style.configure("Header.TLabel", font=("Calibri", 18, "bold"), background="#f8f9fc", foreground="#333333")
    style.configure("TLabel", font=("Calibri", 14), background="#f8f9fc", foreground="#333333")
    style.configure("TButton", font=("Calibri", 12), background="#007bff", foreground="white", borderwidth=0,
                    focuscolor="none")
    style.map("TButton", background=[("active", "#0056b3")])
    style.configure("TFrame", background="#f8f9fc")

    header_text = "Success!" if success else "Error!"
    header_color = "#28a745" if success else "#dc3545"
    header_label = ttk.Label(root, text=header_text, style="Header.TLabel", anchor="center", foreground=header_color)
    header_label.pack(pady=20)

    result_label = ttk.Label(root, text=message, style="TLabel", anchor="center", wraplength=400, justify="center")
    result_label.pack(expand=True, pady=10)

    button_frame = ttk.Frame(root, style="TFrame")
    button_frame.pack(pady=20)

    close_button = ttk.Button(button_frame, text="Close", style="TButton", command=root.destroy)
    close_button.grid(row=0, column=0, padx=10)

    root.mainloop()


if __name__ == "__main__":
    run_as_admin()
    main()
