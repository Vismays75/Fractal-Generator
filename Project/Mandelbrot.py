import numpy as np
import pygame as pg
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer


vertex_shader_src = '''
#version 460 core

layout(location = 0) in vec3 vertPos;

out vec2 fragCoord;


void main(){
        gl_Position = vec4(vertPos, 1);
        fragCoord = vertPos.xy * 0.5 + 0.5;  // Convert to range [0,1]
}
'''

fragment_shader_src = '''

#version 460 core

uniform int max_iterations;
uniform vec2 resolution;
uniform vec2 offset;
uniform float zoom;

in vec2 fragCoord;
out vec4 color;

int mandelbrot(vec2 c) {
    vec2 z = vec2(0.0, 0.0);
    int iterations = 0;

    while (iterations < max_iterations) {
        float x = z.x * z.x - z.y * z.y + c.x;
        float y = 2.0 * z.x * z.y + c.y;
        z = vec2(x, y);

        if (dot(z, z) > 4.0) break; // Escape condition

        iterations++;
    }
    return iterations;
}

vec3 map_color(float t) {
    vec3 color1 = vec3(0.0, 0.0, 0.0);  // Black
    vec3 color2 = vec3(0.0, 0.0, 1.0);  // Blue
    vec3 color3 = vec3(0.0, 1.0, 1.0);  // Cyan
    vec3 color4 = vec3(0.0, 1.0, 0.0);  // Green
    vec3 color5 = vec3(1.0, 1.0, 0.0);  // Yellow
    vec3 color6 = vec3(1.0, 0.0, 0.0);  // Red
    vec3 color7 = vec3(1.0, 1.0, 1.0);  // White

    if (t < 0.16) {
        return mix(color1, color2, t / 0.16); // Black to Blue
    } else if (t < 0.32) {
        return mix(color2, color3, (t - 0.16) / 0.16); // Blue to Cyan
    } else if (t < 0.48) {
        return mix(color3, color4, (t - 0.32) / 0.16); // Cyan to Green
    } else if (t < 0.64) {
        return mix(color4, color5, (t - 0.48) / 0.16); // Green to Yellow
    } else if (t < 0.80) {
        return mix(color5, color6, (t - 0.64) / 0.16); // Yellow to Red
    } else {
        return mix(color6, color7, (t - 0.80) / 0.20); // Red to White
    }
}



void main() {
    vec2 uv = (gl_FragCoord.xy / resolution) * 2.0 - 1.0;
    uv.x *= resolution.x / resolution.y;
    vec2 c = uv * zoom + offset;
    
    int iter = mandelbrot(c);

    // If inside the Mandelbrot set, colours it black; otherwise, colours it with the mix of black and blue
    if (iter == max_iterations) {
        color = vec4(0.0, 0.0, 0.0, 1.0); // Black for inside the set
    } else {
        float t = float(iter) / float(max_iterations);
        color = vec4(map_color(t), 1.0);


    }
}

'''
    
def create_shader(shader_type, source): #function to create shader
    shader = glCreateShader(shader_type) 
    glShaderSource(shader, source) #set the source code of the shader
    glCompileShader(shader) #compile the shader
    
    result = glGetShaderiv(shader, GL_COMPILE_STATUS) #check if shader compiled successfully
    if not result:
        raise Exception(glGetShaderInfoLog(shader)) #error message if shader fails to compile
    
    return shader

def create_program(vertex_shader, fragment_shader): #function to create program
    program = glCreateProgram()  #create a program
    glAttachShader(program, vertex_shader) #attach the vertex shader to the program
    glAttachShader(program, fragment_shader) #attach the fragment shader to the program
    glLinkProgram(program) #link the program
    
    result = glGetProgramiv(program, GL_LINK_STATUS) #check if program linked successfully
    if not result:
        raise Exception(glGetProgramInfoLog(program)) #error message if program fails to link
    
    return program

