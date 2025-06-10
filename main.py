
import glfw
from OpenGL.GL import *
from PIL import Image, ImageDraw, ImageFont
import random
import time
import winsound

mouse_pos = (0.0, 0.0)
score = 0
bullets = 10
ducks = []
game_over = False
PATOS = 5
PATOS_A_MAIS = 0
PATOS_SPEED_A_MAIS = 0.002

def new_duck(): return {
   "x": -1.2,
   "y": random.uniform(-0.7, 0.95),
   "speed": random.uniform(0.001, 0.002),
   "texture": None,
   "state": "flying_0",
   "death_animation_cd": 30,
}

pallete = {
    "background": (59/255, 187/255, 250/255, 1.0)
}

def load_texture(path):
    img = Image.open(path).convert("RGBA")
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = img.tobytes()
    width, height = img.size

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id, width, height

def create_text_texture(text, font_path=None, font_size=32, color=(255,255,255,255)):
    font = ImageFont.truetype(font_path or "./teachers/dejavu-fonts-ttf-2.37/ttf/DejaVuSans.ttf", font_size)
    dummy_img = Image.new("RGBA", (1,1))
    dummy_draw = ImageDraw.Draw(dummy_img)
    bbox = dummy_draw.textbbox((0, 0), text, font=font)
    text_size = (bbox[2] - bbox[0], bbox[3])
    img = Image.new("RGBA", text_size, (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.text((0,0), text, font=font, fill=color)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = img.tobytes()
    width, height = img.size

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id, width, height

def draw_background():
    glClearColor(*pallete["background"])

def draw_with_texture(bottom_left, bottom_right, top_right, top_left, texture=None):
    if texture:
        # Para respeitar a transparência da imagem
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex2f(bottom_left[0], bottom_left[1])
        glTexCoord2f(1, 0)
        glVertex2f(bottom_right[0], bottom_right[1])
        glTexCoord2f(1, 1)
        glVertex2f(top_right[0], top_right[1])
        glTexCoord2f(0, 1)
        glVertex2f(top_left[0], top_left[1])
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)

def draw_text_texture(bottom_left, bottom_right, top_right, top_left, tex_id):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(*bottom_left)
    glTexCoord2f(1, 0); glVertex2f(*bottom_right)
    glTexCoord2f(1, 1); glVertex2f(*top_right)
    glTexCoord2f(0, 1); glVertex2f(*top_left)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)

def draw_crosshair(x, y, size=0.05, gap=0.01):
    glColor3f(1, 1, 1)
    glLineWidth(2)
    glBegin(GL_LINES)

    # Horizontal left
    glVertex2f(x - size, y)
    glVertex2f(x - gap, y)
    # Horizontal right
    glVertex2f(x + gap, y)
    glVertex2f(x + size, y)
    # Vertical top
    glVertex2f(x, y + gap)
    glVertex2f(x, y + size)
    # Vertical bottom
    glVertex2f(x, y - gap)
    glVertex2f(x, y - size)
    glEnd()

