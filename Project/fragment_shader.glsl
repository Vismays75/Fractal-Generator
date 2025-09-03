#version 460 core

// Input from vertex shader
in vec2 fragcoord;
out vec4 color; // Final output color

// Uniforms (set from Python)
uniform float zoom;       // Zoom level
uniform vec2 resolution;  // Screen resolution (width, height)
uniform vec2 offset;      // Panning offset
uniform int max_iterations;    // Static max iterations

// Converts HSV to RGB
vec3 hsv2rgb(vec3 c) {
    vec3 k = vec3(1.0, 2.0 / 3.0, 1.0 / 3.0);
    vec3 p = abs(fract(c.xxx + k) * 6.0 - k.xxx);
    return c.z * mix(k.xxx, clamp(p - k.xxx, 0.0, 1.0), c.y);
}

// Maps iterations to a color gradient
vec3 map_color(int i, float escape) {
    float di = float(i);
    float hue = (di + 1.0 - log(log(abs(escape)))) / float(max_iterations);
    return hsv2rgb(vec3(hue, 0.8, 1.0)); // Hue-based color gradient
}

void main() {
    // Normalize pixel coordinates to [-1, 1]
    vec2 uv = (fragcoord / resolution) * 2.0 - 1.0;
    uv.x *= resolution.x / resolution.y; // Maintain aspect ratio

    // Apply zoom and offset
    float cx = uv.x * zoom + offset.x;
    float cy = uv.y * zoom + offset.y;

    float zx = 0.0, zy = 0.0;
    int iteration = 0;

    // Mandelbrot iteration
    while (iteration < max_iterations) {
        float zx_new = zx * zx - zy * zy + cx;
        float zy_new = 2.0 * zx * zy + cy;
        zx = zx_new;
        zy = zy_new;

        // Escape condition: If |Z| > 2, break
        if (zx * zx + zy * zy > 4.0) break;

        iteration++;
    }

    // Set final color
    if (iteration == max_iterations) {
        color = vec4(0, 0, 0, 1); // Black for Mandelbrot set points
    } else {
        color = vec4(map_color(iteration, zx * zx + zy * zy), 1);
    }
}
