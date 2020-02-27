import math
from dijkstar import Graph

pi = math.pi

angles = {}
nav_types = {}

line = 'line'
amcl = 'amcl'
_distance_bias = 1
help_delta_xy = 0
help_delta_theta = 0

n, s, e, w = 'n', 's', 'e', 'w'
help_deltas = {
    n: (0, help_delta_xy),
    s: (0, -help_delta_xy),
    e: (help_delta_xy, 0),
    w: (-help_delta_xy, 0),
}
stop_line_delta = 0.1
stop_line_deltas = {
    1: (0, stop_line_delta),
    2: (stop_line_delta, 0),
    3: (-stop_line_delta, 0),
    4: (0, -stop_line_delta),
}

_points = {
    # "name": (x, y)
    "start": (3.4, -1.6),
    "blue": (1.9, -3.8),
    "red": (-3.4, 2.8),
    "n1": (-0.47, 4.41),
    "n2": (0.23, 4.22),
    "n2_stop_line": (0.72 + stop_line_deltas[2][0], 4.24 + stop_line_deltas[2][1]),
    ("n3", 'n3_s'): (-0.33, 3.47),
    ("n4", "n4_e"): (0.22, 3.49),
    "n4_stop_line": (0.25, 2.7),  # n4_stop_line == pink
    "w1": (-3.47, 0.09),
    "w1_stop_line": (-3.45 + stop_line_deltas[1][0], 0.8 + stop_line_deltas[1][1]),
    ("w2", "w2_n"): (-2.9, 0.15),
    "w2_stop_line": (-2.38 + stop_line_deltas[2][0], 0.16 + stop_line_deltas[2][1]),
    "w3": (-3.48, -0.51),
    ("w4", "w4_e"): (-2.82, -0.43),
    ("e1", "e1_w"): (2.73, 0.12),
    "e2": (3.47, 0.25),
    ("e3", "e3_s"): (2.84, -0.48),
    "e3_stop_line": (2.35 + stop_line_deltas[3][0], -0.54 + stop_line_deltas[3][1]),
    "e4": (3.45, -0.45),
    ("c1", "c1_w"): (-0.32, 0.15),
    "c1_stop_line": (-0.3 + stop_line_deltas[1][0], 0.74 + stop_line_deltas[1][1]),
    ("c2_n", "c2"): (0.25, 0.25),
    "c2_stop_line": (0.58 + stop_line_deltas[2][0], 0.17 + stop_line_deltas[2][1]),
    ("c3", "c3_s"): (-0.33, -0.51),  # c3 == green
    "c3_stop_line": (-0.76 + stop_line_deltas[3][0], -0.4 + stop_line_deltas[3][1]),
    ("c4", "c4_e"): (0.31, -0.44),
    "c4_stop_line": (0.30 + stop_line_deltas[4][0], -0.9 + stop_line_deltas[4][1]),
    ("s1", "s1_w"): (-0.34, -3.86),
    "s1_stop_line": (-0.35 + stop_line_deltas[1][0], -3.35 + stop_line_deltas[1][1]),
    ("s2", "s2_n"): (0.26, -3.76),
    "s3": (-0.24, -4.52),
    "s3_stop_line": (-0.84 + stop_line_deltas[3][0], -4.51 + stop_line_deltas[3][1]),
    "s4": (0.37, -4.53),
    "nw_out": (-3.35, 4.21),
    "nw_in": (-2.84, 3.43),
    "ne_out": (3.38, 4.09),
    "ne_in": (2.89, 3.41),
    "sw_out": (-3.41, -4.42),
    "sw_in": (-2.84, -3.79),
    "se_out": (3.41, -4.4),
    "se_in": (2.61, -3.8),
}
points = {}
for k, v in _points.iteritems():
    if isinstance(k, tuple):
        for x in k:
            points[x] = v
    else:
        points[k] = v


