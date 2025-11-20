import rpyc
import sys
import os
import types

# Configuration
# Users can set these environment variables to point to their RT machine
SERVER_IP = os.environ.get("FRANKY_SERVER_IP", "localhost")
SERVER_PORT = int(os.environ.get("FRANKY_SERVER_PORT", 18861))

# Global connection object
_conn = None

def _connect():
    global _conn
    if _conn is None:
        try:
            # sync_request_timeout=None allows blocking calls (like robot.move) to wait indefinitely
            _conn = rpyc.connect(SERVER_IP, SERVER_PORT, config={
                'sync_request_timeout': None,
                'allow_public_attrs': True,
                'allow_all_attrs': True,
            })
        except Exception as e:
            raise ImportError(f"Failed to connect to Franky server at {SERVER_IP}:{SERVER_PORT}. "
                              f"Ensure the server is running. Error: {e}")
    return _conn

# Connect immediately on import
_conn = _connect()

# Get the remote franky module
# 'modules' gives access to remote modules
if hasattr(_conn, "modules"):
    _remote_franky = _conn.modules.franky
else:
    # If using standard rpyc.connect to a SlaveService/FrankyService, 
    # we can access the module via getmodule
    _remote_franky = _conn.root.getmodule("franky")

# Populate this module's namespace with the remote module's contents
# This makes 'from franky import Robot' work
for name in dir(_remote_franky):
    # Skip private attributes/methods to avoid conflicts with local ones or rpyc internals
    if name.startswith("__") and name not in ["__version__"]:
        continue
    
    # Assign the remote attribute to the local module
    globals()[name] = getattr(_remote_franky, name)

# Handle submodules (like franky.motion)
# If the user does 'import franky.motion', it might fail because local python looks for franky/motion.py.
# However, accessing franky.motion (after import franky) works because we copied the reference.
# To support 'from franky.motion import Motion', we would need to mock the submodule structure
# or rely on the user using 'from franky import Motion' (which is supported by franky's top-level exports).

# Special case: If the remote side has __all__, respect it?
if hasattr(_remote_franky, "__all__"):
    __all__ = list(_remote_franky.__all__)
else:
    # Fallback: export everything we just copied
    __all__ = [name for name in dir(_remote_franky) if not name.startswith("__")]

