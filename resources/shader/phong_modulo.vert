#version 330

// from moderngl examples, this is nonexistent in documentation
in vec3 in_position;
in vec3 in_normal;

// this is automatically interpolated, could add "flat" to disable it
smooth out vec3 interp_normal;
smooth out vec3 frag_position;

uniform mat4 projection;
uniform mat4 view;


void main() {
    interp_normal = in_normal;
    frag_position=in_position;

    gl_Position = projection * view * vec4(in_position, 1.0);
}