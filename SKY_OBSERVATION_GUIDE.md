# Sky Observation Setup Guide

Guide for using webcams to detect and track moving objects in the sky (satellites, meteors, aircraft) with 3D voxel reconstruction.

## Concept

Unlike object-centered setups, sky observation doesn't have a central object to focus on. Instead:

- **Cameras point at overlapping regions of sky**
- **Moving objects** (satellites, meteors, aircraft) pass through these overlapping fields of view
- **3D reconstruction** triangulates object positions and trajectories from multiple camera views
- **No central reference point** needed - cameras point at sky coordinates (azimuth/altitude)

---

## Quick Start: 3-Camera Sky Setup

### 1. Generate Example Configuration

```bash
python webcam_calibration.py --example-sky
```

This creates `example_sky_metadata.json` with three cameras pointing at overlapping sky regions.

### 2. Review the Setup

The example creates:
- **Camera 0** at origin (0, 0, 0), pointing NNE (30°) at 45° elevation
- **Camera 1** at (100, 0, 0), pointing NNW (340°) at 45° elevation
- **Camera 2** at (50, 86.6, 0), pointing N (0°) at 50° elevation

All three fields of view overlap in the northern sky around 45° elevation.

### 3. Adapt to Your Setup

Edit the positions to match your camera locations (in meters, feet, etc.).

---

## Interactive Sky Camera Setup

### Step-by-Step

```bash
python webcam_calibration.py --interactive
```

Choose option **2: Sky observation**

For each camera, you'll need:

1. **Camera Position** [x, y, z]
   - Use any consistent units (meters, feet, etc.)
   - First camera at origin: `0 0 0`
   - Spread cameras apart for better triangulation (50-200 units)
   - Z is usually 0 (ground level) unless cameras are elevated

2. **Azimuth** (0-360°)
   - Compass direction camera points
   - 0 = North, 90 = East, 180 = South, 270 = West
   - Use compass app on phone for accuracy

3. **Altitude** (0-90°)
   - Angle above horizon
   - 0 = horizontal (at horizon)
   - 45 = halfway to zenith
   - 90 = straight up (zenith)
   - Use inclinometer/level app on phone

4. **FOV** (Field of View)
   - Typical webcams: 60-70°
   - Use `--estimate-fov` if unknown

5. **Image filename**
   - Path to captured image from this camera

---

## Understanding Sky Coordinates

### Azimuth (Compass Direction)

```
        0° (North)
           |
           |
270° ------+------ 90° (East)
 (West)    |
           |
        180° (South)
```

### Altitude (Elevation Angle)

```
     90° (Zenith - straight up)
        |
        |
     45°|___
        |    \___
        |        \___
      0°|____________\  (Horizon)
```

### Creating Overlap

For 3 cameras with 60° FOV to overlap:
- Point cameras within ~30-40° of each other in azimuth
- Keep altitude angles similar (±10°)

**Example for northern sky coverage:**
- Camera 0: Az=350°, Alt=45°
- Camera 1: Az=10°, Alt=45°
- Camera 2: Az=0°, Alt=50°

All three overlap around 0° (North) at ~45° elevation.

---

## Physical Setup Tips

### Camera Placement

**Option 1: Triangular Grid (Recommended)**
```
Camera 2
   *
  / \
 /   \
*-----*
Camera 0  Camera 1

Spacing: 50-200m apart
```

**Option 2: Linear Array**
```
*--------*--------*
Cam 0   Cam 1   Cam 2

Spacing: 50-100m apart
```

**Option 3: Compact (for small areas)**
```
  *
 ***  All within 10-20m
  *

Useful for lower-altitude objects (drones, aircraft)
```

### Measuring Camera Positions

1. **Pick a reference point** (tree, building, corner of property)
2. **Set as origin**: (0, 0, 0)
3. **Measure distances** with tape measure or GPS
4. **Use compass** to determine X/Y coordinates:
   - East = +X
   - North = +Y
   - Height = Z (usually 0 if all on ground)

**Example:**
- Camera 0 at reference point: (0, 0, 0)
- Camera 1 is 100m East: (100, 0, 0)
- Camera 2 is 50m East, 87m North: (50, 87, 0)

### Pointing Cameras

1. **Use compass app** on phone for azimuth
2. **Use level/inclinometer app** for altitude angle
3. **Mount cameras securely** (tripods ideal)
4. **Point at overlapping sky region**

---

## Common Sky Observation Scenarios

### Satellite Tracking

**Setup:**
- 3-4 cameras spread 100-300m apart
- All pointing at similar region (e.g., southern sky at 30-60° elevation)
- Wide FOV (60-70°) to capture satellite paths
- Timed captures at same moment (within 1 second)

**Camera Configuration:**
```bash
# Camera 0: Southwest
Position: 0 0 0
Azimuth: 225° (Southwest)
Altitude: 45°

# Camera 1: South
Position: 150 0 0
Azimuth: 180° (South)
Altitude: 45°

# Camera 2: Southeast
Position: 75 130 0
Azimuth: 135° (Southeast)
Altitude: 45°
```

### Meteor Detection

**Setup:**
- Multiple cameras covering wide sky area
- Higher altitude angles (60-80°) for overhead meteors
- Synchronized capture triggers (same timestamp)
- High sensitivity sensors for dim meteors

