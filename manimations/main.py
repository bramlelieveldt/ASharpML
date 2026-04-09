from manim import *
import numpy as np

def main():
    print("Hello from manimations!")

N = 1000 # Amount of particles

class SquareToCircle(Scene):
    def construct(self):
        # Get scene dimensions for reference
        width = self.camera.frame_width   # ~14.222
        height = self.camera.frame_height # 8
        
        # Store dots in a list so we can access them later
        dots = []
        initial_positions = []
        
        for i in range(N):
            # Create a random point within the scene dimensions
            x = np.random.uniform(-width/2, width/2)
            y = np.random.uniform(-height/2, height/2)
            dot = Dot(point=(x, y, 0), color=BLUE)  # Create a dot at the random position
            dots.append(dot)
            initial_positions.append([x, y, 0])
            self.add(dot)  # Add the dot to the scene
        
        time_tracker = ValueTracker(0)

        def sin_dot(dot, dt, wl, freq, A, initial_pos):
            t = time_tracker.get_value()
            x_0 = initial_pos[0]  # Initial x position
            y_0 = initial_pos[1]  # Initial y position
            # Sine wave motion along x-axis
            x = x_0 + A * np.sin(2*np.pi*x_0/wl - 2*np.pi*freq*t)
            y = y_0
            dot.move_to([x, y, 0])

        # Create updaters for each dot with different wavelengths and frequencies
        wl = 1
        freq = 0.2
        A = 0.2
        
        for i, dot in enumerate(dots):
            dot.add_updater(lambda d, dt, w=wl, f=freq, A=A, pos=initial_positions[i]: sin_dot(d, dt, w, f, A, pos))

        # Animate the time tracker to create motion
        self.play(time_tracker.animate.set_value(4 * PI), run_time=4, rate_func=linear)
        
        # Remove updaters to stop motion
        for dot in dots:
            dot.clear_updaters()

