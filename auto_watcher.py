import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_DIRECTORY = "./01_incoming_drops"

class MultiClientDropHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        # 🚀 MEMORY PROTECTION: Prevents OS event double-triggering anomalies
        self.recently_processed_registry = set()

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        filename = os.path.basename(filepath)
        
        # Security Guard: Only handle .csv data streams
        if not filename.lower().endswith('.csv'):
            return

        # Deduplication Check
        if filename in self.recently_processed_registry:
            return
            
        print(f"\n⚡ [WATCHER DETECTED]: '{filename}' successfully placed in drop zone.")
        print("⏳ Verification Node: Activating file-lock polling to clear OS stream buffers...")
        
        # 🚀 FIXED: Dynamic file-lock check loop replaces fragile hardcoded sleep calls
        is_file_ready = False
        retries = 0
        while not is_file_ready and retries < 12:
            try:
                # If we can append cleanly, the writing process is fully complete
                with open(filepath, 'r+b'):
                    is_file_ready = True
            except IOError:
                time.sleep(0.5)
                retries += 1

        if not is_file_ready:
            print(f"⚠️  [INGRESS WARNING]: File system locks are unresolved. Attempting processing anyway...")

        # Register file to memory before starting processing
        self.recently_processed_registry.add(filename)

        print(f"🚀 Launching core data analytics engine pipeline for: {filename}...")
        
        try:
            # Dynamically pass the exact file path to the analyzer!
            subprocess.run(["python", "analyzer.py", filepath], check=True)
            print(f"🔄 Returning to standby mode. Awaiting next data cluster drop...")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR]: Core compiler failed execution on target: {str(e)}")
        finally:
            # Clean up the high-speed registry tracking cache index after a slight delay
            time.sleep(1)
            self.recently_processed_registry.discard(filename)

if __name__ == "__main__":
    if not os.path.exists(WATCH_DIRECTORY):
        os.makedirs(WATCH_DIRECTORY)

    print(f"=======================================================")
    print(f"🌟 LIVE ENTERPRISE MULTI-CLIENT DATA PIPELINE ENGINE V2")
    print(f"=======================================================")
    print(f"[STATUS]: Active standby mode initialized.")
    print(f"[TARGET]: Monitoring directory: /{WATCH_DIRECTORY}")
    print("Awaiting raw CSV data cluster transmissions...\n")

    event_handler = MultiClientDropHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_DIRECTORY, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SYSTEM SHUTDOWN]: De-activating observer loops. Standby mode closed.")
        observer.stop()
    observer.join()