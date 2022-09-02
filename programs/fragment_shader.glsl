#version 330 core

out vec4 color;

in vec3 ourColor;
in vec2 ourTextureCoord;

uniform sampler2D firstTexture;
uniform sampler2D secondTexture;
uniform vec2 resolution;
uniform float time;

void main()
{
    color = mix(texture(firstTexture, ourTextureCoord),
                texture(secondTexture, ourTextureCoord),
                0.2f);
}