import tkinter as tk
import threading
import time
from fastapi import FastAPI
import uvicorn


class Stopwatch:
    def __init__(self, master):
        self.master = master
        master.title("Stopwatch")
        master.geometry("400x200")
        master.configure(bg='white')
        master.resizable(False, False)

        self.time = 0  # elapsed time in seconds
        self.running = False
        self.start_time = None
        self._lock = threading.Lock()  # Thread safety for API access

        # Time display
        self.label = tk.Label(master, text="00:00.00", 
                             font=("Menlo", 48, "normal"), 
                             fg='#2c2c2c', bg='white')
        self.label.pack(pady=50)

        # Button frame
        button_frame = tk.Frame(master, bg='white')
        button_frame.pack(pady=20)

        # Simple, clean buttons
        button_style = {
            'font': ("Helvetica", 12),
            'relief': 'flat',
            'bd': 1,
            'padx': 20,
            'pady': 8,
            'cursor': 'hand2'
        }

        self.start_button = tk.Button(button_frame, text="Start", 
                                    command=self.start,
                                    bg='#f0f0f0', fg='#333333',
                                    activebackground='#e0e0e0',
                                    **button_style)
        self.start_button.pack(side="left", padx=10)

        self.stop_button = tk.Button(button_frame, text="Stop", 
                                   command=self.stop,
                                   bg='#f0f0f0', fg='#333333',
                                   activebackground='#e0e0e0',
                                   **button_style)
        self.stop_button.pack(side="left", padx=10)

        self.reset_button = tk.Button(button_frame, text="Reset", 
                                    command=self.reset,
                                    bg='#f0f0f0', fg='#333333',
                                    activebackground='#e0e0e0',
                                    **button_style)
        self.reset_button.pack(side="left", padx=10)

        # Update the label periodically
        self.update_clock()

    def update_clock(self):
        with self._lock:
            if self.running and self.start_time:
                self.time = time.time() - self.start_time
            self.label.config(text=self.format_time(self.time))
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
                "formatted_time": self.format_time(current_time)
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
    
    print("Stopwatch GUI started!")
    print("API server running on http://127.0.0.1:9000")
    print("API endpoints:")
    print("  GET  /status - Get current stopwatch status")
    print("  POST /start  - Start the stopwatch")
    print("  POST /stop   - Stop the stopwatch") 
    print("  POST /reset  - Reset the stopwatch")
    
    root.mainloop()