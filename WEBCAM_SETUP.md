# Webcam Setup Guide for Pixel-to-Voxel Projector

This guide explains how to record video from your webcam(s) and process it with the existing pipeline.

## Quick Start

### 1. List Available Webcams

```bash
python webcam_recorder.py --list
```

This will show all detected cameras with their indices and resolutions.

### 2. Record a Test Video

```bash
python webcam_recorder.py --output targetvideo.mp4 --duration 30
```

This records 30 seconds from your default webcam (camera 0) and saves it as `targetvideo.mp4`.

### 3. Process the Video

Edit [PixelationDecensorer.py](PixelationDecensorer.py) configuration (lines 98-108) and run:

```bash
python PixelationDecensorer.py
```

---

## Detailed Usage

### Recording Options

#### Basic Recording

```bash
# Record until you press 'q'
python webcam_recorder.py

# Record from specific camera
python webcam_recorder.py --camera 1

# Record with custom output filename
python webcam_recorder.py --output my_test_video.mp4
```

#### Advanced Settings

```bash
# High FPS recording
python webcam_recorder.py --fps 60 --output high_fps_test.mp4

# Specific resolution
python webcam_recorder.py --resolution 1920 1080

# Timed recording without preview (headless mode)
python webcam_recorder.py --duration 120 --no-preview
```

#### During Recording

- **Press 'q'**: Stop recording
- **Press 's'**: Take a screenshot (saved as `screenshot_TIMESTAMP.png`)

### Multi-Camera Recording

To record from multiple cameras simultaneously, open separate terminals:

```bash
# Terminal 1 - Camera 0
python webcam_recorder.py --camera 0 --output camera0.mp4 --duration 60

# Terminal 2 - Camera 1
python webcam_recorder.py --camera 1 --output camera1.mp4 --duration 60
```

---

## Video Processing Configuration

After recording, configure [PixelationDecensorer.py](PixelationDecensorer.py) to process your video.

### Key Configuration Parameters

Edit these variables at the top of [PixelationDecensorer.py](PixelationDecensorer.py):

```python
# Line 98 - Input video file
VIDEO_PATH = "targetvideo.mp4"

# Line 99 - Starting frame number
START_AT_FRAME = 50

# Line 100 - Number of frames to process
MAX_FRAMES = 200

# Line 101 - Pixelation grid cell size (in pixels)
CELL_SIZE = 25.2

# Line 102 - Super-resolution factor (1-4)
SR_FACTOR = 1

# Line 103 - Window tracking search margin
TRACK_SEARCH_MARGIN = 300

# Line 104 - Hole-filling iterations
FILL_MAX_ITERS = 1200
```

### Understanding the Parameters

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| `VIDEO_PATH` | Path to your recorded video | Any .mp4 file |
| `START_AT_FRAME` | Skip initial frames | 0-100 |
| `MAX_FRAMES` | Frames to process (more = slower) | 50-500 |
| `CELL_SIZE` | Pixelation period in pixels | 10-50 |
| `SR_FACTOR` | Resolution multiplier | 1, 2, 3, or 4 |
| `TRACK_SEARCH_MARGIN` | Tracking search radius | 100-500 |
| `FILL_MAX_ITERS` | Reconstruction iterations | 500-2000 |

### Workflow Example

1. **Record test footage:**
   ```bash
   python webcam_recorder.py --output test_motion.mp4 --duration 10
   ```

2. **Edit PixelationDecensorer.py:**
   ```python
   VIDEO_PATH = "test_motion.mp4"
   START_AT_FRAME = 0
   MAX_FRAMES = 100
   CELL_SIZE = 20.0  # Adjust based on your pixelation pattern
   ```

3. **Run the processor:**
   ```bash
   python PixelationDecensorer.py
   ```

4. **Check output:**
   - Processed frames saved in the same directory
   - Console will show tracking and reconstruction progress

---

## Troubleshooting

### Camera Not Found

```bash
# Check available cameras
python webcam_recorder.py --list

# Try different camera indices
python webcam_recorder.py --camera 1
python webcam_recorder.py --camera 2
```

### Camera Opens But Shows Black Screen

- Check camera permissions (macOS: System Preferences → Security & Privacy → Camera)
- Try unplugging and reconnecting the webcam
- Close other applications using the camera

### Recording Stopped Immediately

- Ensure OpenCV is installed: `pip install opencv-python`
- Check disk space
- Verify write permissions in the output directory

### Poor Quality / Low FPS

```bash
# Increase FPS setting
python webcam_recorder.py --fps 60

# Use higher resolution
python webcam_recorder.py --resolution 1920 1080

# Check system load - close other applications
```

