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
    //color = mix(texture(firstTexture, ourTextureCoord),
    //            texture(secondTexture, ourTextureCoord),
    //            0.2f);

    //color = vec4(ourNormals, ourTextureCoord[0]);
    //color = vec4(ourNormals, 1.0f);
    //color = vec4(0.2f, 0.2f, 0.2f, 1.0f);
    color = texture(mainTexture, ourTextureCoord);
}