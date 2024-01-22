#version 330

in vec3 in_position;
in vec3 in_normal;
in vec2 in_texcoord_0;  // Dodajemy współrzędne tekstury

smooth out vec3 interp_normal;
smooth out vec3 frag_position;
smooth out vec2 tex_coords;  // Dodajemy do przekazywanych zmiennych wyjściowych

uniform mat4 projection;
uniform mat4 view;

void main() {
    interp_normal = in_normal;
    frag_position = in_position;
    tex_coords = in_texcoord_0;  // Przypisz współrzędne tekstury

    gl_Position = projection * view * vec4(in_position, 1.0);
}
