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

ROUTES = {
    "STAR": {
        "coordinates": [
            (7.447631289561067, -72.82989420918472),
            (7.688465530734027, -72.64823713018512),
            (7.639287419149673, -72.52301723596005),
            (7.889099999999999, -72.4967)
        ],
        "color": (255, 255, 255),
        "type": "star"
    },
    "UMPEX1A": {
        "coordinates": [
            (7.456088668509097, -72.54229706015661),
            (7.889099999999999, -72.4967)
        ],
        "color": (255, 255, 255),
        "type": "star"
    },
    "HOLDING": {
        "coordinates": [
            (7.889099999999999, -72.49670000000002),
            (7.8943199144148855, -72.54686802298092),
            (7.811498848464485, -72.55565427771462),
            (7.806278934049598, -72.50548625473371),
            (7.889099999999999, -72.49670000000002)
        ],
        "color": (255, 255, 255),
        "type": "holding"
    },
    "SID": {
        "coordinates": [
            (7.889099999999999, -72.49670000000002),
            (8.136498332446672, -72.46157677120075),
            (8.137067813159366, -72.52745630867507),
            (8.065719266656753, -72.67512201525814),
            (7.8890245252969295, -72.7489182154572),
            (7.77561941414433, -72.72136674790345),
            (7.662020799946988, -72.94591194285007)
        ],
        "color": (255, 255, 255),
        "type": "sid"
    },
    "DIMIL6A": {
        "coordinates": [
            (7.889099999999999, -72.49670000000002),
            (8.136498332446672, -72.46157677120075),
            (8.137067813159366, -72.52745630867507),
            (8.065719266656753, -72.67512201525814),
            (8.24226127933224, -72.85369994695671)
        ],
        "color": (255, 255, 255),
        "type": "sid"
    }
}
class ui():
    def __init__(self, ):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 30)
        self.left = 0 
        self.top = 0
        self.menu_options =  ["Join Holding Pattern", "Finish Holding Pattern", "Stop descent at","Continue descent to", "disregard"]
        self.cols = 1
        self.rows = len(self.menu_options)
        self.option_height = 25
        self.show_menu = False
        self.acft = None
        self.level_window_active = False
        self.string_level = ""
        self.update_level = False
        self.is_continue_descent = False
    def get_input(self, text_rect,i):

        if  text_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            if self.menu_options[i] == "Join Holding Pattern":
                self.show_menu = False
                self.acft.pending_holding_pattern = True
            if self.menu_options[i] == "Finish Holding Pattern":
                self.acft.finish_holding_pattern = True
                self.show_menu = False
            if self.menu_options[i] == "Stop descent at":
                self.show_menu = False
                self.level_window_active = True
                self.string_level = ""     
            if self.menu_options[i] == "Continue descent to":
                self.level_window_active = True
                self.show_menu = False
                self.string_level = ""     
                self.is_continue_descent = True
    def show_level(self):
        
        if self.level_window_active: 
            rect2 = pygame.Rect(0, 0 , 400,25)
            pygame.draw.rect(self.display_surface, (0, 255, 0),rect2, 0, 4) 
            pygame.draw.rect(self.display_surface, (255, 255, 255),rect2, 4, 4)

            text_surf2 = self.font.render(f"level: {self.string_level}", True, (255, 255, 100))        
            text_rect2 = text_surf2.get_rect(center = (rect2.centerx,rect2.centery))
            self.display_surface.blit(text_surf2, text_rect2)
        
    def update(self):
        if self.update_level:
             if self.is_continue_descent:
                self.acft.start_altitude = self.acft.altitude
                self.acft.cumulative_distance_to_last_descent = \
                    self.acft.partial_cumulative_distance_travelled + self.acft.cumulative_segment_distance
                self.is_continue_descent = False
                print(f"start altitude updated to {self.acft.start_altitude}")

             self.acft.desired_altitude = int(self.string_level)
             self.update_level = False
            
             print("level updated to ", self.acft.desired_altitude)
       
    def draw(self):
        if self.level_window_active:
            self.show_level()
        # bg
        if not self.show_menu:
            return
        # Dynamic placement (ensure label stays within the screen bounds)
        if self.left + 10 + self.cols * 400 > self.display_surface.get_width():
            self.left -= 10 + self.cols * 400
        if self.top + 10 + self.rows * self.option_height > self.display_surface.get_height():
            self.top -= 10 + self.rows * self.option_height
        rect = pygame.Rect(self.left + 10, self.top + 10 ,self.cols * 400, self.rows * self.option_height)
        pygame.draw.rect(self.display_surface, (0, 255, 0),rect, 0, 4)
        pygame.draw.rect(self.display_surface, (255, 255, 255),rect, 4, 4)

        # Draw menu options
        for col in range(self.cols):
            for row in range(self.rows):
                x = rect.left + rect.width / (self.cols * 2) + (rect.width / self.cols) * col
                y = rect.top + rect.height / (self.rows * 2) + (rect.height / self.rows) * row
                i = row  
                #color = COLORS['gray'] if col == index['col'] and row == index['row'] else COLORS['black']
                
                
                text_surf = self.font.render(self.menu_options[i], True, (255, 255, 100))
                text_rect = text_surf.get_rect(center = (x,y))
                self.display_surface.blit(text_surf, text_rect)
                self.get_input(text_rect,i) 
        
