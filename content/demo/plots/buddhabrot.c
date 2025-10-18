#include <math.h>
#include <stdlib.h>

// Uniform random double in [0, 1)
static inline double rand_double() {
    return (double)rand() / (double)RAND_MAX;
}

void buddhabrot_random(
    int width,
    int height,
    int max_iter,
    int n_samples,
    double x_min,
    double x_max,
    double y_min,
    double y_max,
    double *path_real,
    double *path_imag,
    double *image  // size = width * height
) {
    double inv_xrange = width / (x_max - x_min);
    double inv_yrange = height / (y_max - y_min);

    for (int i = 0; i < n_samples; i++) {
        double cx = x_min + (x_max - x_min) * rand_double();
        double cy = y_min + (y_max - y_min) * rand_double();
        double zx = 0.0, zy = 0.0;
        int escaped = 0;
        int j;

        for (j = 0; j < max_iter; j++) {
            double zx2 = zx * zx - zy * zy + cx;
            double zy2 = 2.0 * zx * zy + cy;
            zx = zx2;
            zy = zy2;
            path_real[j] = zx;
            path_imag[j] = zy;
            if (zx * zx + zy * zy > 4.0) {
                escaped = 1;
                break;
            }
        }

        if (escaped) {
            for (int k = 0; k < j; k++) {
                int px = (int)((path_real[k] - x_min) * inv_xrange);
                int py = (int)((path_imag[k] - y_min) * inv_yrange);
                if (px >= 0 && px < width && py >= 0 && py < height) {
                    image[py * width + px] += 1.0;
                }
            }
        }
    }
}

void buddhabrot_grid(
    int width,
    int height,
    int max_iter,
    double x_min,
    double x_max,
    double y_min,
    double y_max,
    int scale,
    double *path_real,
    double *path_imag,
    double *image  // size = height * width
) {
    int scaled_width = width * scale;
    int scaled_height = height * scale;

    double dx = (x_max - x_min) / (double)scaled_width;
    double dy = (y_max - y_min) / (double)scaled_height;
    double inv_xrange = width / (x_max - x_min);
    double inv_yrange = height / (y_max - y_min);

    for (int iy = 0; iy < scaled_height; iy++) {
        double cy = y_min + dy * iy;

        for (int ix = 0; ix < scaled_width; ix++) {
            double cx = x_min + dx * ix;
            double zx = 0.0, zy = 0.0;
            int escaped = 0;
            int j;

            for (j = 0; j < max_iter; j++) {
                double zx2 = zx * zx - zy * zy + cx;
                double zy2 = 2.0 * zx * zy + cy;
                zx = zx2;
                zy = zy2;
                path_real[j] = zx;
                path_imag[j] = zy;

                if (zx * zx + zy * zy > 4.0) {
                    escaped = 1;
                    break;
                }
            }

            if (escaped) {
                for (int k = 0; k < j; k++) {
                    int px = (int)((path_real[k] - x_min) * inv_xrange);
                    int py = (int)((path_imag[k] - y_min) * inv_yrange);
                    if (px >= 0 && px < width && py >= 0 && py < height) {
                        image[py * width + px] += 1.0;
                    }
                }
            }
        }
    }
}
