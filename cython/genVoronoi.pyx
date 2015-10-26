import numpy as np
cimport numpy as np
cimport cython

cdef int colors_index[1000][1000][21]
cdef float pulls[21]
cdef float cache[1000][1000]
cdef int colors_internal[21][3]
cdef int points_internal[21][200][2]
cdef float eps = 1e-12

@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef init_cache():
    cdef int i, j
    cdef float d

    for i in range(1000):
        for j in range(1000):
            d = i*i + j*j
            if (i == 0 and j == 0):
                cache[i][j] = 1000.0
            else:
                cache[i][j] = 1.0/d

cdef void reset_pulls(int n_players):
    for i in range(n_players):
        pulls[i] = 0.0

cdef float max_val(int n_players):
    cdef int i
    cdef float max_value = 0.0

    for i in range(n_players):
        if max_value < pulls[i]:
            max_value = pulls[i]
    return max_value

cdef void generate_max_indices(int n_players, int x, int y):
    cdef int i, k = 0
    cdef float max_value

    # +1 space for the count of players that have same max value
    for i in range(n_players+1):
        colors_index[x][y][i] = -1

    max_value = max_val(n_players)
    for i in range(n_players):
        if abs(max_value - pulls[i]) < eps:
            colors_index[x][y][k+1] = i
            k += 1
    colors_index[x][y][0] = k

@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef generate_voronoi_diagram(
    int n_players, int n_moves,
    np.ndarray[np.int_t, ndim=3] points,
    np.ndarray[np.uint8_t, ndim=2] colors,
    np.ndarray[np.uint8_t, ndim=3] image,
    int GUIOn,
    int scale
):
    cdef int px, py, a, b, x, y, p, m, i, max_i, j, k, n
    cdef int red, green, blue

    for i in range(n_players):
        for j in range(3):
            colors_internal[i][j] = colors[i,j]

    for i in range(n_players):
        for j in range(n_moves):
            for k in range(2):
                points_internal[i][j][k] = points[i,j,k]

    for x in range(1000):
        for y in range(1000):
            reset_pulls(n_players)
            for p in range(n_players):
                for m in range(n_moves):
                    if points_internal[p][m][0] == -1:
                        break
                    px = points_internal[p][m][0]
                    py = points_internal[p][m][1]
                    pulls[p] += cache[abs(px-x)][abs(py-y)]
            generate_max_indices(n_players, x, y)

    if GUIOn:
        for x from 0 <= x < 1000 by scale:
            for y from 0 <= y < 1000 by scale:
                n = colors_index[x][y][0]
                red = 0
                green = 0
                blue = 0
                for i in range(1, n+1):
                    red += colors_internal[colors_index[x][y][i]][0]
                    green += colors_internal[colors_index[x][y][i]][1]
                    blue += colors_internal[colors_index[x][y][i]][2]
                image[y/scale,x/scale,0] = red/n
                image[y/scale,x/scale,1] = green/n
                image[y/scale,x/scale,2] = blue/n

@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef get_scores(int n_players):
    cdef np.ndarray[np.float_t, ndim=1] scores_external = np.zeros([n_players], dtype=np.float)
    cdef int x, y, i, n
    for x in range(1000):
        for y in range(1000):
            n = colors_index[x][y][0]
            for i in range(1, n+1):
                scores_external[colors_index[x][y][i]] += 1.0/n
    return scores_external

@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef get_color_indices_and_scores(
    int n_players,
    int n_moves,
    np.ndarray[np.int_t, ndim=3] points
):
    cdef np.ndarray[np.float_t, ndim=1] scores_external = np.zeros([n_players], dtype=np.float)
    cdef np.ndarray[np.int_t, ndim=3] colors_index_external = np.zeros([1000, 1000, 21], dtype=np.int)
    cdef int x, y, i, n
    for x in range(1000):
        for y in range(1000):
            n = colors_index[x][y][0]
            colors_index_external[x, y, 0] = n
            for i in range(1, n+1):
                colors_index_external[x, y, i] = colors_index[x][y][i]
                scores_external[colors_index[x][y][i]] += 1.0/n
    return scores_external, colors_index_external
