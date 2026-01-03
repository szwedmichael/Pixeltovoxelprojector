# Installation Guide

Complete setup instructions for the Pixel-to-Voxel Projector and webcam observation system.

---

## Quick Start (pipenv - Recommended)

### 1. Install pipenv

```bash
# macOS/Linux
pip install --user pipenv

# Or via Homebrew (macOS)
brew install pipenv
```

### 2. Install all dependencies

```bash
# In the project directory
pipenv install
```

### 3. Activate virtual environment

```bash
pipenv shell
```

### 4. Test installation

```bash
# List available cameras
python webcam_recorder.py --list

# Generate example calibration
python webcam_calibration.py --example-sky
```

---

## Manual Installation (pip)

### Prerequisites

- Python 3.8 or higher
- C++ compiler (for ray-casting engine)
  - macOS: Xcode Command Line Tools (`xcode-select --install`)
  - Linux: GCC (`sudo apt-get install build-essential`)
  - Windows: Visual Studio Build Tools

### Python Dependencies

```bash
pip install numpy opencv-python pyvista astropy matplotlib pybind11
```

**Individual packages:**
- `numpy` - Numerical computing
- `opencv-python` - Computer vision and video capture
- `pyvista` - 3D visualization
- `astropy` - Astronomy data handling (FITS files)
- `matplotlib` - Plotting
- `pybind11` - C++ Python bindings

---

## Platform-Specific Setup

### macOS

```bash
# Install Xcode Command Line Tools (for C++ compiler)
xcode-select --install

# Install pipenv
pip3 install --user pipenv

# Install dependencies
pipenv install

# Activate environment
pipenv shell
```

**Camera permissions:**
- System Preferences → Security & Privacy → Camera
- Allow Terminal/IDE to access camera

### Linux (Ubuntu/Debian)

```bash
# Install build tools
sudo apt-get update
sudo apt-get install build-essential python3-pip python3-dev

# Install OpenMP (for parallel processing)
sudo apt-get install libomp-dev

# Install pipenv
pip3 install --user pipenv

# Install dependencies
pipenv install

# Activate environment
pipenv shell
```

### Windows

```bash
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/
# Select "Desktop development with C++" workload

# Install pipenv
pip install pipenv

# Install dependencies
pipenv install

# Activate environment
pipenv shell
```

---

## Compiling C++ Components

The voxel ray-casting engine is written in C++ for performance.

### Build Python Extension (Optional)

```bash
# Using pipenv script
pipenv run build-cpp

# Or manually
python setup.py build_ext --inplace
```

### Build Standalone Ray-Casting Tool

```bash
# macOS/Linux
g++ -std=c++17 -O2 -fopenmp ray_voxel.cpp -o ray_voxel

# Linux (if OpenMP issues)
g++ -std=c++17 -O2 -fopenmp ray_voxel.cpp -o ray_voxel -lpthread

# Windows (MSVC)
cl /std:c++17 /O2 /openmp ray_voxel.cpp
```

---

## Verification

### Test Webcam Access

```bash
python webcam_recorder.py --list
```

**Expected output:**
```
Found N camera(s):
  Camera 0: 1920x1080
  Camera 1: 1280x720
```

### Test Calibration Tool

```bash
python webcam_calibration.py --example-sky
```

**Expected output:**
```
Generating example sky observation setup...
Sky observation metadata created: example_sky_metadata.json
```

### Test 3D Visualization

```bash
python -c "import pyvista; print('PyVista version:', pyvista.__version__)"
```

### Test OpenCV

```bash
python -c "import cv2; print('OpenCV version:', cv2.__version__)"
```

---

## Troubleshooting

### Camera Not Detected

**macOS:**
```bash
# Grant camera permissions
# System Preferences → Security & Privacy → Camera → Terminal (check)

# Test with system camera
system_profiler SPCameraDataType
```

**Linux:**
```bash
# Check video devices
ls -l /dev/video*

# Add user to video group
sudo usermod -a -G video $USER
# Log out and back in
```