### Video Processing Issues

**Problem**: "File not found" error in PixelationDecensorer.py

**Solution**: Use absolute path or place video in the same directory:
```python
VIDEO_PATH = "/absolute/path/to/targetvideo.mp4"
# or
VIDEO_PATH = "targetvideo.mp4"  # if in same folder
```

**Problem**: Processing very slow

**Solution**: Reduce `MAX_FRAMES` or `FILL_MAX_ITERS`:
```python
MAX_FRAMES = 50        # Process fewer frames
FILL_MAX_ITERS = 600  # Fewer iterations
```

---

## Recommended Testing Workflow

### 1. Initial Camera Test (1 minute)
```bash
python webcam_recorder.py --list
python webcam_recorder.py --output test1.mp4 --duration 10
```

### 2. Review Recording
Open `test1.mp4` in a video player to verify quality.

### 3. Quick Processing Test
```python
# In PixelationDecensorer.py
VIDEO_PATH = "test1.mp4"
START_AT_FRAME = 0
MAX_FRAMES = 20  # Small batch for testing
```

```bash
python PixelationDecensorer.py
```

### 4. Full Capture
Once configuration is working:
```bash
python webcam_recorder.py --output final_capture.mp4 --fps 30 --duration 60
```

---

## System Requirements

### Python Dependencies
```bash
pip install opencv-python numpy
```

### Recommended Specs
- **Camera**: 720p or higher
- **Storage**: 100MB per minute of recording (varies by resolution)
- **RAM**: 4GB minimum for processing

---

## Tips for Best Results

1. **Lighting**: Ensure good lighting for clear tracking
2. **Steady Camera**: Use a tripod or stable surface
3. **Frame Rate**: 30 FPS is usually sufficient, 60 FPS for fast motion
4. **Test First**: Always do a short test recording before long captures
5. **Disk Space**: Check available space before long recordings
6. **Processing Time**: Start with small `MAX_FRAMES` values to test settings

---

## 3D Voxel Reconstruction with Multiple Webcams

For true 3D reconstruction, you need to know the **physical positions and orientations** of your cameras in 3D space.

### Understanding Camera Coordinates

The voxel reconstruction system requires this metadata for each camera:

```json
{
  "camera_index": 0,
  "frame_index": 0,
  "camera_position": [x, y, z],
  "yaw": 45.0,
  "pitch": -15.0,
  "roll": 0.0,
  "fov_degrees": 60.0,
  "image_file": "camera0_frame000.png"
}
```

**Coordinate System:**
- `camera_position`: [x, y, z] in your world coordinate system (e.g., centimeters from scene center)
- `yaw`: Rotation around vertical Z-axis (0-360°, like compass heading)
- `pitch`: Vertical angle (-90° = down, 0° = horizontal, 90° = up)
- `roll`: Camera tilt/bank angle (usually 0° for upright cameras)
- `fov_degrees`: Horizontal field of view (typically 50-70°)

---

### Method 1: Interactive Setup (Easiest)

Use the calibration tool to enter camera positions interactively:

```bash
python webcam_calibration.py --interactive
```

This launches a guided setup where you can enter positions using:
- **Manual XYZ coordinates** (if you measured a grid)
- **Physical measurements** (distances and angles - easier!)

#### Physical Measurements Example:

```
Define object/scene center: 0 0 0
Camera 0:
  Distance to object: 500 cm
  Horizontal angle: 0 degrees (North)
  Vertical angle: -15 degrees (looking down slightly)
  Height above ground: 120 cm
  FOV: 60 degrees
  Image: camera0_frame000.png
```

The tool automatically calculates XYZ positions and orientations.

---

### Method 2: Generate Example Setup

Create a test setup with 3 cameras in a circle:

```bash
python webcam_calibration.py --example
```

This creates `example_metadata.json` with three cameras at 120° intervals, all looking at the origin.

---

### Method 3: Manual Command-Line Entry

Add cameras one at a time:

```bash
# Add camera at position (0, 500, 100) looking at origin
python webcam_calibration.py --add-camera \
    --position 0 500 100 \
    --orientation 180 -15 0 \
    --fov 60 \
    --image camera0.png \
    --output metadata.json

# Add second camera
python webcam_calibration.py --add-camera \
    --position 433 -250 100 \
    --orientation 300 -15 0 \
    --fov 60 \
    --image camera1.png \
    --output metadata.json
```

---

### Method 4: Estimate Field of View (FOV)

If you don't know your camera's FOV, use a checkerboard:

