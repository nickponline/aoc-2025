def solve(filename, inscribed=False):
    from shapely.geometry import Polygon
    from shapely.prepared import prep
    xy = [tuple(map(int, line.strip().split(','))) for line in open(filename)]
    polygon = Polygon(xy)
    prepared_polygon = prep(polygon)
    max_area = 0
    for i in range(len(xy)):
        for j in range(i + 1, len(xy)):
            x1, y1 = xy[i]
            x2, y2 = xy[j]
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)
            rect = Polygon([(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)])
            if not inscribed or prepared_polygon.covers(rect):
                max_area = max(max_area, (max_x - min_x + 1) * (max_y - min_y + 1))
    return max_area
print(solve('part1.in', inscribed=False))
print(solve('part1.in', inscribed=True))