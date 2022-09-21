#version 330 core

out vec4 color;

in vec2 ourTextureCoord;
in vec3 ourNormals;
in vec3 worldFragPos;

uniform sampler2D mainTexture;
uniform sampler2D firstTexture;
uniform sampler2D secondTexture;
uniform vec2 resolution;
uniform float time;
uniform vec3 lightColor;
uniform vec3 lightPos;
uniform vec3 viewPos;

void main()
{
    vec2 newTextures = vec2(ourTextureCoord.x, 1.0f - ourTextureCoord.y);

    float ambientStrength = 0.3f;
    vec3 ambient = ambientStrength * lightColor;

    vec3 norm = normalize(ourNormals);
    vec3 lightDirection = normalize(lightPos - worldFragPos);
    float cosAngle = max(dot(norm, lightDirection), 0.0);
    vec3 diffuse = cosAngle * lightColor;

    float specularStrength = 0.4;
    vec3 viewDir = normalize(viewPos - worldFragPos);
    vec3 reflectDir = reflect(-lightDirection, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0), 32);
    vec3 specular = specularStrength * spec * lightColor;

    vec4 objectColor = texture(mainTexture, newTextures);

    color = objectColor * vec4(ambient + diffuse + specular, 1.0f);
}