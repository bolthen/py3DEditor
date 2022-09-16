#version 330 core

in vec2 ourTextureCoord;
in vec3 localPos;

out vec4 color;

uniform sampler2D mainTexture;

void main()
{
    color = texture(mainTexture, ourTextureCoord);
    //color = vec4(0.2f, 0.2f, 0.2f, 1);
    //vec2 uv = (gl_FragCoord.xy - 0.5f * vec2(1920, 1080)) / 1080;
    //vec3 col = vec3(0);
    //col += 0.01f / length(uv);
    //color = vec4(sqrt(dot(uv, uv)));
}