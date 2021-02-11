# white-background-removal

A CLI tool for removing white backgrounds from images.

Replace white backgrounds with transparency while optionally ignoring holes in the foreground object.

## Usage
Run the program with the source directory (`src`) as its sole positional argument. The source directory is the directory containing the white-background images you want to process.

```shell
python main.py C:\Users\usr\Pictures\product_images
```

The program will process each image in the source directory and output it as a PNG file. The results will be stored in `C:\Users\usr\Pictures\product_images results`. You can specify a custom destination directory using the optional argument `--dst`.

## Optional Arguments

| Argument       | Effect                                            | Default                  | Type  |
| -------------- | ------------------------------------------------- | ------------------------ | ----- |
| `-h`, `--help` | Show help message and exit.                       | N/A                      | N/A   |
| `--dst`        | Set the destination directory for results.        | src + ' results' | str   |
| `--thresh`     | Luminosity threshold above which is white.        | 0.95                     | float |
| `--blur`       | Sigma for Gaussian filter (higher for more blur). | 1.0                      | float |
| `--hole`       | Ignore holes below this area threshold.           | 750                      | int   |

## Known Issues

- Program assumes the input images are RGB.
- Only processes one image at a time.

## Todo
- [ ] Accommodate wide range of color schemes.
- [ ] Add white border test for checking if an image has a white background.
- [ ] Implement and test multithreading.
- [ ] Write docstrings.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
