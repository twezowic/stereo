#version 330

#define MAX_LIGHTS 5
out vec4 f_color; // when there is only one output, it gets recognised as location 0 aka the fragment color

smooth in vec3 frag_position;
smooth in vec3 interp_normal;
smooth in vec2 tex_coords;

uniform vec3 camera_position;

uniform sampler2D textureSampler; 

struct Light
{
  vec3 pos;
  vec3 color;
};

uniform Light point_lights[MAX_LIGHTS];
uniform int light_count;

uniform vec3 Ka;  // Ambient color
uniform vec3 Kd;  // Diffuse color
uniform vec3 Ks;  // Specular color
uniform float Ns; // Specular exponent

// phong shading
void main()
{
    //ambient
    vec3 ambient = Ka;


    float alpha=32;

    vec3 direction_to_viewer = normalize(frag_position-camera_position);
    vec3 normal = normalize(interp_normal);

    vec3 diffuse= vec3(0,0,0);
    vec3 specular= vec3(0,0,0);
    for(int i=0;i<min(light_count,MAX_LIGHTS);++i){
        vec3 direction_to_light = normalize(point_lights[i].pos-frag_position);
        //diffuse
        float diffuse_power = max(dot(direction_to_light,normal),0);
        diffuse+= Kd * point_lights[i].color*diffuse_power;
        //specular
        if (diffuse_power>0){

        vec3 reflect_direction = reflect(direction_to_light, normal);
        float specular_power = max(dot(reflect_direction, direction_to_viewer), 0.0);
        specular +=Ks * point_lights[i].color * pow(specular_power,Ns);
        }
    }

    vec3 color_sum = ambient+diffuse+specular;
    vec4 textureColor = texture(textureSampler, tex_coords);
    if (dot(textureColor.rgb,textureColor.rgb)!=0.0){
      color_sum *= textureColor.rgb; 
    }
    f_color = vec4(color_sum, 1.0);
}