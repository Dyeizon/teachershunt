import glfw
from OpenGL.GL import *
import math
import random

pallete = {
    "background": (59/255, 187/255, 250/255, 1.0),
    "dirt": (140/255,107/255,0/255,255/255),
    "grass": (124/255,190/255,5/255,255/255),
    "green": (0, 1, 0),
    "blue": (0, 0, 1),
    "yellow": (1, 1, 0),
    "cyan": (0, 1, 1),
    "magenta": (1, 0, 1)
}

def draw_background():
    glClearColor(*pallete["background"])

def draw_dirt(start=1, height=0.3):
    glColor4f(*pallete["dirt"])
    glBegin(GL_QUADS)
    glVertex2f(-1, -start)
    glVertex2f(1, -start)
    glVertex2f(1, height-1)
    glVertex2f(-1, height-1)
    glEnd()

def draw_grass(start=1, height=0.3):
    glColor4f(*pallete["grass"])
    glBegin(GL_QUADS)
    glVertex2f(-1, -start)
    glVertex2f(1, -start)
    glVertex2f(1, height-1)
    glVertex2f(-1, height-1)
    glEnd()

def draw_floor(heightDirt, heightGrass, start=1):
    draw_dirt(start=start, height=heightDirt)
    draw_grass(start=start-heightDirt, height=heightDirt+heightGrass)

def desenha():
    glPushMatrix()

    glPopMatrix()

    glFlush()

def teclado(window, key, scancode, action, mods):
    pass


def main():
    glfw.init()
    window = glfw.create_window(900, 900, "HuntXHunt", None, None)
    glfw.make_context_current(window)
    glfw.set_key_callback(window, teclado)

    draw_background()

    while glfw.window_should_close(window) == False:
        glClear(GL_COLOR_BUFFER_BIT)
        #desenha()
        draw_floor(heightDirt=0.2, heightGrass=0.3)
        glfw.swap_buffers(window)
        glfw.poll_events()
   
    glfw.terminate()

if(__name__ == "__main__"):
    main()

