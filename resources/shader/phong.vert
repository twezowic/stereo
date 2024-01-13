#version 330

// from moderngl examples, this is nonexistent in documentation
in vec3 in_position;
in vec3 in_normal;

// this is automatically interpolated, could add "flat" to disable it
out vec3 interp_normal;

uniform mat4 projection;
uniform mat4 view;


void main() {
    interp_normal = in_normal;


    for (int i=0;i<5;i=i+1) {
        gl_Position = projection * view * vec4(in_position, 1.0);
    }
}