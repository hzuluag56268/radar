import pygame
import time
from pyproj import Geod

# Pygame initialization
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
LAT_MIN, LAT_MAX = 7.39, 8.61
LON_MIN, LON_MAX = -73.05, -72.35
CIRCLE_SPEED_KNOTS = 10800
MAX_CLIMB_ALTITUDE = 35000  # feet
CLIMB_RATE = 400  # feet per nautical mile
DESCENT_RATE = 333  # feet per nautical mile
INITIAL_DESCENT_ALTITUDE = 17000  # feet
DEFAULT_STOP_DESCENT_ALTITUDE = 6000  # feet

# Colors
COLORS = {
    "STAR": (255, 255, 0),
    "UMPEX1A": (255, 0, 255),
    "SID": (0, 0, 255),
    "DIMIL6A": (0, 128, 255),
    "HOLDING": (0, 255, 0),
}

# Pygame setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Radar Simulation")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Geod setup for geodesic calculations
geod = Geod(ellps="WGS84")

# Routes Definition
ROUTES = {
    "STAR": [
        (7.447631289561067, -72.82989420918472),
        (7.688465530734027, -72.64823713018512),
        (7.639287419149673, -72.52301723596005),
        (7.889099999999999, -72.4967)
    ],
    "UMPEX1A": [
        (7.456088668509097, -72.54229706015661),
        (7.889099999999999, -72.4967)
    ],
    "HOLDING": [
        (7.806278934049598, -72.50548625473371),
        (7.889099999999999, -72.49670000000002),
        (7.8943199144148855, -72.54686802298092),
        (7.811498848464485, -72.55565427771462),
        (7.806278934049598, -72.50548625473371)
    ],
    "SID": [
        (7.889099999999999, -72.49670000000002),
        (8.136498332446672, -72.46157677120075),
        (8.137067813159366, -72.52745630867507),
        (8.065719266656753, -72.67512201525814),
        (7.8890245252969295, -72.7489182154572),
        (7.77561941414433, -72.72136674790345),
        (7.662020799946988, -72.94591194285007)
    ],
    "DIMIL6A": [
        (7.889099999999999, -72.49670000000002),
        (8.136498332446672, -72.46157677120075),
        (8.137067813159366, -72.52745630867507),
        (8.065719266656753, -72.67512201525814),
        (8.24226127933224, -72.85369994695671)
    ]
}

# Helper Functions
def latlon_to_pixel(lat, lon):
    """Converts latitude and longitude to screen pixel coordinates."""
    x = int((lon - LON_MIN) / (LON_MAX - LON_MIN) * SCREEN_WIDTH)
    y = int((LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * SCREEN_HEIGHT)
    return x, y

def calculate_segments(waypoints):
    """Calculates pixel positions and distances for a list of waypoints."""
    pixel_points = [latlon_to_pixel(lat, lon) for lat, lon in waypoints]
    distances = [
        geod.inv(wp1[1], wp1[0], wp2[1], wp2[0])[2] / 1852
        for wp1, wp2 in zip(waypoints[:-1], waypoints[1:])
    ]
    return pixel_points, distances

def interpolate(p1, p2, t):
    """Interpolates between two points based on a ratio t (0 to 1)."""
    return (p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t)

def calculate_altitude(cumulative_distance, is_climbing, stop_altitude):
    """Calculates the altitude based on cumulative distance and climb/descent rate."""
    if is_climbing:
        return min(1000 + cumulative_distance * CLIMB_RATE, stop_altitude)
    else:
        return max(INITIAL_DESCENT_ALTITUDE - cumulative_distance * DESCENT_RATE, stop_altitude)

# Aircraft Class
class Aircraft:
    def __init__(self, route_name, is_climbing=False):
        self.route_name = route_name
        self.route, self.distances = ROUTES_PIXELS[route_name]
        self.color = COLORS[route_name]
        self.is_climbing = is_climbing
        self.current_segment = 0
        self.start_time = time.time()
        self.cumulative_distance = 0
        self.altitude = 1000 if is_climbing else INITIAL_DESCENT_ALTITUDE
        self.stop_altitude = MAX_CLIMB_ALTITUDE if is_climbing else DEFAULT_STOP_DESCENT_ALTITUDE
        self.moving_point = self.route[0]
        self.visible = True

    def update(self):
        """Updates the aircraft's position and altitude."""
        if self.current_segment >= len(self.route) - 1:
            self.visible = False
            return

        p1, p2 = self.route[self.current_segment], self.route[self.current_segment + 1]
        segment_distance = self.distances[self.current_segment]
        time_required = (segment_distance / CIRCLE_SPEED_KNOTS) * 3600
        t = min((time.time() - self.start_time) / time_required, 1)
        self.moving_point = interpolate(p1, p2, t)

        if t >= 1:  # Move to the next segment
            self.cumulative_distance += segment_distance
            self.altitude = calculate_altitude(self.cumulative_distance, self.is_climbing, self.stop_altitude)
            self.current_segment += 1
            self.start_time = time.time()

    def draw(self, screen):
        """Draws the aircraft on the screen."""
        if self.visible:
            pygame.draw.circle(screen, self.color, (int(self.moving_point[0]), int(self.moving_point[1])), 7)
            altitude_text = font.render(f"{int(self.altitude // 100)}00 ft", True, COLORS["HOLDING"])
            screen.blit(altitude_text, (int(self.moving_point[0] + 10), int(self.moving_point[1] - 10)))

# Precompute Routes
ROUTES_PIXELS = {name: calculate_segments(waypoints) for name, waypoints in ROUTES.items()}

# Main Function
def main():
    aircrafts = [
        Aircraft("STAR"),
        Aircraft("UMPEX1A"),
        Aircraft("SID", is_climbing=True),
        Aircraft("DIMIL6A", is_climbing=True),
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear screen
        screen.fill(BLACK)

        # Draw routes
        for route_name, (pixel_points, _) in ROUTES_PIXELS.items():
            for i in range(len(pixel_points) - 1):
                pygame.draw.line(screen, COLORS[route_name], pixel_points[i], pixel_points[i + 1], 2)

        # Update and draw aircraft
        for aircraft in aircrafts:
            aircraft.update()
            aircraft.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
