from argparse import ArgumentParser
from time import sleep

# Set server IP before importing franky (connection happens at import time)
# You can also set FRANKY_SERVER_PORT if needed
# os.environ.setdefault("FRANKY_SERVER_IP", "192.168.1.100")  # Uncomment and set your server IP
# os.environ.setdefault("FRANKY_SERVER_PORT", "18861")  # Optional: change port

from franky import Affine, Robot


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--host", default="172.16.0.2", help="FCI IP of the robot")
    args = parser.parse_args()

    robot = Robot(args.host)

    while True:
        state = robot.state
        print("\nPose: ", robot.current_pose)
        print("O_TT_E: ", state.O_T_EE)
        print("Joints: ", state.q)
        print("Elbow: ", state.elbow)
        sleep(0.05)
