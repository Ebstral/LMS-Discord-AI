# -*- coding: utf-8 -*-
import nebot
import tkinter as tk
import customtkinter as ctk
import psutil
import pynvml 
import threading
import asyncio
from nebot import AI_Bot

try:
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    gpu_available = True
except:
    gpu_available = False

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LMS Discord AI v1.0 (stable)")
        self.geometry("900x550")
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#3b4cca") 

        self.bot_running = False
        self.ai_manager = None
        self.loop = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # log
        self.log_view = ctk.CTkTextbox(self, width=350, corner_radius=10)
        self.log_view.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=20, pady=20)
        self.add_log("--- System Ready ---")

        # Status
        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.info_label = ctk.CTkLabel(self.right_panel, text="Model: waiting to start...", font=("Arial", 16, "bold"))
        self.info_label.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.right_panel, text="Idle", text_color="white", 
                                        fg_color="#2b2b2b", width=250, height=50, corner_radius=12, font=("Arial", 14, "bold"))
        self.status_label.pack(pady=15)

        self.metrics_label = ctk.CTkLabel(self.right_panel, text="Load system...", font=("Consolas", 12))
        self.metrics_label.pack(pady=20)

        # Buttons
        self.btn_start = ctk.CTkButton(self.right_panel, text="Bot Start", command=self.toggle_bot, 
                                       fg_color="#28a745", hover_color="#218838", height=45)
        self.btn_start.pack(pady=10, fill="x")

        self.btn_new_chat = ctk.CTkButton(self.right_panel, text="New Chat / Token Reset", command=self.clear_history, height=45)
        self.btn_new_chat.pack(pady=10, fill="x")

        self.update_metrics()

    def add_log(self, text):
        self.log_view.insert("end", f"> {text}\n")
        self.log_view.see("end")

    def update_metrics(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        gpu_info = "GPU: Not detected"
        if gpu_available:
            try:
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                gpu_info = f"GPU: {util.gpu}% | VRAM: {info.used//1024**2}MB | {temp}°C"
            except:
                gpu_info = "GPU: Reading error"
        self.metrics_label.configure(text=f"CPU: {cpu}% | RAM: {ram}%\n{gpu_info}")
        self.after(2000, self.update_metrics)

    def toggle_bot(self):
        if not self.bot_running:
            self.add_log("Running a bot...")
            self.ai_manager = AI_Bot(gui_app=self)
            self.loop = asyncio.new_event_loop()
            threading.Thread(target=self.run_bot_thread, daemon=True).start()
            self.bot_running = True
            self.btn_start.configure(text="STOP BOT", fg_color="#dc3545", hover_color="#a71d2a")
        else:
            self.add_log("Bot stops...")
            if self.loop:
                asyncio.run_coroutine_threadsafe(self.ai_manager.stop_bot(), self.loop)
            self.bot_running = False
            self.btn_start.configure(text="START BOT", fg_color="#28a745", hover_color="#218838")

    def run_bot_thread(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.ai_manager.start_bot())

    def clear_history(self):
        if self.ai_manager:
            self.add_log(self.ai_manager.clear_all_history())
        else:
            self.add_log("The bot is not running!")

if __name__ == "__main__":
    app = App()
    app.mainloop()