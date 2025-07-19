import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from skimage.draw import line_aa, ellipse_perimeter
from math import atan2, hypot
from skimage.transform import resize
import os

# ============================
# Hardcoded settings
# ============================

INPUT_FILE = "INSERT YOUR IMAGE FILE PATH"
SNAPSHOT_INTERVAL = 50  # every 50 pulls
PULL_AMOUNT = 4000  # total pulls
NAIL_STEP = 4  # distance between nails on ellipse
SIDE_LEN = 400  # side length for square resize
STRENGTH = -0.1  # draw on white canvas
WB = False  # draw on white canvas
RADIUS1_MULTIPLIER = 1.0
RADIUS2_MULTIPLIER = 1.0

# ============================
# Helper functions
# ============================

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

def largest_square(image: np.ndarray) -> np.ndarray:
    short_edge = np.argmin(image.shape[:2])
    short_edge_half = image.shape[short_edge] // 2
    long_edge_center = image.shape[1 - short_edge] // 2
    if short_edge == 0:
        return image[:, long_edge_center - short_edge_half: long_edge_center + short_edge_half]
    if short_edge == 1:
        return image[long_edge_center - short_edge_half: long_edge_center + short_edge_half, :]

def create_circle_nail_positions(shape, nail_step=2, r1_multip=1, r2_multip=1):
    height, width = shape
    centre = (height // 2, width // 2)
    radius = min(height, width) // 2 - 1
    rr, cc = ellipse_perimeter(centre[0], centre[1], int(radius * r1_multip), int(radius * r2_multip))
    nails = list(set([(rr[i], cc[i]) for i in range(len(cc))]))
    nails.sort(key=lambda c: atan2(c[0] - centre[0], c[1] - centre[1]))
    nails = nails[::nail_step]
    return np.asarray(nails)

def init_canvas(shape, black=False):
    return np.zeros(shape) if black else np.ones(shape)

def get_aa_line(from_pos, to_pos, str_strength, picture):
    rr, cc, val = line_aa(from_pos[0], from_pos[1], to_pos[0], to_pos[1])
    line = picture[rr, cc] + str_strength * val
    line = np.clip(line, a_min=0, a_max=1)
    return line, rr, cc

def find_best_nail_position(current_position, nails, str_pic, orig_pic, str_strength):
    best_cumulative_improvement = -99999
    best_nail_position = None
    best_nail_idx = None

    for nail_idx, nail_position in enumerate(nails):
        overlayed_line, rr, cc = get_aa_line(current_position, nail_position, str_strength, str_pic)
        before_overlayed_line_diff = np.abs(str_pic[rr, cc] - orig_pic[rr, cc])**2
        after_overlayed_line_diff = np.abs(overlayed_line - orig_pic[rr, cc])**2
        cumulative_improvement = np.sum(before_overlayed_line_diff - after_overlayed_line_diff)

        if cumulative_improvement >= best_cumulative_improvement:
            best_cumulative_improvement = cumulative_improvement
            best_nail_position = nail_position
            best_nail_idx = nail_idx

    return best_nail_idx, best_nail_position, best_cumulative_improvement

def scale_nails(x_ratio, y_ratio, nails):
    return [(int(y_ratio * nail[0]), int(x_ratio * nail[1])) for nail in nails]

def pull_order_to_array_bw(order, canvas, nails, strength):
    for pull_start, pull_end in zip(order, order[1:]):
        rr, cc, val = line_aa(
            nails[pull_start][0], nails[pull_start][1],
            nails[pull_end][0], nails[pull_end][1]
        )
        canvas[rr, cc] += val * strength
    return np.clip(canvas, a_min=0, a_max=1)

def get_unique_output_folder(base_folder):
    if not os.path.exists(base_folder):
        return base_folder
    counter = 1
    while True:
        new_folder = f"{base_folder}_{counter}"
        if not os.path.exists(new_folder):
            return new_folder
        counter += 1

# ============================
# MAIN LOGIC
# ============================

# ✅ Always create unique output folder FIRST
base_output = os.path.join(os.path.dirname(INPUT_FILE), "Output")
OUTPUT_FOLDER = get_unique_output_folder(base_output)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "Final.jpg")

img = mpimg.imread(INPUT_FILE)
if np.any(img > 1):
    img = img / 255

img = largest_square(img)
img = resize(img, (SIDE_LEN, SIDE_LEN))
shape = (len(img), len(img[0]))

nails = create_circle_nail_positions(shape, nail_step=NAIL_STEP,
                                     r1_multip=RADIUS1_MULTIPLIER, r2_multip=RADIUS2_MULTIPLIER)
orig_pic = rgb2gray(img) * 0.9
str_pic = init_canvas(shape, black=WB)

pull_order = []
thread_length_px = 0

current_position = nails[0]
pull_order.append(0)

for i in range(1, PULL_AMOUNT + 1):
    idx, best_nail_position, best_cumulative_improvement = find_best_nail_position(
        current_position, nails, str_pic, orig_pic, STRENGTH
    )

    if best_cumulative_improvement <= 0:
        break

    pull_order.append(idx)
    best_overlayed_line, rr, cc = get_aa_line(current_position, best_nail_position, STRENGTH, str_pic)
    str_pic[rr, cc] = best_overlayed_line

    chord = hypot(best_nail_position[0] - current_position[0],
                  best_nail_position[1] - current_position[1])
    thread_length_px += chord

    current_position = best_nail_position

    if i % SNAPSHOT_INTERVAL == 0:
        blank = init_canvas(shape, black=WB)
        scaled_nails = scale_nails(1, 1, nails)
        result = pull_order_to_array_bw(pull_order, blank.copy(), scaled_nails, STRENGTH)
        snapshot_name = os.path.join(OUTPUT_FOLDER, f"{i}.jpg")
        mpimg.imsave(snapshot_name, result, cmap=plt.get_cmap("gray"), vmin=0.0, vmax=1.0)

total_length_cm = thread_length_px * (1.0 / SIDE_LEN) * 70  # approx for 70cm board

# ✅ Save final image
blank = init_canvas(shape, black=WB)
scaled_nails = scale_nails(1, 1, nails)
result = pull_order_to_array_bw(pull_order, blank.copy(), scaled_nails, STRENGTH)
mpimg.imsave(OUTPUT_FILE, result, cmap=plt.get_cmap("gray"), vmin=0.0, vmax=1.0)

# ✅ Save pull sequence
seq_file = os.path.join(OUTPUT_FOLDER, "thread_sequence.txt")
unique_nails_used = len(set(pull_order))
with open(seq_file, "w") as f:
    f.write(f"Estimated total thread length: {total_length_cm:.2f} cm\n")
    f.write(f"Total unique nails used: {unique_nails_used}\n")
    f.write("Thread pull sequence:\n")
    f.write("-".join([str(x) for x in pull_order]))

print(f"✅ Final image saved to: {OUTPUT_FILE}")
print(f"✅ Thread sequence saved to: {seq_file}")
print(f"✅ Total unique nails used: {unique_nails_used}")
