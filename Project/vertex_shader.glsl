#version 460 core

layout(location = 0) in vec3 vertPos;

out vec2 fragcoord;


void main(){
        gl_Position = vec4(vertPos, 1);
        fragcoord = vec2(vertPos.x, vertPos.y);
}