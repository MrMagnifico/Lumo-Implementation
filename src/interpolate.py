import numpy as np
from enum import Enum
from os import path
from matplotlib import pyplot as plt
from PIL import Image
from scipy.interpolate import griddata
from tqdm import trange

D = 0.97
K = 0.4375
ITER_LIMIT = 1000
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


def iterative_interp(values: np.ndarray, unknown_val = 255) -> np.ndarray:
    interpolated_arr    = values.copy().astype(INTERIM_DTYPE)
    unknown_val_cast    = values.dtype.type(unknown_val)
    to_interp           = np.where(values == unknown_val_cast, True, False)
    velocities          = np.zeros(values.shape, dtype=INTERIM_DTYPE)
    resolution          = values.shape[0:2]

    for _ in trange(ITER_LIMIT, desc="Interpolating"):
        prev_velocities = velocities.copy()
        prev_field      = interpolated_arr.copy()
        for y in range(resolution[0]):
            for x in range(resolution[1]):
                # Skip pixel if value is known
                if not np.any(to_interp[y][x]):
                    continue

                # Acquire previous field values
                prev_value  = prev_field[y][x]
                up          = safe_access(prev_field, x, y - 1)
                down        = safe_access(prev_field, x, y + 1)
                left        = safe_access(prev_field, x - 1, y)
                right       = safe_access(prev_field, x + 1, y)

                # Compute new velocity and field value
                prev_velocity   = prev_velocities[y][x]
                velocity        = (D * prev_velocity) + (K * (up + down + left + right - (4 * prev_value)))
                value           = prev_value + velocity

                # Assign new values to running arrays
                velocities[y][x]        = velocity
                interpolated_arr[y][x]  = value

    return interpolated_arr.astype(np.uint8, copy=True)


def scipy_interp(values: np.ndarray, unknown_val = 255) -> np.ndarray:
    # Acquire coords of points having concrete values
    unknown_val_cast    = np.repeat(unknown_val, values.shape[2:]).astype(values.dtype, copy=False)
    mask                = np.all(values != unknown_val_cast, axis=2)
    points              = mask.nonzero()
    points_coords       = np.argwhere(mask).astype(INTERIM_DTYPE, copy=False)

    # Interpolate for each channel
    channel_interps = []
    for channel in trange(values.shape[2], desc="Interpolating RGB channels"):
        points_values   = values[points][:, channel].astype(INTERIM_DTYPE, copy=False)
        largest_dim     = max(values.shape[0], values.shape[1])
        largest_dim_pts = np.linspace(0, largest_dim, 1)
        interp          = griddata(points_coords, points_values, (largest_dim_pts, largest_dim_pts), method='linear', fill_value=255)
        channel_interps.append(interp)
    return np.stack(channel_interps, axis=-1)


if __name__ == "__main__":
    edge_normals_img = Image.open(path.join("resources", "cat-edge-normals.png"))
    edge_normals_arr = np.asarray(edge_normals_img)
    edge_normals_arr = edge_normals_arr[:, :, 0:-1] if edge_normals_img.mode == "RGBA" else edge_normals_arr # Remove transparency if present

    # Own iterative interpolation
    interpolated_arr = iterative_interp(edge_normals_arr)
    plt.imshow(interpolated_arr)
    plt.show()

    # SciPy interpolation
    # interpolated_arr = scipy_interp(edge_normals_arr)
    # plt.imshow(interpolated_arr)
    # plt.show()
