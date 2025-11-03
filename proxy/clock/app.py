import tkinter as tk
import threading
import time
from fastapi import FastAPI
import uvicorn


class Stopwatch:
    def __init__(self, master):
        self.master = master
        master.title("Cache Metrics")
        
        # Center the window on screen - optimized dimensions
        window_width = 520
        window_height = 240
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        master.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        master.configure(bg='#f8f9fa')
        master.resizable(False, False)

        self.time = 0  # elapsed time in seconds
        self.running = False
        self.start_time = None
        self._lock = threading.Lock()  # Thread safety for API access
        
        # Initialize metrics
        self.lookups = 0
        self.admissions = 0
        self.evictions = 0

        # Main container with subtle background
        main_frame = tk.Frame(master, bg='#ffffff', relief='flat', bd=0)
        main_frame.pack(fill='both', expand=True, padx=16, pady=16)

        # Time display with refined typography
        self.label = tk.Label(main_frame, text="00:00.00", 
                             font=("SF Pro Display", 28, "normal"), 
                             fg='#1d1d1f', bg='#ffffff')
        self.label.pack(pady=(20, 30))

        # Metrics container with subtle separator
        metrics_container = tk.Frame(main_frame, bg='#ffffff')
        metrics_container.pack(fill='x', padx=20)

        # Subtle top border for metrics section
        separator = tk.Frame(metrics_container, height=1, bg='#e5e5e7')
        separator.pack(fill='x', pady=(0, 20))

        # Metrics grid with improved spacing
        grid_frame = tk.Frame(metrics_container, bg='#ffffff')
        grid_frame.pack(fill='x')

        # Configure equal column distribution
        for i in range(3):
            grid_frame.grid_columnconfigure(i, weight=1, uniform="metric_col")

        # Refined typography styles
        label_style = {
            'font': ("SF Pro Text", 11, "normal"),
            'fg': '#86868b',
            'bg': '#ffffff'
        }
        
        value_style = {
            'font': ("SF Pro Display", 26, "normal"),
            'fg': '#1d1d1f',
            'bg': '#ffffff'
        }

        # Lookups metric
        lookups_frame = tk.Frame(grid_frame, bg='#ffffff')
        lookups_frame.grid(row=0, column=0, sticky='ew', padx=8)
        
        tk.Label(lookups_frame, text="LOOKUPS", **label_style).pack(anchor='center')
        self.lookups_label = tk.Label(lookups_frame, text="0", **value_style)
        self.lookups_label.pack(anchor='center', pady=(4, 0))

        # Admissions metric
        admissions_frame = tk.Frame(grid_frame, bg='#ffffff')
        admissions_frame.grid(row=0, column=1, sticky='ew', padx=8)
        
        tk.Label(admissions_frame, text="ADMISSIONS", **label_style).pack(anchor='center')
        self.admissions_label = tk.Label(admissions_frame, text="0", **value_style)
        self.admissions_label.pack(anchor='center', pady=(4, 0))

        # Evictions metric
        evictions_frame = tk.Frame(grid_frame, bg='#ffffff')
        evictions_frame.grid(row=0, column=2, sticky='ew', padx=8)
        
        tk.Label(evictions_frame, text="EVICTIONS", **label_style).pack(anchor='center')
        self.evictions_label = tk.Label(evictions_frame, text="0", **value_style)
        self.evictions_label.pack(anchor='center', pady=(4, 0))

        # Update the display periodically
        self.update_clock()

    def update_clock(self):
        with self._lock:
            if self.running and self.start_time:
                self.time = time.time() - self.start_time
            self.label.config(text=self.format_time(self.time))
            
            # Update metrics display (remove hits)
            self.lookups_label.config(text=f"{self.lookups:,}")
            self.admissions_label.config(text=f"{self.admissions:,}")
            self.evictions_label.config(text=f"{self.evictions:,}")
            
        self.master.after(100, self.update_clock)  # update every 100ms for smoother display

    def format_time(self, seconds):
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        centisecs = int((seconds - int(seconds)) * 100)
        return f"{mins:02}:{secs:02}.{centisecs:02}"

    def bring_to_front(self):
        """Bring the window to front"""
        self.master.after(10, lambda: (
            self.master.lift(),
            self.master.attributes('-topmost', True),
            self.master.attributes('-topmost', False),
            self.master.focus_force()
        ))

    def start(self):
        with self._lock:
            if not self.running:
                self.running = True
                self.start_time = time.time() - self.time
                self.bring_to_front()
                return {"status": "started", "time": self.time}
            return {"status": "already_running", "time": self.time}

    def stop(self):
        with self._lock:
            if self.running:
                self.running = False
                self.time = time.time() - self.start_time if self.start_time else 0
                self.bring_to_front()
                return {"status": "stopped", "time": self.time}
            return {"status": "already_stopped", "time": self.time}

    def reset(self):
        with self._lock:
            self.running = False
            self.time = 0
            self.start_time = None
            self.label.config(text="00:00.00")
            self.bring_to_front()
            return {"status": "reset", "time": 0}
    
    def get_status(self):
        with self._lock:
            current_time = self.time
            if self.running and self.start_time:
                current_time = time.time() - self.start_time
            return {
                "running": self.running,
                "time": current_time,
                "formatted_time": self.format_time(current_time),
                "metrics": {
                    "lookups": self.lookups,
                    "admissions": self.admissions,
                    "evictions": self.evictions
                }
            }
    
    def update_metrics(self, hits=None, lookups=None, admissions=None, evictions=None):
        """Update cache metrics"""
        with self._lock:
            if lookups is not None:
                self.lookups = lookups
            if admissions is not None:
                self.admissions = admissions
            if evictions is not None:
                self.evictions = evictions
            return {
                "lookups": self.lookups,
                "admissions": self.admissions,
                "evictions": self.evictions
            }


