import pygame
import sys
import runner

try:
    pygame.init()
    runner_instance = runner.Runner(FPS=60)

    while runner_instance.running:
        runner_instance.update()
        runner_instance.draw()    
    
    pygame.quit()
    sys.exit()

except pygame.error as e:
    print("Error initializing Pygame: ", e)
    pygame.quit()
    sys.exit()



