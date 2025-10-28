import tkinter as tk
import threading
import time
from fastapi import FastAPI
import uvicorn


class Stopwatch:
    def __init__(self, master):
        self.master = master
        master.title("Cache Metrics")
        master.geometry("380x300")
        master.configure(bg='white')
        master.resizable(False, False)

        self.time = 0  # elapsed time in seconds
        self.running = False
        self.start_time = None
        self._lock = threading.Lock()  # Thread safety for API access
        
        # Initialize metrics
        self.hits = 0
        self.misses = 0
        self.admissions = 0
        self.evictions = 0

        # Time display
        self.label = tk.Label(master, text="00:00.00", 
                             font=("Menlo", 36, "normal"), 
                             fg='#2c2c2c', bg='white')
        self.label.pack(pady=30)

        # Metrics grid
        metrics_frame = tk.Frame(master, bg='white')
        metrics_frame.pack(pady=15)

        # Metrics style - cleaner typography
        metric_style = {
            'font': ("Helvetica", 11),
            'fg': '#8E8E93',
            'bg': 'white'
        }
        
        value_style = {
            'font': ("Menlo", 18, "normal"),
            'fg': '#1D1D1F',
            'bg': 'white'
        }

        # Create 2x2 grid
        grid_frame = tk.Frame(metrics_frame, bg='white')
        grid_frame.pack()

        # Row 1
        hits_frame = tk.Frame(grid_frame, bg='white')
        hits_frame.grid(row=0, column=0, padx=15, pady=8)
        tk.Label(hits_frame, text="HITS", **metric_style).pack()
        self.hits_label = tk.Label(hits_frame, text="0", **value_style)
        self.hits_label.pack()

        misses_frame = tk.Frame(grid_frame, bg='white')
        misses_frame.grid(row=0, column=1, padx=15, pady=8)
        tk.Label(misses_frame, text="MISSES", **metric_style).pack()
        self.misses_label = tk.Label(misses_frame, text="0", **value_style)
        self.misses_label.pack()

        # Row 2
        admissions_frame = tk.Frame(grid_frame, bg='white')
        admissions_frame.grid(row=1, column=0, padx=15, pady=12)
        tk.Label(admissions_frame, text="ADMISSIONS", **metric_style).pack()
        self.admissions_label = tk.Label(admissions_frame, text="0", **value_style)
        self.admissions_label.pack()

        evictions_frame = tk.Frame(grid_frame, bg='white')
        evictions_frame.grid(row=1, column=1, padx=15, pady=12)
        tk.Label(evictions_frame, text="EVICTIONS", **metric_style).pack()
        self.evictions_label = tk.Label(evictions_frame, text="0", **value_style)
        self.evictions_label.pack()

        # Update the label periodically
        self.update_clock()

    def update_clock(self):
        with self._lock:
            if self.running and self.start_time:
                self.time = time.time() - self.start_time
            self.label.config(text=self.format_time(self.time))
            
            # Update metrics display
            self.hits_label.config(text=f"{self.hits:,}")
            self.misses_label.config(text=f"{self.misses:,}")
            self.admissions_label.config(text=f"{self.admissions:,}")
            self.evictions_label.config(text=f"{self.evictions:,}")
            
        self.master.after(100, self.update_clock)  # update every 100ms for smoother display

    def format_time(self, seconds):
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        centisecs = int((seconds - int(seconds)) * 100)
        return f"{mins:02}:{secs:02}.{centisecs:02}"

    def start(self):
        with self._lock:
            if not self.running:
                self.running = True
                self.start_time = time.time() - self.time
                return {"status": "started", "time": self.time}
            return {"status": "already_running", "time": self.time}

    def stop(self):
        with self._lock:
            if self.running:
                self.running = False
                self.time = time.time() - self.start_time if self.start_time else 0
                return {"status": "stopped", "time": self.time}
            return {"status": "already_stopped", "time": self.time}

    def reset(self):
        with self._lock:
            self.running = False
            self.time = 0
            self.start_time = None
            self.label.config(text="00:00.00")
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
                    "hits": self.hits,
                    "misses": self.misses,
                    "admissions": self.admissions,
                    "evictions": self.evictions
                }
            }
    
    def update_metrics(self, hits=None, misses=None, admissions=None, evictions=None):
        """Update cache metrics"""
        with self._lock:
            if hits is not None:
                self.hits = hits
            if misses is not None:
                self.misses = misses
            if admissions is not None:
                self.admissions = admissions
            if evictions is not None:
                self.evictions = evictions
            return {
                "hits": self.hits,
                "misses": self.misses,
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

@app.post("/start")
async def start_stopwatch():
    if stopwatch_instance:
        return stopwatch_instance.start()
    return {"error": "Stopwatch not initialized"}

@app.post("/stop")
async def stop_stopwatch():
    if stopwatch_instance:
        return stopwatch_instance.stop()
    return {"error": "Stopwatch not initialized"}

@app.post("/reset")
async def reset_stopwatch():
    if stopwatch_instance:
        return stopwatch_instance.reset()
    return {"error": "Stopwatch not initialized"}

@app.post("/metrics")
async def update_metrics(hits: int = None, misses: int = None, admissions: int = None, evictions: int = None):
    if stopwatch_instance:
        return stopwatch_instance.update_metrics(hits, misses, admissions, evictions)
    return {"error": "Stopwatch not initialized"}

@app.post("/metrics/increment")
async def increment_metrics(hits: int = 0, misses: int = 0, admissions: int = 0, evictions: int = 0):
    """Increment metrics by the specified amounts"""
    if stopwatch_instance:
        with stopwatch_instance._lock:
            stopwatch_instance.hits += hits
            stopwatch_instance.misses += misses
            stopwatch_instance.admissions += admissions
            stopwatch_instance.evictions += evictions
            return {
                "hits": stopwatch_instance.hits,
                "misses": stopwatch_instance.misses,
                "admissions": stopwatch_instance.admissions,
                "evictions": stopwatch_instance.evictions
            }
    return {"error": "Stopwatch not initialized"}

@app.post("/metrics/reset")
async def reset_metrics():
    """Reset all metrics to zero"""
    if stopwatch_instance:
        return stopwatch_instance.update_metrics(hits=0, misses=0, admissions=0, evictions=0)
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
    print("  POST /start  - Start the stopwatch")
    print("  POST /stop   - Stop the stopwatch") 
    print("  POST /reset  - Reset the stopwatch")
    print("\nMetrics endpoints:")
    print("  POST /metrics - Set absolute metric values")
    print("       ?hits=100&misses=25&admissions=80&evictions=15")
    print("  POST /metrics/increment - Increment metrics by amounts")
    print("       ?hits=1&misses=0&admissions=1&evictions=0")
    print("  POST /metrics/reset - Reset all metrics to zero")
    
    root.mainloop()