class Aircraft(pygame.sprite.Sprite):
    def __init__(self, groups, color, route_name, speed,label, screen, ui):  # Added `label` parameter
        super().__init__(groups)
        self.route_name = route_name
        self.start_pos = ROUTES[self.route_name]["pixel_points"][0]
        self.radius = 8
        self.color = color
        self.label = label  # Added to store a unique identifier for the aircraft
        self.creation_time = time.time()
        self.start_segment_time = time.time()
        self.speed = speed
        self.cumulative_distance_to_last_descent = 0
        self.partial_cumulative_distance_travelled = 0
        self.cumulative_distance_travelled = 0
        self.cumulative_segment_distance = 0
        self.current_segment = 0
        self.current_segment_distance_nm = 0
        self.ui = ui
        self.altitude = 17000
        self.start_altitude = 17000
        self.desired_altitude = 6000
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center= self.start_pos)
        self.moving_point = ROUTES[self.route_name]["pixel_points"][0]
        self.descent_rate = 333  # feet per nautical mile
        self.in_holding_pattern = False
        self.pending_holding_pattern = False
        self.finish_holding_pattern = False
        self.screen = screen

    def interpolate(self, p1, p2, t):
        x = p1[0] + (p2[0] - p1[0]) * t
        y = p1[1] + (p2[1] - p1[1]) * t
        return (x, y)

    def calculate_altitude(self, cumulative_distance_from_last_descent, start_altitude, desired_altitude):
        return max(start_altitude - (cumulative_distance_from_last_descent * self.descent_rate), desired_altitude)

    #
    def draw_label(self, screen, font, icon=None):
        """
        Draws a radar-style label with each piece of information displayed on a separate line.
        """
        # Define radar-green color
        radar_green = (0, 255, 0)
        background_color = (0, 50, 0)  # Dark green for the rectangle background

        # Aircraft data for the label
        label_lines = [
            f"ID: {self.label}",             # Aircraft identifier
            f"ALT: {self.altitude:.0f} ft",  # Current altitude
            f"SPEED: {self.speed} kts",      # Aircraft speed
            
        ]

        # Render each line of text
        rendered_lines = [font.render(line, True, radar_green) for line in label_lines]

        # Calculate the size of the label box
        line_height = rendered_lines[0].get_height()
        text_width = max(line.get_width() for line in rendered_lines)
        text_height = len(rendered_lines) * line_height + 6  # Add spacing between lines
        padding = 10
        rect_width = text_width + 2 * padding
        rect_height = text_height + padding
        rect_x = self.rect.centerx + 15  # Adjust placement based on aircraft position
        rect_y = self.rect.centery - rect_height // 2

        
        # Dynamic placement (ensure label stays within the screen bounds)
        if rect_x + rect_width > screen.get_width():
            rect_x = self.rect.centerx - rect_width - 15  # Move to the left if overflowing right
        if rect_y < 0:
            rect_y = 0  # Move down if overflowing top
        if rect_y + rect_height > screen.get_height():
            rect_y = screen.get_height() - rect_height  # Move up if overflowing bottom
        
        # Draw the rectangle background

        # Draw the rounded rectangle background
        pygame.draw.rect(
            screen,
            background_color,
            (rect_x, rect_y, rect_width, rect_height),
            border_radius=8  # Rounded corners
        )

        # Draw the rectangle border
        pygame.draw.rect(
            screen,
            radar_green,
            (rect_x, rect_y, rect_width, rect_height),
            width=2,
            border_radius=8
        )

        # Blit each line of text onto the rectangle
        for i, line_surface in enumerate(rendered_lines):
            line_y = rect_y + padding + i * line_height  # Position each line below the previous one
            screen.blit(line_surface, (rect_x + padding, line_y))

        # Optional: Draw an icon (e.g., a triangle for heading) next to the label
        if icon:
            icon_size = 12
            pygame.draw.polygon(
                screen,
                radar_green,
                [
                    (self.rect.centerx, self.rect.centery - icon_size // 2),
                    (self.rect.centerx + icon_size, self.rect.centery),
                    (self.rect.centerx, self.rect.centery + icon_size // 2)
                ]
            )
        
    
    def acft_clicked(self):    
        if self.ui.show_menu:
            return
        
        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(pos):
                self.ui.left = pos[0]
                self.ui.top = pos[1]
                self.ui.show_menu = True
                self.ui.acft = self   
                         
    
    def update(self):
        #self.get_input()
        
        p1, p2 = ROUTES[self.route_name]["pixel_points"][self.current_segment], \
                 ROUTES[self.route_name]["pixel_points"][self.current_segment + 1]
        self.current_segment_distance_nm = ROUTES[self.route_name]["distances"][self.current_segment]
        time_required_sec = (self.current_segment_distance_nm / self.speed) * 3600
        segment_elapsed = time.time() - self.start_segment_time
        t = min(segment_elapsed / time_required_sec, 1)
        self.moving_point = self.interpolate(p1, p2, t)
        self.rect.center = self.moving_point
        self.cumulative_segment_distance = t * self.current_segment_distance_nm
        self.cumulative_distance_travelled = \
            (self.partial_cumulative_distance_travelled + self.cumulative_segment_distance) - \
            self.cumulative_distance_to_last_descent
        self.altitude = \
            self.calculate_altitude(self.cumulative_distance_travelled, self.start_altitude, self.desired_altitude)

        if t >= 1:
            self.partial_cumulative_distance_travelled += self.current_segment_distance_nm
            self.current_segment += 1
            self.start_segment_time = time.time()
            if self.current_segment >= len(ROUTES[self.route_name]["pixel_points"]) - 1:
                if self.in_holding_pattern and self.finish_holding_pattern:
                    self.kill()
                elif not self.in_holding_pattern and self.pending_holding_pattern:
                    self.in_holding_pattern = True
                    self.current_segment = 0
                    self.route_name = "HOLDING"
                elif not self.in_holding_pattern and not self.pending_holding_pattern:
                    self.kill()
                elif self.in_holding_pattern:
                    self.current_segment = 0
        
        self.draw_label(self.screen, pygame.font.Font(None, 24))
        self.acft_clicked()
geod = Geod(ellps="WGS84")

def latlon_to_pixel(lat, lon):
    x = int((lon - LON_MIN) / (LON_MAX - LON_MIN) * SCREEN_WIDTH)
    y = int((LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * SCREEN_HEIGHT)
    return x, y

for route_name, route_data in ROUTES.items():
    pixel_points = [latlon_to_pixel(lat, lon) for lat, lon in route_data["coordinates"]]
    distances = [
        geod.inv(wp1[1], wp1[0], wp2[1], wp2[0])[2] / 1852
        for wp1, wp2 in zip(route_data["coordinates"][:-1], route_data["coordinates"][1:])
    ]
    ROUTES[route_name].update({"pixel_points": pixel_points, "distances": distances})

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Radar Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)  # Added font for aircraft labels
        self.running = True
        
        self.elapsed_time = 0
        self.all_sprites = pygame.sprite.Group()
        start_pos = ROUTES["STAR"]["pixel_points"][0]
        self.ui = ui()
        self.level_str = ""
        self.Aircraft = Aircraft
        self.aircraft_timers = [{'name':'UMPEX1A', 'time':0, 'speed':2000, 'label':'AVA1364'},
                                {'name':'STAR', 'time':0, 'speed':2000, 'label':'ava1364'},] 
        
        
        
        
        #Aircraft(self.all_sprites, (0, 100, 0), start_pos, "Aircraft-2",self.screen,self.ui)  # Added unique label for the aircraft

        
        

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    
                    if self.ui.level_window_active:
                        
                        if event.key == pygame.K_RETURN:  # Confirm input
                            print("key return pressed")
                            self.ui.level_window_active = False
                            self.ui.update_level = True
                        elif event.key == pygame.K_BACKSPACE:  # Remove last character
                            self.ui.string_level = self.ui.string_level[:-1]
                        elif event.unicode.isdigit():  # Add digit to input
                            self.ui.string_level += event.unicode

               
            
            for acft in self.aircraft_timers[:]:
                if self.elapsed_time >= acft['time']:
                    self.Aircraft(self.all_sprites, (0, 100, 0),acft['name'],acft['speed'] ,\
                                  acft['label'],self.screen,self.ui)
                    self.aircraft_timers.remove(acft)
            
            #Aircraft(self.all_sprites, (0, 100, 0), 'STAR', 10500,"AVA1364",self.screen,self.ui)  # Added unique label for the aircraft
            self.screen.fill((0, 0, 0))
            for route_name, route_data in ROUTES.items():
                for i in range(len(route_data["pixel_points"]) - 1):
                    pygame.draw.line(self.screen, route_data["color"], route_data["pixel_points"][i], route_data["pixel_points"][i + 1], 2)

            self.all_sprites.update()
            
            self.all_sprites.draw(self.screen)

            self.ui.update()
            self.ui.draw()
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    radar = Game()
    radar.run()

