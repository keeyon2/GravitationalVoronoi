import numpy as np
import genVoronoi
if __name__ == '__main__':
    num_players, num_moves = tuple(int(n) for n in raw_input().split())
    points = np.zeros([num_players, num_moves, 2], dtype=np.int)
    points.fill(-1)

    # Can put any garbage here. Not using this in the end.
    image = np.zeros([10, 10, 3], dtype=np.uint8)
    colors = np.zeros([num_players, 3], dtype=np.uint8)

    for p in xrange(num_players):
        player, actual_move_count = tuple(int(n) for n in raw_input().split())
        for m in xrange(actual_move_count):
            x, y = tuple(int(n) for n in raw_input().split())
            points[p, m, 0] = x
            points[p, m, 1] = y
    genVoronoi.init_cache()

    # Important to put GUIOn as false
    genVoronoi.generate_voronoi_diagram(num_players, num_moves, points, colors, image, 0, 1)

    scores, colors_index = genVoronoi.get_color_indices_and_scores(num_players, num_moves, points)
    for i in range(num_players):
        print scores[i]
    for i in range(1000):
        for j in range(1000):
            n = colors_index[i,j,0]
            print n,
            for k in range(1, n+1):
                print colors_index[i,j,k],
            print
