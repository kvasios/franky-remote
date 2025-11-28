import rpyc
from rpyc.utils.server import ThreadedServer
from rpyc.core import SlaveService
import os
import time
import argparse
import math

# Ensure franky is installed and importable on the server
try:
    import franky
    print(f"Successfully imported franky version {franky.__version__ if hasattr(franky, '__version__') else 'unknown'}")
except ImportError:
    print("Error: 'franky' package is not installed or not found in PYTHONPATH.")
    print("Please ensure you are running this server in the environment where franky is installed.")
    exit(1)

class FrankyService(SlaveService):
    """
    A service that exposes the franky module and allows full access.
    SlaveService is used to allow the client to import arbitrary modules (like franky).
    """
    def on_connect(self, conn):
        print(f"Client connected: {conn}")

    def on_disconnect(self, conn):
        print("Client disconnected")

if __name__ == "__main__":
    # Attempt to promote to Real-Time scheduler (SCHED_FIFO)
    try:
        # SCHED_FIFO requires root privileges. 
        # We pick a priority of 80 (range is 1-99, 99 is highest).
        param = os.sched_param(80)
        os.sched_setscheduler(0, os.SCHED_FIFO, param)
        print("Successfully set Real-Time Scheduler (SCHED_FIFO, Priority 80).")
    except Exception as e_rt:
        print(f"Warning: Could not set SCHED_FIFO: {e_rt}")
        print("Falling back to nice/process priority...")
        
        # Fallback: Attempt to increase process "niceness"
        try:
            os.nice(-20)
            print("Successfully set process priority to -20 (High Priority).")
        except Exception as e_nice:
            print(f"Warning: Could not set process priority: {e_nice}")
            print("Consider running with 'sudo' for real-time performance.")

    PORT = int(os.environ.get("FRANKY_SERVER_PORT", 18861))
    
    parser = argparse.ArgumentParser(description="Franky Remote Server")
    parser.add_argument("--persistent", action="store_true", help="Keep restarting the server on failure (infinite retries).")
    parser.add_argument("--retries", type=int, default=0, help="Number of retries before exiting (default: 0). Ignored if --persistent is set.")
    args = parser.parse_args()

    if args.persistent:
        max_retries = math.inf
    else:
        max_retries = args.retries

    retry_count = 0

    while retry_count <= max_retries:
        try:
            print(f"Starting Franky RPC Server on port {PORT}...")
            
            # protocol_config with allow_all_attrs=True is crucial for accessing internal attributes if needed
            # and for the proxying to feel "transparent".
            t = ThreadedServer(FrankyService, port=PORT, protocol_config={
                'allow_all_attrs': True,
                'allow_public_attrs': True,
                'allow_setattr': True,
                'allow_delattr': True,
                'allow_pickle': True, # Useful for numpy arrays if passed by value
            })
            t.start()
            # If server stops cleanly, we assume we shouldn't restart unless intended otherwise.
            # Typically start() blocks until close() is called or an exception raised.
            break
        except Exception as e:
            # Check if we should retry
            if not args.persistent and retry_count >= max_retries:
                 print(f"Server crashed with error: {e}")
                 print(f"Max retries ({max_retries}) reached. Exiting.")
                 raise e
            
            retry_count += 1
            print(f"Server crashed with error: {e}")
            
            wait_time = 1
            retry_msg = f"{retry_count}/{max_retries}" if not args.persistent else f"{retry_count}/inf"
            print(f"Attempting recovery ({retry_msg}) in {wait_time} seconds...")
            time.sleep(wait_time)

