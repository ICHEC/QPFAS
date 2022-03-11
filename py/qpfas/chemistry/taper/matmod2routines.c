#include <stdio.h>
#include <stdlib.h>

void print_mat(int **A, int m, int n){
	int i, j;
	for (i=0; i<m; i++){
	    for (j=0; j<n; j++){
	        printf("%i ", A[i][j]);
	    }
	    printf("\n");
	}
}

void binary_gaussian_elimination(int **A, int m, int n){
	int i, j, k, pivot_row_index, pivot_cond, temp, n_pivot;
	n_pivot = 0;

	for (j=0; j<n; j++){
	    // Find pivot
	    pivot_cond=0;
	    pivot_row_index = n_pivot;

        //printf("***[ %i ]***\n", j);
        //print_mat(A, m, n);

	    while (pivot_row_index < m && pivot_cond == 0){
	        //printf("\t\t %i (%i)\n", pivot_row_index, A[pivot_row_index][j]);
			if (A[pivot_row_index][j] == 1){
			    pivot_cond = 1;
			    n_pivot += 1;
			    break;}
		    pivot_row_index += 1;}

	    //printf("Col: %i\nPivot Row: %i (%i)\nN Pivot: %i\n", j, pivot_row_index, pivot_cond, n_pivot);

        // If the pivot is not at j, swap rows
	    if (pivot_cond==1 && pivot_row_index!=(n_pivot-1)){
	        //printf("\tswapping (%i, %i)\n", pivot_row_index, n_pivot-1);
		    for (i=0; i<n; i++){
			    temp = A[pivot_row_index][i];
			    A[pivot_row_index][i] = A[n_pivot-1][i];
			    A[n_pivot-1][i] = temp;}
            }


        // Add rows mod 2
        if (pivot_cond == 1){
	    	for (i=0; i<m; i++){
			    if (i != (n_pivot-1) && A[i][j] == 1){
			        //printf("\tsumming (%i, %i)\n", i, n_pivot-1);
				    for (k=0; k<n; k++)
				        A[i][k] = (A[i][k] + A[n_pivot-1][k]) % 2;
			        }
		        }
    		}

	}
}


void mat_vec_mod2(int **A, int *x, int *y, int m, int n){
    //  Ax=y (all done mod 2)
    int i, j;
	for (i=0; i<m; i++){
	    for (j=0; j<n; j++)
   	        y[i] += A[i][j]*x[j];
   	    y[i] = y[i] % 2;}
}