# Global stopwatch instance for API access
stopwatch_instance = None

# FastAPI app
app = FastAPI(title="Stopwatch API", description="REST API for controlling the stopwatch")

@app.get("/")
async def root():
    return {"message": "Stopwatch API is running"}

@app.get("/status")
async def get_status():
    if stopwatch_instance:
        return stopwatch_instance.get_status()
    return {"error": "Stopwatch not initialized"}

@app.get("/start")
async def start_stopwatch():
    if stopwatch_instance:
        return stopwatch_instance.start()
    return {"error": "Stopwatch not initialized"}

@app.get("/stop")
async def stop_stopwatch():
    if stopwatch_instance:
        return stopwatch_instance.stop()
    return {"error": "Stopwatch not initialized"}

@app.get("/reset")
async def reset_stopwatch():
    if stopwatch_instance:
        return stopwatch_instance.reset()
    return {"error": "Stopwatch not initialized"}

@app.get("/metrics")
async def update_metrics(hits: int = None, lookups: int = None, admissions: int = None, evictions: int = None):
    if stopwatch_instance:
        return stopwatch_instance.update_metrics(hits, lookups, admissions, evictions)
    return {"error": "Stopwatch not initialized"}

@app.get("/metrics/reset")
async def reset_metrics():
    """Reset all metrics to zero"""
    if stopwatch_instance:
        return stopwatch_instance.update_metrics(lookups=0, admissions=0, evictions=0)
    return {"error": "Stopwatch not initialized"}

@app.get("/quit")
async def quit_app():
    """Close the application"""
    if stopwatch_instance:
        # Schedule the GUI to close on the main thread
        stopwatch_instance.master.after(100, stopwatch_instance.master.quit)
        return {"status": "Application closing..."}
    return {"error": "Stopwatch not initialized"}

@app.get("/focus")
async def focus_window():
    """Bring the GUI window to front/focus"""
    if stopwatch_instance:
        # Schedule the GUI focus on the main thread
        stopwatch_instance.master.after(10, lambda: (
            stopwatch_instance.master.lift(),
            stopwatch_instance.master.attributes('-topmost', True),
            stopwatch_instance.master.attributes('-topmost', False),
            stopwatch_instance.master.focus_force()
        ))
        return {"status": "Window brought to front"}
    return {"error": "Stopwatch not initialized"}

def run_api_server():
    """Run the FastAPI server in a separate thread"""
    uvicorn.run(app, host="127.0.0.1", port=9000, log_level="info")

if __name__ == "__main__":
    # Start the API server in a separate thread
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()
    
    # Start the GUI
    root = tk.Tk()
    stopwatch_instance = Stopwatch(root)
    
    print("Cache Metrics GUI started!")
    print("API server running on http://127.0.0.1:9000")
    print("\nTimer endpoints:")
    print("  GET  /status - Get current status and metrics")
    print("  GET  /start  - Start the stopwatch")
    print("  GET  /stop   - Stop the stopwatch") 
    print("  GET  /reset  - Reset the stopwatch")
    print("\nMetrics endpoints:")
    print("  GET  /metrics - Set absolute metric values")
    print("       ?lookups=25&admissions=80&evictions=15")
    print("  GET  /metrics/reset - Reset all metrics to zero")
    print("\nApp control:")
    print("  GET  /focus - Bring window to front")
    print("  GET  /quit - Close the application")
    
    root.mainloop()