# Remote Franky

This solution allows you to run your Python Franky code on a workstation (client) while the actual robot control happens on a real-time enabled machine (server).

## Architecture

- **Server**: Runs on the real-time machine. It hosts the actual `franky` library and exposes it via RPyC.
- **Client**: Runs on your workstation. It installs a "fake" `franky` package that transparently forwards all calls to the server.

## Setup

### 1. Server Side (Real-time Machine)

1. Ensure `franky` is installed and working.
2. Install `rpyc`:
   ```bash
   pip install rpyc
   ```
3. Run the server script:
   ```bash
   python3 remote_franky/server/run.py
   ```
   (You can set the port via `FRANKY_SERVER_PORT` env var, default is 18861)

### 2. Client Side (Workstation)

1. Install `rpyc`:
   ```bash
   pip install rpyc
   ```
2. Install the client package:
   ```bash
   cd remote_franky/client
   pip install -e .
   ```
   *Note: If you already have `franky` installed on the client, you should uninstall it first to avoid conflicts, or rely on PYTHONPATH precedence.*

3. Configure the connection:
   Set the environment variable `FRANKY_SERVER_IP` to the IP of your server.
   ```bash
   export FRANKY_SERVER_IP=192.168.1.X
   ```

### Usage

Run your scripts exactly as before!

```python
from franky import Robot, JointMotion

# This connects to the remote server, which connects to the robot
robot = Robot("172.16.0.2") 

motion = JointMotion([0, 0, 0, -1.5, 0, 1.5, 0])
robot.move(motion)
```

## How it works

The client `franky` package connects to the server upon import. It then populates its own namespace with references to the server's `franky` objects. When you create a `Robot` or `Motion` object, you are actually creating it on the server. All method calls are forwarded over the network.

