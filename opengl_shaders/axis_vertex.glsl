#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;

//uniform mat4 view;
uniform mat4 projection;
uniform mat4 model;

out vec3 axisColor;

void main()
{
    //gl_Position = projection * view * vec4(position, 1);
    //gl_Position = projection * model * vec4(position, 1);
    gl_Position = model * vec4(position, 1);
    axisColor = color;
}