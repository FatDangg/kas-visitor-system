import json
import time
import pynput
from pynput import mouse

def record_events(output_file="mouse_events.json"):
    """
    Records mouse events and saves them in a JSON file (output_file).
    Events are saved in a list, where each event has the format:
      [event_type, x, y, button_or_scroll_data, pressed_or_scroll_delta, timestamp]
    """
    events = []
    start_time = time.perf_counter()

    def on_move(x, y):
        t = time.perf_counter() - start_time
        # Store as: ['move', x, y, None, None, timestamp]
        events.append(["move", x, y, None, None, t])

    def on_click(x, y, button, pressed):
        t = time.perf_counter() - start_time
        # Store as: ['click', x, y, button, pressed, timestamp]
        events.append(["click", x, y, str(button), pressed, t])

    def on_scroll(x, y, dx, dy):
        t = time.perf_counter() - start_time
        # Store as: ['scroll', x, y, dx, dy, timestamp]
        events.append(["scroll", x, y, dx, dy, t])

    print("Recording will start in 5 seconds. Move your mouse/press/click after it starts.")
    time.sleep(5)  # Optional delay before we start capturing

    listener = mouse.Listener(
        on_move=on_move, 
        on_click=on_click,
        on_scroll=on_scroll
    )
    listener.start()
    
    try:
        print("Recording... Press Ctrl+C or close the terminal to stop.")
        # Keep the main thread alive so listener can continue to run
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping the recording...")
    finally:
        listener.stop()

    # Save recorded events to JSON
    with open(output_file, "w") as f:
        json.dump(events, f, indent=2)

    print(f"Events successfully written to {output_file}")


if __name__ == "__main__":
    record_events()  # by default saves to mouse_events.json
