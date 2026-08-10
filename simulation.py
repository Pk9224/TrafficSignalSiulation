import random
import time
import threading
import pygame
import sys

defaultGreen = {0:10, 1:10, 2:10, 3:10}
defaultRed = 150
defaultYellow = 5
collision_detected = False
signals = []
noOfSignals = 4
currentGreen = 0   
nextGreen = (currentGreen + 1) % noOfSignals    
currentYellow = 0  

speeds = {'car': 1, 'bus': 0.75, 'truck': 0.75, 'bike': 1.25}  

x = {'right': [0, 0, 0], 'down': [755-350, 727-350, 697-350], 'left': [1400, 1400, 1400], 'up': [602-350, 627-350, 657-350], 'up2': [602+325, 627+325, 657+325], 'down2': [755+325, 727+325, 697+325]}    
y = {'right': [348-50, 370-50, 398-50], 'down': [0, 0, 0], 'left': [498-60, 466-60, 436-60], 'up': [800, 800, 800], 'up2': [800, 800, 800], 'down2': [0, 0, 0]}

vehicles = {'right': {0:[], 1:[], 2:[], 'crossed': 0, 'crossed2': 0}, 'down': {0:[], 1:[], 2:[], 'crossed': 0}, 'left': {0:[], 1:[], 2:[], 'crossed': 0, 'crossed2': 0}, 'up': {0:[], 1:[], 2:[], 'crossed': 0}, 'up2': {0:[], 1:[], 2:[], 'crossed': 0}, 'down2': {0:[], 1:[], 2:[], 'crossed': 0}}
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'bike'}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up', 4: 'up2', 5: 'down2'}

signalCoods = [(530-350, 230-60), (810-350, 230-60), (810-350, 570-60), (530-350, 570-60)]
signalTimerCoods = [(530-350, 210-60), (810-350, 210-60), (810-350, 550-60), (530-350, 550-60)]
signalCoods2 = [(530+350, 230-60), (810+350, 230-60), (810+350, 570-60), (530+350, 570-60)]
signalTimerCoods2 = [(530+350, 210-60), (810+350, 210-60), (810+350, 550-60), (530+350, 550-60)]

stopLines = {'right': 590-350, 'down': 330-50, 'left': 800+350, 'up': 535-50}
stopLines2 = {'right': 590+350, 'down2': 330-50, 'left': 800+350, 'up2': 535-50}

defaultStop = {'right': 580-350, 'down': 320-50, 'left': 810+350, 'up': 545-50}
defaultStop2 = {'right': 580+350, 'down2': 320-50, 'left': 810+350, 'up2': 545-50}
stoppingGap = 15   
movingGap = 15  

pygame.init()
simulation = pygame.sprite.Group()

