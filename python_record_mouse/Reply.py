import json
import time
import pynput
from pynput.mouse import Button, Controller

def replay_events(events_file="mouse_events.json", speed_factor=1, start_position=(100, 100)):
    """
    Reads a JSON file with recorded mouse events and replays them.
    
    Args:
        events_file: Path to the JSON file containing recorded events.
        speed_factor: 0.1 means 10x faster replay (original time intervals * 0.1).
        start_position: Coordinates to move the mouse to before playback.
    """
    print("Recording will start in 5 seconds. Move your mouse/press/click after it starts.")
    time.sleep(5)  # Optional delay before we start capturing
    # 1. Load events
    with open(events_file, 'r') as f:
        events = json.load(f)

    mouse_controller = Controller()

    # 2. Fixed starting position (optional)
    mouse_controller.position = start_position
    print(f"Starting position set to {start_position}")

    # 3. Replay loop
    # The events are stored with timestamps in the last position of the list: [event_type, x, y, something, something, event_time]
    # We'll track the previous event time to know how long to wait.
    if not events:
        print("No events to replay. Exiting.")
        return

    start_time = events[0][-1]  # The timestamp of the very first event

    print(f"Replaying events from {events_file} at speed factor = {speed_factor} (lower = faster).")
    for event in events:
        event_type = event[0]      # "move", "click", or "scroll"
        x = event[1]
        y = event[2]
        extra_1 = event[3]        # Could be button for "click" or dx for "scroll"
        extra_2 = event[4]        # Could be pressed for "click" or dy for "scroll"
        event_time = event[-1]    # The timestamp

        # Calculate how long to wait before replaying this event
        wait_time = (event_time - start_time) * speed_factor
        time.sleep(wait_time)

        # Replay the event
        if event_type == "move":
            mouse_controller.position = (x, y)

        elif event_type == "click":
            # extra_1 = button, extra_2 = pressed (bool)
            button = Button.left if extra_1 == 'Button.left' else Button.right
            if extra_2:  # If pressed
                mouse_controller.press(button)
            else:  # If released
                mouse_controller.release(button)

        elif event_type == "scroll":
            # extra_1 = dx, extra_2 = dy
            dx = extra_1
            dy = extra_2
            mouse_controller.scroll(dx, dy)

        # Update reference time to the current event
        start_time = event_time

    print("Mouse/trackpad events replayed.")


if __name__ == "__main__":
    # By default, replay at 10x speed and starting at (100, 100).
    #  speed_factor=0.1 -> Wait time is 0.1 * (original_time_delta)
    replay_events(events_file="mouse_events.json", speed_factor=0.2, start_position=(100, 100))