def mouse_button_callback(window, button, action, mods):
    global score, bullets, game_over
    if(button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS):
        winsound.PlaySound("shot.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        if bullets <= 0:
            print("Acabaram as balas!")
            return
        bullets -= 1
        if bullets == 0:
            print("Sem balas! Game Over!")
            game_over = True
            return
        for duck in ducks:
            if (duck["x"] - 0.075 <= mouse_pos[0] <= duck["x"] + 0.075 and
                duck["y"] - 0.075 <= mouse_pos[1] <= duck["y"] + 0.075 and duck["state"] != "dead" and duck["state"] != "hit"):
                duck["state"] = "hit"
                score += 100
                break

def cursor_pos_callback(window, xpos, ypos):
    global mouse_pos
    width, height = glfw.get_window_size(window)

    mouse_pos = ((xpos / width) * 2 - 1, -((ypos / height) * 2 - 1))

def load_all_textures():
    textures = {}
    textures["duck"] = load_texture("./teachers/fabio.jpg")
    textures["hit_duck"] = load_texture("./teachers/fabiohit.png")
    textures["dead_duck"] = load_texture("./teachers/fabiodead.png")
    textures["grass"] = load_texture("./sprites/spr_floor.png")
    textures["bush"] = load_texture("./sprites/spr_bush.png")
    textures["tree"] = load_texture("./sprites/spr_tree.png")
    textures["bullet"] = load_texture("./sprites/bullet.png")
    return textures

def get_quad_corners(center_x, center_y, desired_width, img_width, img_height):
    aspect = img_height / img_width
    half_w = desired_width / 2
    half_h = (desired_width * aspect) / 2

    return [
        (center_x - half_w, center_y - half_h),  # bottom left
        (center_x + half_w, center_y - half_h),  # bottom right
        (center_x + half_w, center_y + half_h),  # top right
        (center_x - half_w, center_y + half_h),  # top left
    ]

def update_ducks(delta_time, textures):
    global score, game_over
    dead_ducks = 0

    for duck in ducks:
        duck["x"] += duck["speed"]  * delta_time * 120

        if duck["state"] == "hit":
            duck["texture"] = textures["hit_duck"][0]
            duck["speed"] = 0.0
            duck["death_animation_cd"] -= 1
        
        if duck["death_animation_cd"] <= 0:
            duck["texture"] = textures["dead_duck"][0]
            duck["state"] = "dead"
            duck["y"] -= 0.0015

        if duck["state"] == "dead":
            duck["y"] -= 0.0015
            dead_ducks += 1
           

        if duck["x"] > 1.2 and duck["state"] != "dead" and duck["state"] != "hit":
            print("Um pato escapou! Game Over!")
            game_over = True
            return

    # Quando todos os patos estiverem mortos: começa nova wave
    if dead_ducks == len(ducks):
        global bullets
        bullets = 10
        global PATOS, PATOS_A_MAIS, PATOS_SPEED_A_MAIS
        PATOS_A_MAIS += 1
        PATOS_SPEED_A_MAIS += 0.0004

        if(PATOS_A_MAIS >= 4): PATOS_A_MAIS = 4

        for i in range(0, (PATOS + PATOS_A_MAIS)):
            new = new_duck()
            # Aumentar a velocidade proporcional ao número da wave
            new["speed"] += PATOS_SPEED_A_MAIS  # Aumenta a velocidade base
            new["texture"] = textures["duck"][0]
            ducks.append(new)

def load_all_textures():
    textures = {}
    textures["duck"] = load_texture("./teachers/fabio.jpg")
    textures["hit_duck"] = load_texture("./teachers/fabiohit.png")
    textures["dead_duck"] = load_texture("./teachers/fabiodead.png")
    textures["grass"] = load_texture("./sprites/spr_floor.png")
    textures["bush"] = load_texture("./sprites/spr_bush.png")
    textures["tree"] = load_texture("./sprites/spr_tree.png")
    textures["bullet"] = load_texture("./sprites/bullet_2.png")
    return textures


def draw_bullets(bullets_left, textures):
    bullet_tex, w, h = textures["bullet"]
    spacing = 0.07
    start_x = -1 + spacing
    y = 0.9
    for i in range(bullets_left):
        corners = get_quad_corners(start_x + i * spacing, y, 0.05, w, h)
        draw_with_texture(*corners, texture=bullet_tex)

def draw_game_over():
    text = f"IT'S OVER!\nPONTOS: {score}"
    tex_id, w, h = create_text_texture(text, font_size=64, color=(255, 0, 0, 255))
    corners = get_quad_corners(0, 0, 0.6, w, h)
    draw_text_texture(*corners, tex_id)

def main():
    glfw.init()
    window = glfw.create_window(900, 900, "HuntXHunt", None, None)
    glfw.make_context_current(window)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_HIDDEN)

    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)

    draw_background()
    textures = load_all_textures()

    global game_over

    grass_texture, _, _ = textures["grass"]
    bush_texture, bush_w, bush_h = textures["bush"]
    tree_texture, tree_w, tree_h = textures["tree"]
    duck_texture, duck_w, duck_h = textures["duck"]
    
    for _ in range(PATOS):
        duck = new_duck()
        duck["texture"] = duck_texture    
        ducks.append(duck)

    last_time = time.time()
    game_over_display_time = 0  # para controlar quanto tempo mostrar o game over

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)
        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time

        if not game_over:
            update_ducks(delta_time, textures)

            # desenhar cenário e elementos
            draw_with_texture(*get_quad_corners(-0.5, -0.45, 0.5, tree_w, tree_h), tree_texture)
            draw_with_texture(*get_quad_corners(0.6, -0.76, 0.2, bush_w, bush_h), bush_texture)
            draw_with_texture((-1, -1), (1, -1), (1, -0.75), (-1, -0.75), grass_texture)
            
            # desenhar score
            score_tex, score_w, score_h = create_text_texture(f"Score: {score}")
            draw_text_texture(*get_quad_corners(0, 0.9, 0.3, score_w, score_h), score_tex)

            # desenhar patos
            for duck in ducks:
                draw_with_texture(*get_quad_corners(duck["x"], duck["y"], 0.15, duck_w, duck_h), duck["texture"])     
            
            # desenhar balas
            draw_bullets(bullets, textures)

            # desenhar mira
            draw_crosshair(*mouse_pos)

        else:
            # game over: desenha o texto GAME OVER
            draw_game_over()
            game_over_display_time += delta_time

            # após 3 segundos, fecha a janela
            if game_over_display_time > 3:
                glfw.set_window_should_close(window, True)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if(__name__ == "__main__"):
    main()
