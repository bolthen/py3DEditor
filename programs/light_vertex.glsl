#version 330 core

layout (location = 0) in vec2 textureCoord;
layout (location = 1) in vec3 normals;
layout (location = 2) in vec3 position;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec2 ourTextureCoord;
out vec3 localPos;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1);
    ourTextureCoord = textureCoord;
    localPos = position;
}