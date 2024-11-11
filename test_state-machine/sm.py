import graphviz
import time

class StateMachine:
    def __init__(self, states, transitions, initial_state):
        self.states = states
        self.transitions = transitions
        self.initial_state = initial_state
        self.current_state = initial_state

    def trigger(self, event):
        state_transitions = self.transitions.get(self.current_state, {})
        if event in state_transitions:
            next_state, condition, callback = state_transitions[event]
            if condition is None or condition():
                self.perform_transition(next_state, event, callback)
            else:
                print(f"Blocking transition: waiting for condition to be met to transition from {self.current_state} to {next_state}")
                while not condition():
                    time.sleep(0.1)  # Small delay to avoid busy-waiting
                self.perform_transition(next_state, event, callback)
        else:
            raise ValueError(f"Invalid event '{event}' for state '{self.current_state}'")

    def perform_transition(self, next_state, event, callback):
        # Execute the transition callback if it exists
        if callback:
            callback(event)

        # Change the state
        self.current_state = next_state

    def get_state(self):
        return self.current_state

    def draw(self, filename='state_machine'):
        dot = graphviz.Digraph(format='png')

        # Add states as nodes
        for state in self.states:
            dot.node(state)

        # Add transitions as edges
        for state, events in self.transitions.items():
            for event, (next_state, _, _) in events.items():
                dot.edge(state, next_state, label=event)

        # Mark the initial state
        dot.node(self.initial_state, shape='doublecircle')

        # Render the diagram to a file
        dot.render(filename, cleanup=True)

# Example usage:
if __name__ == "__main__":
    states = ['idle', 'info', 'details']

    def condition_met():
        # Example condition that becomes true after 5 seconds
        return time.time() > start_time + 5

    def on_start(event):
        print(f"Transitioned from idle to running on event: {event}")

    def on_stop(event):
        print(f"Transitioned from running to stopped on event: {event}")

    def volume_change(event):
        print(f"info volume change")
    
    def first_details(event):
        print(f"first details")
    
    def next_details(event):
        print(f"next details")
    
    transitions = {
        'idle': {
            'get_info': ('info', None, on_start),
            'get_details': ('details', None, on_start),
                 },
        'info': {
            'end_of_sound': ('idle', condition_met, on_stop),  # Blocking transition
            'volume_change': ('info', None, volume_change),
            'get_details': ('details', None, first_details),
                 },
        'details': {
            'end_of_sound': ('idle', condition_met, on_stop),  # Blocking transition
            'get_next_details': ('details', None, next_details),
            'get_info': ('info', None, on_start),
            }
    }

    sm = StateMachine(states, transitions, 'idle')

    start_time = time.time()

    print(sm.get_state())  # Output: idle

    sm.trigger('get_info')
    print(sm.get_state())  # Output: running (and "Transitioned from idle to running on event: start" is printed)

    sm.trigger('volume_change')  # This will block until condition_met() returns True
    print(sm.get_state())  # Output: stopped (after 5 seconds, and "Transitioned from running to stopped on event: stop" is printed)

    sm.trigger('get_details')
    print(sm.get_state())  # Output: idle

    # Draw the state machine diagram
    sm.draw('state_machine_diagram')
