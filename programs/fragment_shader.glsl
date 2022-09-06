#version 330 core

out vec4 color;

in vec2 ourTextureCoord;
in vec3 ourNormals;

uniform sampler2D mainTexture;
uniform sampler2D firstTexture;
uniform sampler2D secondTexture;
uniform vec2 resolution;
uniform float time;

void main()
{
    vec2 newTextures = vec2(ourTextureCoord.x, 1.0f - ourTextureCoord.y);
    color = texture(mainTexture, newTextures);
}