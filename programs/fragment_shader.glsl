#version 430

out vec4 fragColor;

uniform float time;
uniform vec2 resolution;

void main()
{
    vec2 uv = (gl_FragCoord.xy - 0.5f * resolution.xy) / resolution.y;
    vec3 color = vec3(0.0, 0.2, 0.6);

    color += abs(sin(time)) * length(uv) * 10;

    fragColor = vec4(color, 1.0);
}