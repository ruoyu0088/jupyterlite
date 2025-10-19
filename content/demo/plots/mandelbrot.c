#include <stdlib.h>
#include <math.h>

typedef struct {
    double real;
    double imag;
} Complex;

double iter_point(Complex c, int n, double R) {
    Complex z = c;
    int i;
    double r2, mu;
    double R2 = R * R;

    for (i = 1; i < n; i++) {
        r2 = z.real * z.real + z.imag * z.imag;
        if (r2 > R2) break;
        double real = z.real * z.real - z.imag * z.imag + c.real;
        double imag = 2 * z.real * z.imag + c.imag;
        z.real = real;
        z.imag = imag;
    }

    r2 = z.real * z.real + z.imag * z.imag;
    if (r2 > 4.0) {
        mu = i - log2(0.5 * log2(r2));
    } else {
        mu = i;
    }
    return mu;
}

void mandelbrot(double cx, double cy, double d, int h, int w, double* result, int n, double R) {
    double x0 = cx - d;
    double x1 = cx + d;
    double y0 = cy - d;
    double y1 = cy + d;
    double dx = (x1 - x0) / (w - 1);
    double dy = (y1 - y0) / (h - 1);
    int i, j;

    for (i = 0; i < h; i++) {
        for (j = 0; j < w; j++) {
            Complex z;
            z.imag = y0 + i * dy;
            z.real = x0 + j * dx;
            result[i * w + j] = iter_point(z, n, R);
        }
    }
}