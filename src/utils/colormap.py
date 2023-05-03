colors = [
    '#BA55D3',
    '#FF52AF',
    '#FF6E86',
    '#FF9C65',
    '#FFCC59'
]

index = 0


def reset_index():
    global index
    index = 0


def next_color() -> str:
    global index
    index += 1
    return colors[index % len(colors)]


def now_color() -> str:
    global index
    return colors[index % len(colors)]