def generate_graph():
    """ general:
    nw --- n --- ne
    |      |      |
    w ---- c ---- e
    |      |      |
    sw --- s --- se

    junctions- 4-complete graph:
    w1--w2
    |  X |
    w3--w4

    corners- separated:
    nw_o -------
    |
    |   nw_i ---
    |    |

    mid-points:
    |       |
    |       |
    red---red2
    |       |
    |       |
    """
    g = Graph(undirected=False)
    # junction edges
    add_complete_4_group('n1', 'n2', ['n3', 'n3_s'], ['n4', 'n4_e'], g)

    add_complete_4_group('w1', ['w2', 'w2_n'], 'w3', ['w4', 'w4_e'], g)

    add_complete_4_group(['e1', 'e1_w'], 'e2', ['e3', 'e3_s'], 'e4', g)

    add_complete_4_group(['s1', 's1_w'], ['s2', 's2_n'], 's3', 's4', g)

    add_complete_4_group(['c1', 'c1_w'], ['c2', 'c2_n'], ['c3', 'c3_s'], ['c4', 'c4_e'], g)

    # corners edges
    add_edge('n1', 'nw_out', g, 3*pi/2, line)
    add_edge('nw_out', 'w1_stop_line', g, 3*pi/2, line)

    add_edge('w1_stop_line', 'w1', g, 3*pi/2, amcl)

    add_edge('nw_in', 'n3', g, 0, line)
    add_edge('nw_in', 'n3_s', g, 3 * pi / 2, line)
    add_edge('w2_n', 'nw_in', g, 0, line)

    add_edge('n2_stop_line', 'n2', g, pi, amcl)

    add_edge('ne_out', 'n2_stop_line', g, pi, line)
    add_edge('e2', 'ne_out', g, pi, line)

    add_edge('n4_e', 'ne_in', g, 3*pi/2, line)
    add_edge('ne_in', 'e1', g, 3*pi/2, line)
    add_edge('ne_in', 'e1_w', g, pi, line)

    add_edge('w3', 'sw_out', g, 0, line)
    add_edge('sw_out', 's3_stop_line', g, 0, line)

    add_edge('s3_stop_line', 's3', g, 0, amcl)  # amcl?

    add_edge('sw_in', 'w4', g, pi / 2, line)
    add_edge('sw_in', 'w4_e', g, 0, line)
    add_edge('s1_w', 'sw_in', g, pi/2, line)

    add_edge('s4', 'se_out', g, pi/2, line)
    add_edge('se_out', 'e4', g, pi/2, line)
    add_edge('se_out', 'start', g, pi/2, line)

    add_edge('e3_s', 'se_in', g, pi, line)
    add_edge('se_in', 's2', g, pi, line)
    add_edge('se_in', 's2_n', g, pi / 2, line)

    add_edge('n3_s', 'c1_stop_line', g, 3*pi/2, line)
    add_edge('c1_stop_line', 'c1', g, 3*pi/2, amcl)
    add_edge('c1_stop_line', 'c1_w', g, pi, amcl)

    add_edge('c1_w', 'w2_stop_line', g, pi, line)
    add_edge('w2_stop_line', 'w2', g, pi, amcl)
    add_edge('w2_stop_line', 'w2_n', g, pi/2, amcl)

    add_edge('c2_n', 'n4_stop_line', g, pi/2, line)
    add_edge('n4_stop_line', 'n4', g, pi/2, amcl)
    add_edge('n4_stop_line', 'n4_e', g, 0, amcl)

    add_edge('e1_w', 'c2_stop_line', g, pi, line)
    add_edge('c2_stop_line', 'c2', g, pi, amcl)
    add_edge('c2_stop_line', 'c2_n', g, pi/2, amcl)

    add_edge('w4_e', 'c3_stop_line', g, 0, line)
    add_edge('c3_stop_line', 'c3', g, 0, amcl)
    add_edge('c3_stop_line', 'c3_s', g, 3*pi/2, amcl)

    add_edge('c3_s', 's1_stop_line', g, 3*pi/2, line)
    add_edge('s1_stop_line', 's1', g, 3*pi/2, amcl)
    add_edge('s1_stop_line', 's1_w', g, pi, amcl)

    add_edge('s2_n', 'c4_stop_line', g, pi/2, line)
    add_edge('c4_stop_line', 'c4', g, pi/2, amcl)
    add_edge('c4_stop_line', 'c4_e', g, 0, amcl)

    add_edge('c4_e', 'e3_stop_line', g, 0, line)
    add_edge('e3_stop_line', 'e3', g, 0, amcl)
    add_edge('e3_stop_line', 'e3_s', g, 3*pi/2, amcl)

    # mid-points
    # green is c3
    add_edge('se_out', 'start', g, pi/2, line)
    add_edge('start', 'e4', g, pi/2, line)  # e4 == e4_stop_line

    add_edge('nw_out', 'w1_stop_line', g, 3*pi/2, line)
    add_edge('nw_out', 'red', g, 3*pi/2, line)
    add_edge('red', 'w1_stop_line', g, 3*pi/2, line)


    add_edge('e3_s', 'se_in', g, pi, line)
    add_edge('se_in', 'blue', g, pi, line)
    add_edge('se_in', 's2', g, pi, line)
    add_edge('se_in', 's2_n', g, pi/2, line)
    add_edge('blue', 's2', g, pi, line)
    add_edge('blue', 's2_n', g, pi/2, line)

    return g


