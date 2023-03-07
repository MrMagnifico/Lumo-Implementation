import numpy as np
from enum import Enum
from os import path
from matplotlib import pyplot as plt
from PIL import Image
from tqdm import trange

D = 0.97
K = 0.4375
ITER_LIMIT = 50
INTERIM_DTYPE = np.float32

class PaddingStrategy(Enum):
    ZERO    = 1
    NEAREST = 2


def safe_access(values: np.ndarray, x: int, y: int, pad_strat = PaddingStrategy.NEAREST):
    # Apply padding strategy
    dims = values.shape[0:2]
    if not ((0 <= y < dims[0]) and (0 <= x < dims[1])):
        if pad_strat is PaddingStrategy.ZERO:
            return 0
        elif pad_strat is PaddingStrategy.NEAREST:
            y = np.clip(y, 0, dims[0] - 1)
            x = np.clip(x, 0, dims[1] - 1)

    return values[y][x]


def iterative_interp(values: np.ndarray, unknown_val = 255, ignore_val = 0) -> np.ndarray:
    interpolated_arr    = values.copy().astype(INTERIM_DTYPE)
    unknown_val_cast    = values.dtype.type(unknown_val)
    ignore_val_cast     = values.dtype.type(ignore_val)
    to_interp           = np.where(values == unknown_val_cast, True, False)
    to_ignore           = np.where(values == ignore_val_cast, True, False)
    velocities          = np.zeros(values.shape, dtype=INTERIM_DTYPE)
    resolution          = values.shape[0:2]

    for _ in trange(ITER_LIMIT, desc="Interpolating"):
        prev_velocities = velocities.copy()
        prev_field      = interpolated_arr.copy()
        for y in range(resolution[0]):
            for x in range(resolution[1]):
                # Skip pixel if value is known or should be ignored
                if (not np.any(to_interp[y][x])) or (np.all(to_ignore[y][x])):
                    continue

                # Acquire previous field values
                prev_value  = prev_field[y][x]
                up          = safe_access(prev_field, x, y - 1)
                down        = safe_access(prev_field, x, y + 1)
                left        = safe_access(prev_field, x - 1, y)
                right       = safe_access(prev_field, x + 1, y)

                # If values are equal to the ignore value, replace them with the previous value
                up      = prev_value if np.all(up == ignore_val_cast) else up
                down    = prev_value if np.all(down == ignore_val_cast) else down
                left    = prev_value if np.all(left == ignore_val_cast) else left
                right   = prev_value if np.all(right == ignore_val_cast) else right

                # Compute new velocity and field value
                prev_velocity   = prev_velocities[y][x]
                velocity        = (D * prev_velocity) + (K * (up + down + left + right - (4 * prev_value)))
                value           = prev_value + velocity

                # Assign new values to running arrays
                velocities[y][x]        = velocity
                interpolated_arr[y][x]  = value

    return interpolated_arr.astype(np.uint8, copy=True)


if __name__ == "__main__":
    edge_normals_img = Image.open(path.join("resources", "cat-edge-normals-ignore.png"))
    edge_normals_arr = np.asarray(edge_normals_img)
    edge_normals_arr = edge_normals_arr[:, :, 0:-1] if edge_normals_img.mode == "RGBA" else edge_normals_arr # Remove transparency if present

    interpolated_arr = iterative_interp(edge_normals_arr)
    plt.imshow(interpolated_arr)
    plt.show()
