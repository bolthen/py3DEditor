#version 330 core

in vec2 ourTextureCoord;
in vec3 localPos;

out vec4 color;

uniform sampler2D mainTexture;

void main()
{
    //color = texture(mainTexture, ourTextureCoord);
    //color = vec4(0.2f, 0.2f, 0.2f, 1);
    vec3 uv = localPos - gl_FragCoord.xyz;
    color = vec4(sqrt(dot(uv, uv)));
}