import pygame
import sys
import numpy as np
import math
import random

class Runner():
    def __init__(self, FPS=60, title="Renderer"):
        self.running = True
        self.clock = pygame.time.Clock()
        self.FPS = FPS

        self.lowest_dot = 0
        self.highest_dot = 0

        self.screen = pygame.display.set_mode((1000,1000))
        pygame.display.set_caption(title)
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()

        self.camera_pos = np.array([0.0,0.0,1.0])
        self.FOV = 90
        self.speed_x = 3
        self.speed_y = 3
        self.speed_z = 2
        self.zoom_speed = 50/self.FPS
        self.rotation_speed = 2/self.FPS

        self.light_source = np.array([0.0,0.0,101.0])
        self.light_direction = np.array([0.0,0.0,-1.0])

        self.vertices = []
        self.triangles = np.array([])
        self.triangle_relationships = []
        
        donut_file = open('donut.obj', 'r')
        for line in donut_file.readlines():
            if line.split()[0] == 'v':
                vertices = line.split()[1:]
                self.vertices.append([float(string) for string in vertices])
            if line.split()[0] == 'f':
                face = line.split()[1:]
                relative_point = []
                for triangle in face:
                    relative_point.append(triangle.split("/")[0])
                self.triangle_relationships.append([int(string) for string in relative_point])
        
        self.vertices = np.array(self.vertices) 
        self.triangle_relationships = np.array(self.triangle_relationships)

    def world_to_screen_space(self, position):
        delta_x = position[0] - self.camera_pos[0]
        delta_y = position[1] - self.camera_pos[1]
        #we expect camera z to be bigger than position z
        delta_z = self.camera_pos[2] - position[2]

        fov_scale = 1/math.tan(math.radians(self.FOV/2))

        return np.array([self.screen_width/2 * (fov_scale*delta_x/delta_z + 1), self.screen_height/2 * (-fov_scale*delta_y/delta_z + 1)])

    def get_triangles(self):
        self.triangles = []
        for list in self.triangle_relationships:
            triangle = []
            for index in list:
                # subtract 1 here because the triangle relationships given have a starting index of 1 
                triangle.append(self.world_to_screen_space(self.vertices[index - 1]))
            self.triangles.append(triangle)
    
    def get_normals(self):
        self.normals = []
        for list in self.triangle_relationships:
            vector1 = self.vertices[list[1]-1] - self.vertices[list[0]-1]
            vector2 = self.vertices[list[2]-1] - self.vertices[list[0]-1]
            normal = np.cross(vector1, vector2)
            self.normals.append(normal/np.linalg.norm(normal))

    
    def move_camera(self):
        vertical = 0
        if self.ctrl: vertical += -1
        if self.space: vertical += 1
        change_array = np.array([self.wasd[0] * self.speed_x, vertical * self.speed_y, self.wasd[1] * self.speed_z])
        self.camera_pos = self.camera_pos + change_array*(1/self.FPS)
        # subtract so that up zooms in and vice versa
        self.FOV -= self.zoom * self.zoom_speed
    
    def rotate_vertices(self):
        new_vertices = []
        z_rotation_matrix = np.array([[np.cos(self.rotation_speed), -np.sin(self.rotation_speed), 0],
                                        [np.sin(self.rotation_speed), np.cos(self.rotation_speed), 0],
                                        [0, 0, 1]])
        y_rotation_matrix = np.array([  [np.cos(self.rotation_speed), 0, np.sin(self.rotation_speed)],
                                        [0, 1, 0],
                                        [-np.sin(self.rotation_speed), 0, np.cos(self.rotation_speed)]])
        for vertex in self.vertices:
            new_position = np.matmul(z_rotation_matrix, vertex)
            new_position = np.matmul(y_rotation_matrix, new_position)
            new_vertices.append(new_position)
        self.vertices = new_vertices
    
    def get_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
        
        self.wasd = [0, 0]
        self.ctrl = False
        self.space = False
        self.zoom = 0
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_d]:
            self.wasd[0] += 1
        if pressed[pygame.K_a]:
            self.wasd[0] -= 1
        if pressed[pygame.K_w]:
            self.wasd[1] -= 1
        if pressed[pygame.K_s]:
            self.wasd[1] += 1
        if pressed[pygame.K_UP]:
            self.zoom += 1
        if pressed[pygame.K_DOWN]:
            self.zoom -= 1
        if pressed[pygame.K_LCTRL]:
            self.ctrl = True
        if pressed[pygame.K_SPACE]:
            self.space = True

    def update(self):
        self.clock.tick(self.FPS)
        
        self.get_input()
        self.move_camera()
        self.rotate_vertices()
        self.get_triangles()
        self.get_normals()

    
    def draw(self):
        rainbow = np.array([(255,0,0), (255,127,0),(255,255,0),(0,255,0),(0,255,127),(0,0,255),(127,0,255)])

        self.screen.fill((0,0,0))
        for index in range(len(self.triangles)):
            dp = np.dot(self.light_direction, self.normals[index])
            light_strength = max(-dp, 0)
            if light_strength > 0:
                # pygame.draw.polygon(self.screen, (light_strength,light_strength,light_strength), self.triangles[index])
                pygame.draw.polygon(self.screen, rainbow[4]*light_strength, self.triangles[index])
        
        font = pygame.font.Font(None, 36)
        fps_text = font.render("FPS: " + str(round(self.clock.get_fps())), True, (255,255,255))
        fov_text = font.render("FOV: " + str(round(self.FOV)), True, (255,255,255)) 
        position_text = font.render("Position: " + str(np.round(self.camera_pos,1)), True, (255,255,255))

        self.screen.blit(fps_text, (0,0))
        self.screen.blit(fov_text, (0,30))
        self.screen.blit(position_text, (00,60))

        pygame.display.update()