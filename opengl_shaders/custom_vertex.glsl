#version 330 core

layout (location = 0) in vec3 colors;
layout (location = 1) in vec3 normals;
layout (location = 2) in vec3 position;

out vec3 ourColors;
out vec3 ourNormals;
out vec3 worldFragPos;

uniform mat4 model;
uniform mat4 normModel;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1);
    ourColors = colors;
    ourNormals = mat3(normModel) * normals;
    worldFragPos = vec3(model * vec4(position, 1));
}