class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""
        
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.collided = False
        self.crossed = 0
        if self.direction == 'right' or self.direction == 'left':
            self.crossed2 = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.image = pygame.image.load(path)

        if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0 :
            if direction == 'right':
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().width - stoppingGap        
            elif direction == 'left':
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().width + stoppingGap
            elif direction == 'down':
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().height - stoppingGap
            elif direction == 'down2':
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().height - stoppingGap
            elif direction == 'up':
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().height + stoppingGap
            elif direction == 'up2':
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().height + stoppingGap
        else:
            self.stop = defaultStop[direction] if direction in stopLines  else defaultStop2[direction]
            
        if direction == 'right':
            temp = self.image.get_rect().width + stoppingGap    
            x[direction][lane] -= temp
        elif direction == 'left':
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif direction == 'down':
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif direction == 'down2':
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif direction == 'up':
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        elif direction == 'up2':
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)

    def check_collision(self):
        """Check if the vehicle collides with any other vehicle, regardless of direction."""
        for direction in vehicles:  # Check all directions (not just the same direction)
            for lane in range(0, 3):  # Loop over all lanes
                for other_vehicle in vehicles[direction][lane]:
                    if other_vehicle != self:
                        # Ensure that the other vehicle has an image before checking for collision
                        if hasattr(other_vehicle, 'image') and hasattr(self, 'image'):
                            # Check for overlap based on their bounding boxes
                            if pygame.Rect(self.x, self.y, self.image.get_rect().width, self.image.get_rect().height).colliderect(
                                pygame.Rect(other_vehicle.x, other_vehicle.y, other_vehicle.image.get_rect().width, other_vehicle.image.get_rect().height)):
                                
                                self.collided = True
                                other_vehicle.collided = True
                                
                                # Stop both vehicles upon collision
                                self.speed = 0
                                other_vehicle.speed = 0
                                
                                # Return True to indicate a collision has occurred
                                return True
        return False

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        global collision_detected
        if self.check_collision():
            collision_detected = True
            return 
        
        ignore_red_light = random.random() < 0.01
        if self.direction == 'right':
            if self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[self.direction]: 
                self.crossed = 1
            if self.crossed2 == 0 and self.x + self.image.get_rect().width > stopLines2[self.direction]: 
                self.crossed2 = 1

            # Check if vehicle can ignore the red light and proceed
            if (self.x + self.image.get_rect().width <= self.stop or 
                (self.crossed == 1 and self.crossed2 == 1) or 
                (currentGreen == 0 and currentYellow == 0) or 
                (ignore_red_light and self.index == 0)) and (
                self.index == 0 or self.x + self.image.get_rect().width < (vehicles[self.direction][self.lane][self.index-1].x - movingGap)): 
                self.x += self.speed 

        elif self.direction == 'down':
            if self.crossed == 0 and self.y + self.image.get_rect().height > stopLines[self.direction]:
                self.crossed = 1
            if (self.y + self.image.get_rect().height <= self.stop or self.crossed == 1 or 
                (currentGreen == 1 and currentYellow == 0) or 
                (ignore_red_light and self.index == 0)) and (
                self.index == 0 or self.y + self.image.get_rect().height < (vehicles[self.direction][self.lane][self.index-1].y - movingGap)): 
                self.y += self.speed

        elif self.direction == 'down2':
            if self.crossed == 0 and self.y + self.image.get_rect().height > stopLines2[self.direction]:
                self.crossed = 1
            if (self.y + self.image.get_rect().height <= self.stop or self.crossed == 1 or 
                (currentGreen == 1 and currentYellow == 0) or 
                (ignore_red_light and self.index == 0)) and (
                self.index == 0 or self.y + self.image.get_rect().height < (vehicles[self.direction][self.lane][self.index-1].y - movingGap)): 
                self.y += self.speed

        elif self.direction == 'left':
            if self.crossed == 0 and self.x < stopLines[self.direction]:
                self.crossed = 1
            if self.crossed2 == 0 and self.x < stopLines2[self.direction]:
                self.crossed2 = 1
            if (self.x >= self.stop or 
                (self.crossed == 1 and self.crossed2 == 1) or 
                (currentGreen == 2 and currentYellow == 0) or 
                (ignore_red_light and self.index == 0)) and (
                self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap)): 
                self.x -= self.speed   

        elif self.direction == 'up':
            if self.crossed == 0 and self.y < stopLines[self.direction]:
                self.crossed = 1
            if (self.y >= self.stop or self.crossed == 1 or 
                (currentGreen == 3 and currentYellow == 0) or 
                (ignore_red_light and self.index == 0)) and (
                self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height + movingGap)): 
                self.y -= self.speed

        elif self.direction == 'up2':
            if self.crossed == 0 and self.y < stopLines2[self.direction]:
                self.crossed = 1
            if (self.y >= self.stop or self.crossed == 1 or 
                (currentGreen == 3 and currentYellow == 0) or 
                (ignore_red_light and self.index == 0)) and (
                self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height + movingGap)): 
                self.y -= self.speed

def initialize():
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red + ts1.yellow + ts1.green, defaultYellow, defaultGreen[1])
    signals.append(ts2)
    ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[2])
    signals.append(ts3)
    ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[3])
    signals.append(ts4)
    
    repeat()

def calculate_vehicle_count(direction):
    """Calculate the number of vehicles in all lanes of the given direction."""
    vehicle_count = 0
    for lane in range(0, 3):  # Loop over 3 lanes
        vehicle_count += len(vehicles[direction][lane])
    return vehicle_count

def adjust_green_light_duration():
    """Adjust the duration of the green light based on vehicle count in each direction."""
    global signals
    for direction in range(0, noOfSignals):
        vehicle_count = calculate_vehicle_count(directionNumbers[direction])
        # Base green light duration, with adjustment factor
        green_duration = defaultGreen[direction] + (vehicle_count * 2)  # Adjust as needed
        signals[direction].green = green_duration

