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
        if ((y1 > py) != (y2 > py)) and (px < (x2 - x1) * (py - y1) // (y2 - y1) + x1):
            inside = not inside
    return inside

def segments_intersect(p1, p2, p3, p4):
    d1 = (p4[0] - p3[0]) * (p1[1] - p3[1]) - (p4[1] - p3[1]) * (p1[0] - p3[0])
    d2 = (p4[0] - p3[0]) * (p2[1] - p3[1]) - (p4[1] - p3[1]) * (p2[0] - p3[0])
    d3 = (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])
    d4 = (p2[0] - p1[0]) * (p4[1] - p1[1]) - (p2[1] - p1[1]) * (p4[0] - p1[0])
    
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    return False

def polygon_covers_rect(poly, min_x, min_y, max_x, max_y):
    # Check all four corners
    if not (point_in_polygon(min_x, min_y, poly) and 
            point_in_polygon(max_x, min_y, poly) and
            point_in_polygon(max_x, max_y, poly) and
            point_in_polygon(min_x, max_y, poly)):
        return False
    
    # Check for edge intersections
    n = len(poly)
    rect_corners = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
    
    for i in range(n):
        p1, p2 = poly[i], poly[(i + 1) % n]
        for j in range(4):
            r1, r2 = rect_corners[j], rect_corners[(j + 1) % 4]
            if segments_intersect(p1, p2, r1, r2):
                return False
    return True

def solve(filename, inscribed=False):
    xy = [tuple(map(int, line.strip().split(','))) for line in open(filename)]
    max_area = 0
    
    # Precompute bounding box for early rejection
    if inscribed:
        poly_min_x = min(x for x, y in xy)
        poly_max_x = max(x for x, y in xy)
        poly_min_y = min(y for x, y in xy)
        poly_max_y = max(y for x, y in xy)
    
    for i in range(len(xy)):
        for j in range(i + 1, len(xy)):
            x1, y1 = xy[i]
            x2, y2 = xy[j]
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)
            
            # Early rejection: if rectangle is outside polygon bounding box
            if inscribed and (min_x < poly_min_x or max_x > poly_max_x or 
                            min_y < poly_min_y or max_y > poly_max_y):
                continue
            
            if not inscribed or polygon_covers_rect(xy, min_x, min_y, max_x, max_y):
                max_area = max(max_area, (max_x - min_x + 1) * (max_y - min_y + 1))
    return max_area

if __name__ == "__main__":
    print(solve('part1.in', inscribed=False))
    print(solve('part1.in', inscribed=True))