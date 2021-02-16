# whitebg-erase
A CLI tool for erasing white backgrounds from images.

Replace white backgrounds with transparency while ignoring small holes in the foreground. Consistent, conservative, and fast.

## Motivation
White-background product images are common in the world of ecommerce and dropshipping. If your website has a background, using transparency-backed product images will make your products appear to float directly over the background. Alternatively, you might wish to replace the white backgrounds with new ones. With this tool, you'll have your work cut out for you.

## Core Algorithms
##### Global Luminosity Threshold (GLT)
This program uses a sophisticated **Global Luminosity Threshold** algorithm to erase white backgrounds. It basically works by erasing every pixel which is above the predetermined luminosity threshold, a process which is simple and fast.

But there are problems with the algorithm as described. The first problem is that it cuts off too much at the foreground's boundaries. Sometimes chunks of foreground near the boundary will be missing, and almost always the boundaries are left jagged. The second problem is that it erases too much from within the foreground. Images with glare hotspots are turned into swiss cheese&mdash;a most undesirable result.

The solution is to introduce two layers of sophistication. The first problem can be solved by preprocessing the images with blur. Adding blur helps prevent the algorithm from erasing too much at the boundaries and results in a smoother boundary overall. The second problem can be solved by ignoring small holes. This preserves such things as glare hotspots and eyeball-whites.

Even with these added layers of sophistication, output images sometimes require further doctoring. The algorithm is both robust and fast, but alas, not perfect. It is designed to be consistent and conservative.

##### White Border Test (WBT)
Another important algorithm is the **White Border Test**, designed to rapidly decide whether an image has a white background. Since GLT is useless on images with non-white backgrounds, it is best to skip over them.

The test algorithm takes an image and proceeds as follows. First, convert the image to grayscale to get its luminosity. Then, extract all 4 sides of the image's border and calculate the mean luminosity of each. Finally, check if at least 3 out of 4 sides are above the predetermined luminosity threshold. If this is the case, then the image passes the test&mdash;otherwise not.

## Usage
Run the script with the source directory (`src`) as its sole positional argument. The source directory is the directory containing the white-background images you want to process.

```shell
python main.py C:\Users\usr\Pictures\product_images
```

The program will process each image in the source directory and output it as a PNG file. The results will be stored in `...\product_images results`. You can specify a custom destination directory using the optional argument `--dst`.

#### Optional Arguments
| Argument               | Effect                                            | Default                  | Type  |
| ---------------------- | ------------------------------------------------- | ------------------------ | ----- |
| `-h`, `--help`         | Show help message and exit.                       | N/A                      | N/A   |
| `-b`, `--check-border` | Ensure white border before processing.            | N/A                      | N/A   |
| `-c`, `--copy-failed`  | Copy and set aside images which fail border test. | N/A                      | N/A   |
| `-D`, `--dst`          | Set the destination directory for results.        | src + ' results'         | str   |
| `-L`, `--lum-thresh`   | Luminosity threshold above which is white.        | 0.95                     | float |
| `-G`, `--gaussian`     | Sigma for Gaussian filter (higher for more blur). | 1.0                      | float |
| `-H`, `--hole-thresh`  | Ignore holes with area below this threshold.      | 750                      | int   |
| `-T`, `--border-thick` | Thickness in pixels for border test.              | 10                       | int   |
| `-S`, `--border-sides` | Minimum white sides to pass border test.          | 3                        | int   |
| `-B`, `--batch-size`   | Number of images per batch.                       | 50                       | int   |
| `-W`, `--workers`      | Number of threads to create.                      | CPU count                | int   |


## Todo
- [ ] Accommodate wide range of color schemes.
- [X] Add white border test for checking if an image has a white background.
- [X] Implement and test multithreading.
- [ ] Write docstrings.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