def reset_simulation():
    global currentGreen, currentYellow, nextGreen, collision_detected
    collision_detected = False
    currentGreen = 0
    nextGreen = (currentGreen + 1) % noOfSignals
    currentYellow = 0
    for signal in signals:
        signal.green = defaultGreen[signals.index(signal)]
        signal.yellow = defaultYellow
        signal.red = defaultRed

    # Clear all vehicles from the simulation group
    simulation.empty()

    # Reset vehicle data (positions and lists)
    for direction in directionNumbers.values():
        for lane in range(0, 3):
            vehicles[direction][lane] = []

    # Reset lane positions to defaults
    global x, y
    x = {
        'right': [0, 0, 0], 
        'down': [755-350, 727-350, 697-350], 
        'left': [1400, 1400, 1400], 
        'up': [602-350, 627-350, 657-350], 
        'up2': [602+325, 627+325, 657+325], 
        'down2': [755+325, 727+325, 697+325]
    }
    y = {
        'right': [348-50, 370-50, 398-50], 
        'down': [0, 0, 0], 
        'left': [498-60, 466-60, 436-60], 
        'up': [800, 800, 800], 
        'up2': [800, 800, 800], 
        'down2': [0, 0, 0]
    }

def repeat():
    global currentGreen, currentYellow, nextGreen
    while True:
        # Adjust green light duration before starting the signal cycle
        adjust_green_light_duration()
        signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green
        # Process the current green light cycle
        while signals[currentGreen].green > 0:  
            updateValues()
            time.sleep(1)
        
        # Switch to yellow light
        currentYellow = 1  
        for i in range(0, 3):
            for vehicle in vehicles[directionNumbers[currentGreen]][i]:
                vehicle.stop = defaultStop[directionNumbers[currentGreen]]
        
        while signals[currentGreen].yellow > 0:  
            updateValues()
            time.sleep(1)
        
        # Reset the yellow light
        currentYellow = 0  

        # Reset traffic signal times
        signals[currentGreen].green = defaultGreen[currentGreen]
        signals[currentGreen].yellow = defaultYellow
        signals[currentGreen].red = defaultRed

        # Move to the next green light signal
        currentGreen = nextGreen 
        nextGreen = (currentGreen + 1) % noOfSignals    
          

def updateValues():
    for i in range(0, noOfSignals):
        if i == currentGreen:
            if currentYellow == 0:
                signals[i].green -= 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1

def generateVehicles():
    while True:
        vehicle_type = random.randint(0, 3)
        lane_number = random.randint(1, 2)
        temp = random.randint(0, 96)
        direction_number = 0
        dist = [16, 32, 48, 64, 80, 96]
        if temp < dist[0]:
            direction_number = 0
        elif temp < dist[1]:
            direction_number = 1
        elif temp < dist[2]:
            direction_number = 2
        elif temp < dist[3]:
            direction_number = 3
        elif temp < dist[4]:
            direction_number = 4
        elif temp < dist[5]:
            direction_number = 5
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number])
        time.sleep(1)

class Main:
    thread1 = threading.Thread(name="initialization", target=initialize, args=())    
    thread1.daemon = True
    thread1.start()

    black = (0, 0, 0)
    white = (255, 255, 255)

    screenWidth = 1280
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    background = pygame.image.load('images/intersection.jpg')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)

    thread2 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())    
    thread2.daemon = True
    thread2.start()
    reset_button = pygame.Rect(0, 0, 140, 40)  
    button_color = (0, 255, 0)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if reset_button.collidepoint(event.pos):
                    reset_simulation()
        screen.blit(background, (0, 0))   
        pygame.draw.rect(screen, button_color, reset_button)
        font_render = font.render("Reset", True, (0, 0, 0))
        screen.blit(font_render, (reset_button.x + 10, reset_button.y + 10))
        if collision_detected:
            collision_message = font.render("Collision Detected!.", True, (255, 0, 0))
            screen.blit(collision_message, (screenWidth // 3, screenHeight // 2))
        for i in range(0, noOfSignals):  
            if i == currentGreen:
                if currentYellow == 1:
                    signals[i].signalText = signals[i].yellow
                    screen.blit(yellowSignal, signalCoods[i])
                    screen.blit(yellowSignal, signalCoods2[i])
                else:
                    signals[i].signalText = signals[i].green
                    screen.blit(greenSignal, signalCoods[i])
                    screen.blit(greenSignal, signalCoods2[i])
            else:
                if signals[i].red <= 10:
                    signals[i].signalText = signals[i].red
                else:
                    signals[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])
                screen.blit(redSignal, signalCoods2[i])

        signalTexts = ["", "", "", "", "", "", "", ""]
        
        for i in range(0, noOfSignals):  
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i], signalTimerCoods[i])
            screen.blit(signalTexts[i], signalTimerCoods2[i])

        for vehicle in simulation:  
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()
        pygame.display.update()

Main()
