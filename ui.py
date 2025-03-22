import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap import Style, Window
import pandas as pd
import threading
from main import start_bot
from database.db import load_trade_history
import json

# Modern Cyberpunk style
CYBERPUNK_THEME = "cyborg"

class TradeBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Trade Bot")
        self.root.geometry("900x600")
        self.style = Style(theme=CYBERPUNK_THEME)
        
        # Bot instance
        self.bot = None
        self.bot_thread = None

        # Variables
        self.risk_age = tk.StringVar()
        self.money = tk.StringVar(value="1000")  # Default $1000
        self.mode = tk.StringVar(value="Default")
        self.risk_percentage = tk.StringVar(value="2")
        self.target_profit = tk.StringVar(value="1")
        self.bot_status = tk.StringVar(value="Not Running")

        # Create Tabs
        self.tab_control = ttk.Notebook(root)
        self.overview_tab = ttk.Frame(self.tab_control)
        self.history_tab = ttk.Frame(self.tab_control)
        self.settings_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.overview_tab, text="Overview")
        self.tab_control.add(self.history_tab, text="Trade History")
        self.tab_control.add(self.settings_tab, text="Settings")
        self.tab_control.pack(expand=True, fill="both", padx=10, pady=10)

        # Setup Tabs
        self.setup_overview_tab()
        self.setup_history_tab()
        self.setup_settings_tab()
        
        # Update timer
        self.root.after(1000, self.update_trade_history)

    def setup_overview_tab(self):
        # Frame for Inputs
        input_frame = ttk.LabelFrame(self.overview_tab, text="Trading Configuration", padding=10)
        input_frame.pack(fill="x", padx=10, pady=10)

        # Money Input
        ttk.Label(input_frame, text="Trading Capital ($):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(input_frame, textvariable=self.money).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Mode Selection
        ttk.Label(input_frame, text="Trading Mode:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        mode_combo = ttk.Combobox(input_frame, textvariable=self.mode, values=["Default", "Aggressive"], state="readonly")
        mode_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Start/Stop Button
        self.start_button = ttk.Button(input_frame, text="Start Bot", command=self.toggle_bot, style="success.TButton")
        self.start_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        # Bot Status
        status_frame = ttk.LabelFrame(self.overview_tab, text="Status", padding=10)
        status_frame.pack(fill="x", padx=10, pady=10)
        ttk.Label(status_frame, text="Bot Status:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(status_frame, textvariable=self.bot_status, style="info.TLabel").grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Money Overview Section
        money_overview_frame = ttk.LabelFrame(self.overview_tab, text="Trading Overview", padding=10)
        money_overview_frame.pack(fill="x", padx=10, pady=10)

        # Current Money
        ttk.Label(money_overview_frame, text="Trading Capital:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.current_money_label = ttk.Label(money_overview_frame, text="$0", style="info.TLabel")
        self.current_money_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Risk Percentage
        ttk.Label(money_overview_frame, text="Risk Per Trade:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.risk_percentage_label = ttk.Label(money_overview_frame, text="2%", style="info.TLabel")
        self.risk_percentage_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Target Profit
        ttk.Label(money_overview_frame, text="Target Profit:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.target_profit_label = ttk.Label(money_overview_frame, text="1%", style="info.TLabel")
        self.target_profit_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Update overview when values change
        self.money.trace_add("write", self.update_money_overview)
        self.risk_percentage.trace_add("write", self.update_money_overview)
        self.target_profit.trace_add("write", self.update_money_overview)

    def setup_history_tab(self):
        # Frame for Trade History
        history_frame = ttk.LabelFrame(self.history_tab, text="Trade History", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview for Trade History
        columns = ("Timestamp", "Action", "Price", "Reason")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_settings_tab(self):
        # Frame for Settings
        settings_frame = ttk.LabelFrame(self.settings_tab, text="Trading Settings", padding=10)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Risk Percentage
        ttk.Label(settings_frame, text="Risk Percentage:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.risk_percentage).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Target Profit
        ttk.Label(settings_frame, text="Target Profit %:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.target_profit).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Save Button
        ttk.Button(settings_frame, text="Save Settings", command=self.save_settings, style="primary.TButton").grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

    def toggle_bot(self):
        if self.bot is None or not self.bot.is_running:
            self.start_bot()
        else:
            self.stop_bot()

    def start_bot(self):
        try:
            money = float(self.money.get())
            risk = float(self.risk_percentage.get())
            profit = float(self.target_profit.get())
            
            if money <= 0 or risk <= 0 or profit <= 0:
                messagebox.showerror("Error", "Money, risk, and profit must be positive numbers")
                return
                
            self.bot = start_bot(
                total_money=money,
                risk_percentage=risk,
                mode=self.mode.get(),
                target_profit=profit
            )
            
            self.bot_thread = threading.Thread(target=self.bot.start)
            self.bot_thread.daemon = True
            self.bot_thread.start()
            
            self.bot_status.set("Running")
            self.start_button.configure(text="Stop Bot", style="danger.TButton")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start bot: {str(e)}")

    def stop_bot(self):
        if self.bot:
            self.bot.stop()
            self.bot = None
            self.bot_status.set("Stopped")
            self.start_button.configure(text="Start Bot", style="success.TButton")

    def save_settings(self):
        try:
            risk = float(self.risk_percentage.get())
            profit = float(self.target_profit.get())
            
            if risk <= 0 or profit <= 0:
                messagebox.showerror("Error", "Risk and profit must be positive numbers")
                return
                
            self.update_money_overview()
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid risk or profit values")

    def update_money_overview(self, *args):
        try:
            money = float(self.money.get())
            risk = float(self.risk_percentage.get())
            profit = float(self.target_profit.get())
            
            self.current_money_label.config(text=f"${money:,.2f}")
            self.risk_percentage_label.config(text=f"{risk}%")
            self.target_profit_label.config(text=f"{profit}%")
            
        except ValueError:
            pass

    def update_trade_history(self):
        """Update trade history every second"""
        try:
            trade_data = load_trade_history()
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Add new items
            for trade in trade_data:
                self.tree.insert("", "end", values=(
                    trade["timestamp"],
                    trade["action"].upper(),
                    f"${trade['price']:,.2f}",
                    trade["reason"]
                ))
                
        except Exception as e:
            print(f"Error updating trade history: {str(e)}")
            
        finally:
            # Schedule next update
            self.root.after(1000, self.update_trade_history)

# Run the App
if __name__ == "__main__":
    root = Window(themename=CYBERPUNK_THEME)
    app = TradeBotApp(root)
    root.mainloop() 