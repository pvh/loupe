# Loupe

## Configuration

### Surface Dial

You'll need to pair the Surface Dial, which should appear in `dev/input/event{n, n+1}` (edit the source if the dial itself isn't at 0).

### LEDs

The LEDs require root for mmap()ing purposes, so you'll need to run this whole shebang with sudo (remember your pipenv there.)

You also need to disable the soundcard, since it competes for the PCM / DMA access.

See: https://github.com/jgarff/rpi_ws281x for details.

