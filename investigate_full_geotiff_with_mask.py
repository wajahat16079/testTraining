import os
import sys
import rasterio
import numpy as np
import plotly.express as px


def read_geotiff(filename):
    with rasterio.open(filename) as src:
        blue = src.read(1)
        green = src.read(2)
        red = src.read(3)
        # mask = np.zeros(blue.shape)
        mask = src.read(11)
    return blue, green, red, mask


def prepare_mask(mask):
    # This function now returns a mask where values are 255 where mask > 0, and 0 otherwise
    return np.where(mask > 0, 255, 0)


def apply_mask_to_rgb(rgb, mask):
    # Apply a colored mask (neon pink) to the RGB image
    mask_rgb = np.zeros_like(rgb)
    mask_rgb[..., 0] = 255  # Red channel
    mask_rgb[..., 1] = 20  # Green channel very low
    mask_rgb[..., 2] = 147  # Blue channel for pink
    return np.where(mask[..., None] > 0, mask_rgb, rgb)


def plot_rgb_with_mask(blue, green, red, mask):
    # Stack and normalize RGB
    rgb = np.stack([red, green, blue], axis=-1)
    rgb = np.clip(rgb, 0, np.percentile(rgb, 99))  # Clip values to 99th percentile
    rgb_normalized = (rgb / rgb.max() * 255).astype(np.uint8)  # Normalize to 0-255

    # Prepare and apply the mask
    mask_prepared = prepare_mask(mask)
    rgb_with_mask = apply_mask_to_rgb(rgb_normalized, mask_prepared)

    # Plot using Plotly
    fig = px.imshow(rgb_with_mask, origin='upper', binary_string=True)
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    fig.show()



def main(filename):
    blue, green, red, mask = read_geotiff(filename)
    plot_rgb_with_mask(blue, green, red, mask)

if __name__ == "__main__":
    # Automatically expand the path to the home directory
    default_path = '/Users/jameslowman/Desktop/kelpwatch2/training/S2A_MSIL2A_20230924T181101_R084_T11RPL_20230925T005225_label/S2A_MSIL2A_20230924T181101_R084_T11RPL_20230925T005225.tif'
    expanded_path = os.path.expanduser(default_path)
    filename = sys.argv[1] if len(sys.argv) > 1 else expanded_path
    main(filename)