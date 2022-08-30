#version 430

out vec4 fragColor;

uniform float time;
uniform vec2 resolution;

void main()
{
    vec2 uv = gl_FragCoord.xy / resolution.xy;
    vec3 col = 0.5 + 0.5 * cos(time+uv.xyx + vec3(0,2,4));
    fragColor = vec4(col,1.0);
}