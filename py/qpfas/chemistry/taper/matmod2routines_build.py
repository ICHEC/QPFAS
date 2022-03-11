from cffi import FFI
ffibuilder = FFI()

ffibuilder.cdef("""
void binary_gaussian_elimination(int **A, int m, int n);
void mat_vec_mod2(int **A, int *x, int *y, int m, int n);
void print_mat(int **A, int m, int n);
""")

ffibuilder.set_source("mm2r",
"""
void binary_gaussian_elimination(int **A, int m, int n);
void mat_vec_mod2(int **A, int *x, int *y, int m, int n);
void print_mat(int **A, int m, int n);
""",
                      sources=['matmod2routines.c']   # library name, for the linker
 )

ffibuilder.compile(verbose=True)
