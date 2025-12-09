def point_in_polygon(px, py, poly):
    n = len(poly)
    inside = False
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2):
            cross = (px - x1) * (y2 - y1) - (py - y1) * (x2 - x1)
            if cross == 0:
                return True
        if ((y1 > py) != (y2 > py)) and (px < (x2 - x1) * (py - y1) / (y2 - y1) + x1):
            inside = not inside
    return inside

def segments_intersect(p1, p2, p3, p4):
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
    
    def on_segment(a, b, c):
        return (min(a[0], c[0]) <= b[0] <= max(a[0], c[0]) and
                min(a[1], c[1]) <= b[1] <= max(a[1], c[1]))
    
    d1 = (p4[0] - p3[0]) * (p1[1] - p3[1]) - (p4[1] - p3[1]) * (p1[0] - p3[0])
    d2 = (p4[0] - p3[0]) * (p2[1] - p3[1]) - (p4[1] - p3[1]) * (p2[0] - p3[0])
    d3 = (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])
    d4 = (p2[0] - p1[0]) * (p4[1] - p1[1]) - (p2[1] - p1[1]) * (p4[0] - p1[0])
    
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    return False

def polygon_covers_rect(poly, rect_corners):
    for corner in rect_corners:
        if not point_in_polygon(corner[0], corner[1], poly):
            return False
    
    n = len(poly)
    rect_edges = [(rect_corners[i], rect_corners[(i + 1) % 4]) for i in range(4)]
    
    for i in range(n):
        p1, p2 = poly[i], poly[(i + 1) % n]
        for r1, r2 in rect_edges:
            if segments_intersect(p1, p2, r1, r2):
                return False
    return True

def solve(filename, inscribed=False):
    xy = [tuple(map(int, line.strip().split(','))) for line in open(filename)]
    max_area = 0
    for i in range(len(xy)):
        for j in range(i + 1, len(xy)):
            x1, y1 = xy[i]
            x2, y2 = xy[j]
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)
            rect_corners = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
            if not inscribed or polygon_covers_rect(xy, rect_corners):
                max_area = max(max_area, (max_x - min_x + 1) * (max_y - min_y + 1))
    return max_area

if __name__ == "__main__":
    print(solve('part1.in', inscribed=False))
    print(solve('part1.in', inscribed=True))