**Windows:**
```bash
# Check Device Manager for camera
# Privacy Settings → Camera → Allow apps to access camera
```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'cv2'`

**Solution:**
```bash
# Ensure virtual environment is activated
pipenv shell

# Reinstall opencv
pip install opencv-python
```

### C++ Compilation Errors

**macOS - Missing Xcode:**
```bash
xcode-select --install
```

**Linux - Missing OpenMP:**
```bash
sudo apt-get install libomp-dev
```

**Windows - Missing Visual Studio:**
- Install Visual Studio Build Tools
- Select "Desktop development with C++" workload

### PyVista Display Issues

**Linux - Missing GL libraries:**
```bash
sudo apt-get install libgl1-mesa-glx libxrender1 libsm6
```

**Headless server:**
```python
# Use offscreen rendering
import pyvista as pv
pv.start_xvfb()
```

### Astropy/FITS Issues

**Problem:** FITS file reading errors

**Solution:**
```bash
# Update astropy
pip install --upgrade astropy
```

---

## Optional Dependencies

### For Blender Integration

Blender comes with its own Python environment:

```bash
# Install in Blender's Python (adjust path for your Blender version)
/Applications/Blender.app/Contents/Resources/3.6/python/bin/python3.10 -m pip install numpy
```

### For GPU Acceleration (Optional)

If you have NVIDIA GPU and want GPU-accelerated ray-casting:

```bash
# Install CUDA Toolkit (check PyTorch compatibility)
# https://developer.nvidia.com/cuda-downloads

# For PyVista GPU rendering
pip install pyopenvdb
```

---

## Using pipenv Scripts

The Pipfile includes convenient scripts:

```bash
# Activate environment first
pipenv shell

# Record from webcam
pipenv run record

# Interactive calibration
pipenv run calibrate

# Generate example setups
pipenv run example-sky
pipenv run example-object

# Process video
pipenv run process-video

# Visualize voxels
pipenv run view-voxels

# Build C++ extension
pipenv run build-cpp
```

---

## Development Setup

For contributing or development:

```bash
# Install dev dependencies
pipenv install --dev

# Install in editable mode
pip install -e .

# Run tests (if available)
pytest
```

---

## Environment Variables

Optional configuration:

```bash
# Set default output directory
export VOXEL_OUTPUT_DIR="/path/to/output"

# Set OpenMP thread count (for C++ processing)
export OMP_NUM_THREADS=4

# PyVista rendering backend
export PYVISTA_TRAME_SERVER_PROXY_PREFIX="/proxy/"
```

---

## Updating Dependencies

```bash
# Using pipenv
pipenv update

# Or manually
pip install --upgrade numpy opencv-python pyvista astropy matplotlib
```

---

## Uninstallation

```bash
# Remove virtual environment
pipenv --rm

# Or remove entire directory
rm -rf ~/.local/share/virtualenvs/Pixeltovoxelprojector-*
```

---

## Minimal Installation (Sky Observation Only)

If you only need webcam recording and sky observation (no Blender, no FITS):

```bash
pip install numpy opencv-python pyvista matplotlib
```

This installs only what's needed for:
- Webcam recording ([webcam_recorder.py](webcam_recorder.py))
- Camera calibration ([webcam_calibration.py](webcam_calibration.py))
- Voxel visualization ([voxelmotionviewer.py](voxelmotionviewer.py))

---

## Next Steps

After installation:

1. **Test webcam setup**: [WEBCAM_SETUP.md](WEBCAM_SETUP.md)
2. **Sky observation guide**: [SKY_OBSERVATION_GUIDE.md](SKY_OBSERVATION_GUIDE.md)
3. **Record test video**: `python webcam_recorder.py --output test.mp4 --duration 10`
4. **Create calibration**: `python webcam_calibration.py --interactive`

---

## Support

For issues:
- Check this guide's troubleshooting section
- Review documentation in [WEBCAM_SETUP.md](WEBCAM_SETUP.md)
- Verify Python version: `python --version` (3.8+ required)
- Check dependencies: `pip list`
