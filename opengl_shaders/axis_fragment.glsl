#version 330 core

in vec3 axisColor;
out vec4 color;


void main()
{
    color = vec4(axisColor[0] / 255.0f, axisColor[1] / 255.0f, axisColor[2] / 255.0f, 1);
}