def distance(p1, p2, bias=0):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2)) + bias


def add_edge(p1, p2, g, angle, nav_type):
    d = distance(points[p1], points[p2], bias=_distance_bias)
    g.add_edge(p1, p2, d)
    angles[(p1, p2)] = angle
    nav_types[(p1, p2)] = nav_type


# def add_double_edge(p1, p2, g, angle):
#     add_edge(p1, p2, g, angle)
#     add_edge(p2, p1, g, (angle + pi) % pi)


# def add_complete_4(p1, p2, p3, p4, g):
#     # add_double_edge(p1, p2, g, 0)
#     # add_double_edge(p1, p3, g, 3 * pi / 2)
#     # add_double_edge(p1, p4, g, 7 * pi / 4)
#     # add_double_edge(p2, p3, g, 5 * pi / 4)
#     # add_double_edge(p2, p4, g, 3 * pi / 2)
#     # add_double_edge(p3, p4, g, 0)
#     # add_edge(p1, p2, g, pi/2)
#     add_edge(p2, p1, g, pi)
#
#     add_edge(p1, p3, g, 3*pi/2)
#     # add_edge(p3, p1, g, 3*pi/2)
#
#     add_edge(p1, p4, g, 0)
#     add_edge(p4, p1, g, pi)
#
#     add_edge(p2, p3, g, 3*pi/2)
#     add_edge(p3, p2, g, pi/2)
#
#     add_edge(p2, p4, g, 3*pi/2)
#     # add_edge(p2, p4, g, 3*pi/2)
#
#     add_edge(p3, p4, g, 0)
#     # add_edge(p3, p4, g, 0)


def add_complete_4_group(p1s, p2s, p3s, p4s, g):
    p1s = p1s if isinstance(p1s, list) else [p1s]
    p2s = p2s if isinstance(p2s, list) else [p2s]
    p3s = p3s if isinstance(p3s, list) else [p3s]
    p4s = p4s if isinstance(p4s, list) else [p4s]
    for p1 in p1s:
        for p2 in p2s:
            for p3 in p3s:
                for p4 in p4s:
                    # print p1, p2, p3, p4
                    # add_double_edge(p1, p2, g, 0)
                    # add_double_edge(p1, p3, g, 3 * pi / 2)
                    # add_double_edge(p1, p4, g, 7 * pi / 4)
                    # add_double_edge(p2, p3, g, 5 * pi / 4)
                    # add_double_edge(p2, p4, g, 3 * pi / 2)
                    # add_double_edge(p3, p4, g, 0)
                    # add_edge(p1, p2, g, pi/2)
                    if '_' not in p2:
                        add_edge(p2, p1, g, pi, line)

                    if '_' not in p1:
                        add_edge(p1, p3, g, 3 * pi / 2, amcl)

                    # add_edge(p3, p1, g, 3*pi/2)

                    if '_' not in p1:
                        add_edge(p1, p4, g, 0, amcl)

                    if '_' not in p4:
                        add_edge(p4, p1, g, pi, amcl)

                    if '_' not in p2:
                        add_edge(p2, p3, g, 3*pi/2, amcl)

                    if '_' not in p3:
                        add_edge(p3, p2, g, pi/2, amcl)

                    # add_edge(p2, p4, g, 3*pi/2)
                    if '_' not in p4:
                        add_edge(p4, p2, g, pi/2, amcl)

                    if '_' not in p3:
                        add_edge(p3, p4, g, 0, amcl)
                    # add_edge(p3, p4, g, 0)
