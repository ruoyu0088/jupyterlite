#include <math.h>
#include <stdint.h>
#include <stdlib.h>

void clifford_attractor(double a, double b, double c, double d,
                        uint32_t *image, int width, int height, int n)
{
    const int warmup = 100000; // iterations for range estimation
    double x = 0.0, y = 0.0;
    double min_x = 1e9, max_x = -1e9;
    double min_y = 1e9, max_y = -1e9;

    // --- Phase 1: measure range ---
    for (int i = 0; i < warmup; i++) {
        double x_next = sin(a * y) + c * cos(a * x);
        double y_next = sin(b * x) + d * cos(b * y);
        x = x_next;
        y = y_next;
        if (x < min_x) min_x = x;
        if (x > max_x) max_x = x;
        if (y < min_y) min_y = y;
        if (y > max_y) max_y = y;
    }

    // Prevent division by zero if attractor collapses
    double range_x = (max_x - min_x);
    double range_y = (max_y - min_y);
    if (range_x == 0.0) range_x = 1e-9;
    if (range_y == 0.0) range_y = 1e-9;

    // --- Phase 2: accumulate image ---
    for (int i = 0; i < n; i++) {
        double x_next = sin(a * y) + c * cos(a * x);
        double y_next = sin(b * x) + d * cos(b * y);
        x = x_next;
        y = y_next;

        // Map to pixel coordinates
        int ix = (int)((x - min_x) / range_x * (width - 1));
        int iy = (int)((y - min_y) / range_y * (height - 1));

        if (ix >= 0 && ix < width && iy >= 0 && iy < height) {
            image[iy * width + ix]++;
        }
    }
}