def main():

    if not glfw.init(): #initialize glfw
        raise Exception("glfw failed to initialize")  #error message if glfw fails to initialize
        
    width = 1920 #set width of window
    height = 1080 #set height of window
    title = "Fractal Renderer" #set title of window

    window = glfw.create_window(width, height, title, None, None) #creates a window with given parameters
    if not window: #if window fails to create
        glfw.terminate()
        raise Exception("glfw window failed to create") #error message if window fails to create
        
    glfw.make_context_current(window) #makes the window the current context

    vertex_shader = create_shader(GL_VERTEX_SHADER, vertex_shader_src)
    fragment_shader = create_shader(GL_FRAGMENT_SHADER, fragment_shader_src)
    program = create_program(vertex_shader, fragment_shader)

    vertices = (
            -1.0, -1.0, 0.0, # bottom left (shared in both triangles)
            1.0, -1.0, 0.0, # bottom right (first traingle)
            1.0, 1.0, 0.0, # top right (shared in both triangles)
            -1.0, -1.0, 0.0, # bottom left (second triangle)
            1.0, 1.0, 0.0,# top right (second triangle)
            -1.0, 1.0, 0.0, # top left (second triangle)
        )
    
    vertices = np.array(vertices, dtype=np.float32)

    # Creating the vertex array
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # Set up vertex buffer object
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glClearColor(0, 0, 0, 0)
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(program)
    
    # Setting up the coordinates buffer
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

    # Locations for the uniforms
    zoom_loc = glGetUniformLocation(program, "zoom")
    offset_loc = glGetUniformLocation(program, "offset")
    res_loc = glGetUniformLocation(program, "resolution")
    max_iterations_loc = glGetUniformLocation(program, "max_iterations")

    #Giving values to uniform
    zoom = 1.0
    offset_x, offset_y = 0.0, 0.0
    max_iterations = 1000

    # Setting the uniform values
    glUniform2f(res_loc, width, height)
    glUniform1f(zoom_loc, zoom)
    glUniform2f(offset_loc, offset_x, offset_y)
    glUniform1i(max_iterations_loc, max_iterations)

    zoom_speed = 0.9  # Multiplier for zooming
    pan_speed = 0.1   # Adjust panning speed

   
    #Setting up imgui
    imgui.create_context()  #create the context
    imgui_render = GlfwRenderer(window) #render the window

    while not glfw.window_should_close(window): #while the window is open  
        imgui_render.process_inputs() #process the inputs
        imgui.new_frame() #start a new frame
        imgui.begin("Fractal Controls") 
        imgui.set_window_size(400, 100) #set the window size
        imgui.get_style().window_rounding = 10.0 #set the window rounding
        imgui.get_style().colors[imgui.COLOR_WINDOW_BACKGROUND] = (0.0, 0.0, 0.0, 1.0) 
        imgui.get_style().colors[imgui.COLOR_TITLE_BACKGROUND_ACTIVE] = (0.0, 0.0, 1.0, 1.0)

        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:  
            zoom *= zoom_speed  # Zoom in
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            zoom /= zoom_speed  # Zoom out
        
        if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:  
            offset_x -= pan_speed * zoom  # Move left
        if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:  
            offset_x += pan_speed * zoom  # Move right
        if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:  
            offset_y += pan_speed * zoom  # Move up
        if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:  
            offset_y -= pan_speed * zoom  # Move down
        
        changed, max_iterations = imgui.slider_int("Iterations", max_iterations, 100, 50000)
        if changed:
            glUniform1i(max_iterations_loc, max_iterations)
       
        # Send the updated values to the fragment shader
        glUniform1f(zoom_loc, zoom)
        glUniform2f(offset_loc, offset_x, offset_y)
        

        imgui.end() 
        imgui.render()


        glDrawArrays(GL_TRIANGLES, 0, int(len(vertices)/3)) #draws the triangles
        imgui_render.render(imgui.get_draw_data())
        glfw.swap_buffers(window) #swap the buffers
        glfw.poll_events() #poll the events

    glfw.terminate()


if __name__ == '__main__':
    main()