**Camera Configuration:**
```bash
# Wide field coverage
Camera 0: Az=0° (North), Alt=70°
Camera 1: Az=120° (Southeast), Alt=70°
Camera 2: Az=240° (Southwest), Alt=70°
```

### Aircraft/Drone Tracking

**Setup:**
- Lower altitude angles (20-45°) for closer objects
- Closer camera spacing (20-100m) for better resolution
- Higher frame rate capture if available

**Camera Configuration:**
```bash
# Low-altitude coverage
Camera 0: Az=0°, Alt=30°
Camera 1: Az=30°, Alt=35°
Camera 2: Az=350°, Alt=30°
```

---

## Command-Line Examples

### Add First Sky Camera

```bash
python webcam_calibration.py --add-sky-camera \
    --position 0 0 0 \
    --azimuth 30 \
    --altitude 45 \
    --fov 60 \
    --image cam0_sky.png \
    --output sky_metadata.json
```

### Add Second Camera (overlapping)

```bash
python webcam_calibration.py --add-sky-camera \
    --position 100 0 0 \
    --azimuth 340 \
    --altitude 45 \
    --fov 60 \
    --image cam1_sky.png \
    --output sky_metadata.json
```

### Add Third Camera

```bash
python webcam_calibration.py --add-sky-camera \
    --position 50 86.6 0 \
    --azimuth 0 \
    --altitude 50 \
    --fov 60 \
    --image cam2_sky.png \
    --output sky_metadata.json
```

---

## Capture Workflow

### 1. Record Sky Images

```bash
# Terminal 1 - Camera 0
python webcam_recorder.py --camera 0 --output cam0_sky.png --duration 1

# Terminal 2 - Camera 1
python webcam_recorder.py --camera 1 --output cam1_sky.png --duration 1

# Terminal 3 - Camera 2
python webcam_recorder.py --camera 2 --output cam2_sky.png --duration 1
```

**Important:** Capture all images at the same moment for accurate 3D reconstruction.

### 2. Create Metadata

```bash
python webcam_calibration.py --interactive
# Choose: Sky observation mode
# Enter each camera's position and pointing direction
```

### 3. Build Voxel Grid

```bash
g++ -std=c++17 -O2 -fopenmp ray_voxel.cpp -o ray_voxel
./ray_voxel sky_metadata.json ./images voxel_grid.bin
```

### 4. Visualize

```bash
python voxelmotionviewer.py
```

---

## Tips for Accurate Results

### Camera Spacing

- **Satellites/High altitude**: 100-300m spacing
- **Aircraft/Medium altitude**: 50-150m spacing
- **Drones/Low altitude**: 20-50m spacing

### Overlap Verification

Calculate field of view overlap:
- FOV = 60°
- Pointing difference = 30°
- Overlap = FOV - difference = 30° ✓ (good)

### Synchronization

For moving objects, capture timing is critical:
- Use synchronized triggers if possible
- Manual capture: count down "3, 2, 1, capture" together
- GPS time sync for best accuracy

### Reference Point in Sky

The system automatically creates a reference point 10km away in the direction each camera points. This gives the voxel grid a center region where the overlapping views converge.

---

## Troubleshooting

### No overlapping fields of view

**Symptoms:** Voxel grid is empty or has disconnected regions

**Solutions:**
- Check azimuth/altitude angles point cameras toward same sky region
- Reduce angle differences (aim for <40° separation)
- Verify FOV is wide enough

### Objects appear at wrong position

**Symptoms:** Reconstructed position doesn't match known location

**Solutions:**
- Verify camera positions are accurate
- Check azimuth measurements with compass
- Confirm altitude angles (use inclinometer)
- Ensure all cameras use same coordinate system

### Poor reconstruction quality

**Symptoms:** Fuzzy or incomplete voxel data

**Solutions:**
- Add more camera views (4-6 cameras better than 3)
- Increase camera spacing for better triangulation
- Ensure good image quality (focus on infinity)
- Verify timing synchronization

---

## Advanced: Time-Series Tracking

For tracking moving objects over time, capture multiple frames:

### Sequential Frames

```python
# In webcam_calibration.py, add multiple frames per camera:

for frame_idx in range(10):  # 10 time steps
    for cam_idx in range(3):  # 3 cameras
        calibrator.add_sky_camera(
            camera_index=cam_idx,
            frame_index=frame_idx,
            position=camera_positions[cam_idx],
            azimuth=azimuths[cam_idx],
            altitude=altitudes[cam_idx],
            roll=0,
            fov_degrees=60,
            image_file=f"cam{cam_idx}_frame{frame_idx:03d}.png"
        )
```

This allows tracking object motion through the voxel space over time.

---

## Example: Satellite Pass Setup

**Goal:** Track ISS passing overhead

**Setup:**
1. Check satellite tracker for pass time/direction
2. Position 3 cameras in triangle (150m spacing)
3. Point all cameras at predicted path region
4. Use 60° FOV webcams
5. Capture synchronized images during pass

**Camera Config:**
```
Camera 0: (0, 0, 0), Az=270° (West), Alt=50°
Camera 1: (150, 0, 0), Az=0° (North), Alt=50°
Camera 2: (75, 130, 0), Az=315° (Northwest), Alt=55°

All overlap in northwest sky at ~50° elevation
```

**Result:** 3D position of ISS as it passes through overlapping fields of view.
