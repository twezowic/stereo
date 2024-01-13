#version 330

#define MAX_LIGHTS 5
out vec4 f_color; // when there is only one output, it gets recognised as location 0 aka the fragment color

smooth in vec3 frag_position;
smooth in vec3 interp_normal;
uniform vec3 camera_position;

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
    //ambient
    vec3 ambient = ambient_intensity*ambient_color;

    float alpha=32;

    vec3 direction_to_viewer = normalize(frag_position-camera_position);
    vec3 normal = normalize(interp_normal);

    vec3 diffuse;
    vec3 specular=vec3(0,0,0);
    for(int i=0;i<min(light_count,MAX_LIGHTS);++i){
        vec3 direction_to_light = normalize(point_lights[i].pos-frag_position);
        //diffuse
        float diffuse_power = max(dot(direction_to_light,normal),0);
        diffuse+=point_lights[i].color*diffuse_power;
        //specular
        if (diffuse_power>0){

        vec3 reflect_direction = reflect(direction_to_light, normal);
        float specular_power = max(dot(reflect_direction, direction_to_viewer), 0.0);
        specular += pow(specular_power,alpha)*vec3(1,1,1);
        }
    }

    vec3 color_sum = ambient+diffuse+specular;

    f_color = vec4(color_sum, 1.0);
}