```bash
# Print a checkerboard pattern (9x6 inner corners, 25mm squares)
# Take a photo with your webcam
python webcam_recorder.py --output calibration.mp4 --duration 5

# Extract a frame and estimate FOV
python webcam_calibration.py --estimate-fov frame.jpg \
    --checkerboard 9 6 \
    --square-size 25.0
```

Output: `Estimated FOV: 62.3 degrees`

---

### Complete Multi-Camera Workflow

#### 1. Set Up Your Cameras Physically

- Place 2-4 webcams around your subject
- Measure distances and angles OR place on a measured grid
- Ensure all cameras can see the subject
- Use tripods for stability

#### 2. Record Synchronized Captures

```bash
# Terminal 1
python webcam_recorder.py --camera 0 --output cam0.png --duration 1

# Terminal 2
python webcam_recorder.py --camera 1 --output cam1.png --duration 1

# Terminal 3
python webcam_recorder.py --camera 2 --output cam2.png --duration 1
```

Or extract frames from videos you already recorded.

#### 3. Create Camera Metadata

```bash
python webcam_calibration.py --interactive
```

Enter measurements for each camera. Save as `metadata.json`.

#### 4. Build Voxel Grid

Compile the C++ ray-casting engine:

```bash
g++ -std=c++17 -O2 -fopenmp ray_voxel.cpp -o ray_voxel
```

Run the voxel builder:

```bash
./ray_voxel metadata.json ./images voxel_grid.bin
```

Where:
- `metadata.json` = your camera positions
- `./images` = directory containing your camera images
- `voxel_grid.bin` = output 3D voxel data

#### 5. Visualize Results

```bash
python voxelmotionviewer.py
```

Edit [voxelmotionviewer.py](voxelmotionviewer.py) first to point to your `voxel_grid.bin`.

---

### Tips for Accurate 3D Reconstruction

1. **Camera Spacing**: Place cameras 60-120 degrees apart for best coverage
2. **Distance**: Keep cameras at similar distances from the subject
3. **Height Variation**: Varying heights helps with vertical detail
4. **Measurement Accuracy**: ±5cm error is acceptable for most setups
5. **Synchronization**: Take all images at the same moment
6. **Lighting**: Consistent lighting across all camera views
7. **Calibration Object**: Place a known-size object in scene to verify scale

---

### Measurement Tips

**If you have a measured grid:**
- Place cameras at grid intersections
- Use grid coordinates directly as XYZ positions
- Measure camera heights separately

**If measuring by hand:**
- Use a measuring tape for distances
- Use a compass app for horizontal angles
- Use a protractor or level app for vertical angles
- Measure from a consistent reference point (scene center)

**Using reference objects:**
- Place a meterstick or ruler in the scene
- After reconstruction, verify dimensions match reality
- Adjust scale in visualization if needed

---

### Troubleshooting Calibration

**Problem**: Reconstruction looks wrong/distorted

**Solutions:**
- Verify camera positions are accurate
- Check that yaw/pitch/roll angles are correct
- Ensure FOV is accurate (use `--estimate-fov`)
- Verify images match the metadata order

**Problem**: Object appears in wrong location

**Solutions:**
- Check that object center coordinates are consistent
- Verify all cameras use same coordinate system origin
- Ensure positive/negative directions are consistent

**Problem**: Sparse/incomplete voxel data

**Solutions:**
- Add more camera views
- Increase ray-casting steps in C++ code
- Verify all cameras can see the subject
- Check that `clip_end` distance is sufficient

---

### Example: Simple Tabletop Setup

**Setup:**
- Object: Small figurine at center of table
- Table marked with tape at 0°, 120°, 240°
- All cameras 50cm from object, 30cm above table

**Measurements:**
```bash
python webcam_calibration.py --interactive

# Camera 0 (North)
Distance: 50
Horizontal angle: 0
Vertical angle: -30
Height: 30
FOV: 60
Image: north.png

# Camera 1 (Southeast)
Distance: 50
Horizontal angle: 120
Vertical angle: -30
Height: 30
FOV: 60
Image: southeast.png

# Camera 2 (Southwest)
Distance: 50
Horizontal angle: 240
Vertical angle: -30
Height: 30
FOV: 60
Image: southwest.png
```

**Result:** Produces clean 3D reconstruction of the figurine from three angles.

---

## Additional Resources

- See [blenderrenderscript.py](blenderrenderscript.py) for reference metadata structure
- See [ray_voxel.cpp](ray_voxel.cpp) for ray-casting implementation details
- See [webcam_calibration.py](webcam_calibration.py) for calibration tool source code
