import sys

def getTime(last, n):
    if last == -1:
        return [n]
    else:
        if n - last > 3000:
            return [n]
        else:
            return []

if __name__ == "__main__":
    x = sys.stdin.readlines()
    x = list(map(float, x))
    x.sort()

    agg = []
    for line in x:
        v = agg[-1] if len(agg) > 0 else -1
        agg = agg + getTime(v, int(float(line)))

    for x in agg:
        print(x)