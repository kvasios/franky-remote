# Franky Remote

This solution allows you to run your Python Franky code on a workstation (client) while the actual robot control happens on a real-time enabled machine (server).

## Architecture

- **Server**: Runs on the real-time machine. It hosts the actual `franky` library and exposes it via RPyC.
- **Client**: Runs on your workstation. It installs a "fake" `franky` package that transparently forwards all calls to the server.

## Attribution & License

This project wraps the **Franky** library created by **Tim Schneider**.
- **Original Library**: [https://github.com/TimSchneider42/franky](https://github.com/TimSchneider42/franky)
- **License**: The core `franky-remote` code is licensed under **MIT**. However, the examples directory includes code from the original `franky` repository which is licensed under **LGPL-3.0**.

If you use this project, please credit the original authors of `franky`.

## Setup

### 1. Server Side (Real-time Machine)

#### Option A: Using Servobox (Recommended)

If you are using [Servobox](https://servobox.dev) to manage your real-time environment, you can simply run:

```bash
# For Franka Emika Panda (Gen1)
servobox pkg-install franky-remote-gen1
servobox run franky-remote-gen1  # This will auto-spin the server

# For Franka Research 3 (FR3)
servobox pkg-install franky-remote-fr3
servobox run franky-remote-fr3
```

#### Option B: Manual Setup

1. Ensure `franky` is installed and working.
2. Install `rpyc`:
   ```bash
   pip install rpyc
   ```
3. Run the server script (preferably with sudo for Real-Time scheduling):
   ```bash
   # Runs with SCHED_FIFO priority if possible
   sudo python3 server/run.py
   ```
   (You can set the port via `FRANKY_SERVER_PORT` env var, default is 18861)

### 2. Client Side (Workstation)

1. Install `rpyc`:
   ```bash
   pip install rpyc
   ```
2. Install the client package:
   
   **From source (development):**
   ```bash
   pip install -e .
   ```

   **Directly from GitHub:**
   ```bash
   pip install git+https://github.com/YOUR_USERNAME/franky-remote.git
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
