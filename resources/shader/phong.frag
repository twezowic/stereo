#version 330

#define MAX_LIGHTS 5
out vec4 f_color;

in vec3 in_position;
in vec3 interp_normal;

struct Light
{
  vec3 pos;
  vec3 color;
};

uniform Light point_lights[MAX_LIGHTS];
uniform int light_count;

uniform vec3 ambient_color;
uniform float ambient_intensity;

// phong shading
void main()
{
    float id=1;
    vec3 ambient = ambient_intensity*ambient_color;

    vec3 diffuse;

    //
    for(int i=0;i<min(light_count,MAX_LIGHTS);++i){
        vec3 direction_to_light = normalize(point_lights[i].pos-in_position);
        diffuse+=id*point_lights[i].color*dot(direction_to_light,interp_normal);
    }

    vec3 color_sum = ambient+diffuse;

    f_color = vec4(color_sum, 1.0);
}