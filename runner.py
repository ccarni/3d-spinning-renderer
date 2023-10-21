import pygame
import sys
import numpy as np
import math
import random

class Runner():
    def __init__(self, FPS=60):
        self.running = True
        self.clock = pygame.time.Clock()
        self.FPS = FPS

        self.lowest_dot = 0
        self.highest_dot = 0

        self.screen = pygame.display.set_mode((1000,1000))
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()

        self.camera_pos = np.array([0.0,0.0,100.0])
        self.FOV = 90
        self.speed = 100

        self.rotation_speed = 2/self.FPS

        self.light_source = np.array([0.0,0.0,101.0])
        self.light_direction = np.array([0.0,0.0,-1.0])

        self.vertices = np.array([
            [0.0,0.0,0.0],
            [4.0,0.0,0.0],
            [4.0,4.0,0.0],
            [0.0,4.0,0.0],
            [0.0,0.0,-4.0],
            [4.0,0.0,-4.0],
            [4.0,4.0,-4.0],
            [0.0,4.0,-4.0],   
        ])

        self.triangle_relationships = [
             #front
            [0,1,2,0],
            [0,2,3,0],
            #right
            [1,5,6,1],
            [1,6,2,1],
            #top
            [3,2,6,3],
            [3,6,7,3],

            #bottom
            [4,5,1,4],
            [4,1,0,4],
            #left
            [4,0,3,4],
            [4,3,7,4],
            #back
            [5,4,7,5],
            [5,7,6,5]
        ]
        

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
                triangle.append(self.world_to_screen_space(self.vertices[index]))
            self.triangles.append(triangle)
    
    def get_normals(self):
        self.normals = []
        for list in range(len(self.triangle_relationships)):
            vector1 = self.vertices[self.triangle_relationships[list][1]] - self.vertices[self.triangle_relationships[list][0]]
            vector2 = self.vertices[self.triangle_relationships[list][2]] - self.vertices[self.triangle_relationships[list][0]]
            normal = np.cross(vector1, vector2)
            self.normals.append(normal/np.linalg.norm(normal))

    
    def move_camera(self, wasd, ctrl, space):
        vertical = 0
        if ctrl: vertical += -1
        if space: vertical += 1
        change_array = self.speed * np.array([wasd[0], vertical, wasd[1]])
        self.camera_pos = self.camera_pos + change_array*(1/self.FPS)
    
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

    def update(self):
        self.clock.tick(self.FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
        
        wasd = [0, 0]
        ctrl = False
        space = False
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_d]:
            wasd[0] += 1
        if pressed[pygame.K_a]:
            wasd[0] -= 1
        if pressed[pygame.K_w]:
            wasd[1] -= 1
        if pressed[pygame.K_s]:
            wasd[1] += 1
        if pressed[pygame.K_LCTRL]:
            ctrl = True
        if pressed[pygame.K_SPACE]:
            space = True
    
        self.move_camera(wasd, ctrl, space)
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
                pygame.draw.polygon(self.screen, rainbow[math.floor(index/2)]*light_strength, self.triangles[index])
        pygame.display.update()