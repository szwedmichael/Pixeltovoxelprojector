"""
Webcam Camera Calibration and Position Tracker
Generates metadata.json with camera positions for voxel reconstruction pipeline
"""

import cv2
import numpy as np
import json
import argparse
from pathlib import Path


class CameraCalibrator:
    """
    Manages camera position, orientation, and intrinsics for 3D reconstruction.

    The voxel reconstruction system needs:
    - camera_position: [x, y, z] in world coordinates
    - yaw, pitch, roll: rotation angles in degrees
    - fov_degrees: horizontal field of view
    """

    def __init__(self):
        self.metadata = []

    def add_manual_camera(self, camera_index, frame_index,
                         position, yaw, pitch, roll, fov_degrees,
                         image_file, object_location=None):
        """
        Manually specify camera parameters.

        Args:
            camera_index: Unique camera ID
            frame_index: Frame/time index
            position: [x, y, z] camera position in world coordinates (e.g., [0, 0, 100])
            yaw: Rotation around Z-axis in degrees (heading)
            pitch: Rotation around Y-axis in degrees (elevation)
            roll: Rotation around X-axis in degrees (bank)
            fov_degrees: Horizontal field of view in degrees (typically 50-70)
            image_file: Path to the image file
            object_location: Optional [x, y, z] of object being tracked
        """
        entry = {
            "camera_index": camera_index,
            "frame_index": frame_index,
            "camera_position": list(position),
            "yaw": float(yaw),
            "pitch": float(pitch),
            "roll": float(roll),
            "fov_degrees": float(fov_degrees),
            "image_file": str(image_file),
            "rendered": True,  # Mark as already captured
            "object_name": "tracked_object"
        }

        if object_location is not None:
            entry["object_location"] = list(object_location)

        self.metadata.append(entry)

    def add_camera_from_measurement(self, camera_index, frame_index,
                                    distance_to_object, angle_horizontal,
                                    angle_vertical, height_above_ground,
                                    fov_degrees, image_file,
                                    object_location=(0, 0, 0)):
        """
        Add camera using physical measurements (easier for manual setup).

        Args:
            camera_index: Unique camera ID
            frame_index: Frame/time index
            distance_to_object: Distance from camera to object (cm or meters)
            angle_horizontal: Horizontal angle from reference direction (degrees, 0-360)
            angle_vertical: Vertical angle from horizontal (degrees, -90 to 90)
            height_above_ground: Camera height (same units as distance)
            fov_degrees: Camera field of view
            image_file: Path to image file
            object_location: [x, y, z] of the object being observed
        """
        # Convert measurements to 3D position
        obj_x, obj_y, obj_z = object_location

        # Calculate camera position using spherical coordinates
        angle_h_rad = np.radians(angle_horizontal)
        angle_v_rad = np.radians(angle_vertical)

        # Camera position relative to object
        cam_x = obj_x + distance_to_object * np.cos(angle_v_rad) * np.cos(angle_h_rad)
        cam_y = obj_y + distance_to_object * np.cos(angle_v_rad) * np.sin(angle_h_rad)
        cam_z = obj_z + height_above_ground

        # Calculate orientation (camera looking at object)
        # Yaw: horizontal angle pointing toward object
        yaw = (angle_horizontal + 180) % 360  # Flip direction (camera points opposite)

        # Pitch: vertical angle
        pitch = -angle_vertical  # Negative because looking down

        # Roll: typically 0 for upright cameras
        roll = 0.0

        self.add_manual_camera(
            camera_index, frame_index,
            position=[cam_x, cam_y, cam_z],
            yaw=yaw, pitch=pitch, roll=roll,
            fov_degrees=fov_degrees,
            image_file=image_file,
            object_location=object_location
        )

    def add_sky_camera(self, camera_index, frame_index,
                      position, azimuth, altitude, roll,
                      fov_degrees, image_file, reference_point=None):
        """
        Add camera for sky observation (astronomy, satellite tracking, meteor detection).

        This mode doesn't require a central object - cameras point at sky coordinates.
        Perfect for detecting moving objects (satellites, aircraft, meteors) across
        overlapping fields of view.

        Args:
            camera_index: Unique camera ID
            frame_index: Frame/time index
            position: [x, y, z] camera position (e.g., [0, 0, 0] for first camera)
            azimuth: Compass direction camera points (0=North, 90=East, 180=South, 270=West)
            altitude: Elevation angle above horizon (0=horizon, 90=zenith/straight up)
            roll: Camera rotation around viewing axis (usually 0)
            fov_degrees: Horizontal field of view
            image_file: Path to image file
            reference_point: Optional [x, y, z] far point in sky for voxel grid center
        """
        # For sky cameras, pitch is the altitude angle
        pitch = altitude

        # Yaw is the azimuth
        yaw = azimuth

        # If no reference point specified, create one far away in the direction of view
        if reference_point is None:
            # Create a point 10km away in the direction the camera is pointing
            distance = 10000  # meters
            az_rad = np.radians(azimuth)
            alt_rad = np.radians(altitude)

            ref_x = position[0] + distance * np.cos(alt_rad) * np.sin(az_rad)
            ref_y = position[1] + distance * np.cos(alt_rad) * np.cos(az_rad)
            ref_z = position[2] + distance * np.sin(alt_rad)
            reference_point = [ref_x, ref_y, ref_z]

        self.add_manual_camera(
            camera_index, frame_index,
            position=position,
            yaw=yaw, pitch=pitch, roll=roll,
            fov_degrees=fov_degrees,
            image_file=image_file,
            object_location=reference_point
        )

    def estimate_fov_from_calibration(self, image_path, checkerboard_size=(9, 6),
                                      square_size_mm=25.0):
        """
        Estimate camera FOV using a checkerboard calibration pattern.

        Args:
            image_path: Path to image containing checkerboard
            checkerboard_size: (cols, rows) inner corners
            square_size_mm: Physical size of checkerboard squares

        Returns:
            fov_degrees: Estimated horizontal field of view
        """
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)

        if not ret:
            raise ValueError("Checkerboard pattern not found in image")

        # Prepare object points
        objp = np.zeros((checkerboard_size[0] * checkerboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:checkerboard_size[0],
                               0:checkerboard_size[1]].T.reshape(-1, 2)
        objp *= square_size_mm

        # Calibrate camera
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            [objp], [corners], gray.shape[::-1], None, None
        )

        # Extract focal length and calculate FOV
        fx = camera_matrix[0, 0]
        width = img.shape[1]
        fov_rad = 2 * np.arctan(width / (2 * fx))
        fov_degrees = np.degrees(fov_rad)

        print(f"Estimated FOV: {fov_degrees:.2f} degrees")
        print(f"Focal length: {fx:.2f} pixels")
        print(f"Camera matrix:\n{camera_matrix}")

        return fov_degrees

    def save_metadata(self, output_path="metadata.json"):
        """Save camera metadata to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        print(f"\nMetadata saved to {output_path}")
        print(f"Total cameras: {len(set(m['camera_index'] for m in self.metadata))}")
        print(f"Total frames: {len(self.metadata)}")

    def load_metadata(self, input_path="metadata.json"):
        """Load existing metadata."""
        with open(input_path, 'r') as f:
            self.metadata = json.load(f)
        print(f"Loaded {len(self.metadata)} entries from {input_path}")


def interactive_camera_setup():
    """Interactive CLI for setting up camera positions."""
    print("\n" + "="*70)
    print("Interactive Camera Position Setup")
    print("="*70)

    calibrator = CameraCalibrator()

    print("\nChoose setup mode:")
    print("1. Object tracking (cameras looking at a central object)")
    print("2. Sky observation (cameras pointing at overlapping sky regions)")

    mode = input("\nEnter mode (1 or 2): ").strip()

    if mode == "2":
        setup_sky_observation(calibrator)
    else:
        print("\nChoose coordinate system:")
        print("1. Manual XYZ coordinates (if you know exact positions)")
        print("2. Physical measurements (distance, angles, height)")

        choice = input("\nEnter choice (1 or 2): ").strip()

        if choice == "1":
            setup_manual_coordinates(calibrator)
        elif choice == "2":
            setup_physical_measurements(calibrator)
        else:
            print("Invalid choice")
            return

    # Ask about saving
    output_path = input("\nSave metadata as (default: metadata.json): ").strip()
    if not output_path:
        output_path = "metadata.json"

    calibrator.save_metadata(output_path)
    print_usage_instructions(output_path)


def setup_manual_coordinates(calibrator):
    """Setup using direct XYZ coordinates."""
    print("\n" + "-"*70)
    print("Manual XYZ Coordinate Entry")
    print("-"*70)
    print("Enter camera positions in 3D space (e.g., from a measured grid)")
    print()

    camera_idx = 0

    while True:
        print(f"\n--- Camera {camera_idx} ---")

        # Position
        pos_input = input("Camera position [x y z] (or 'done'): ").strip()
        if pos_input.lower() == 'done':
            break

        try:
            position = [float(x) for x in pos_input.split()]
            if len(position) != 3:
                print("Error: Need 3 values for x, y, z")
                continue
        except ValueError:
            print("Error: Invalid numbers")
            continue

        # Orientation
        yaw = float(input("Yaw angle (degrees, 0-360): "))
        pitch = float(input("Pitch angle (degrees, -90 to 90): "))
        roll = float(input("Roll angle (degrees, usually 0): ") or "0")

        # FOV
        fov = float(input("Field of view (degrees, typical 50-70): ") or "60")

        # Image file
        image_file = input("Image filename: ").strip()

        # Object location
        obj_input = input("Object location [x y z] (optional, press Enter to skip): ").strip()
        object_location = None
        if obj_input:
            object_location = [float(x) for x in obj_input.split()]

        calibrator.add_manual_camera(
            camera_index=camera_idx,
            frame_index=0,
            position=position,
            yaw=yaw, pitch=pitch, roll=roll,
            fov_degrees=fov,
            image_file=image_file,
            object_location=object_location
        )

        print(f"✓ Camera {camera_idx} added")
        camera_idx += 1


def setup_physical_measurements(calibrator):
    """Setup using physical measurements."""
    print("\n" + "-"*70)
    print("Physical Measurement Entry")
    print("-"*70)
    print("Measure distances and angles from your camera setup")
    print()

    # Get object location
    print("First, define the object/scene center:")
    obj_input = input("Object location [x y z] (default: 0 0 0): ").strip()
    if obj_input:
        object_location = [float(x) for x in obj_input.split()]
    else:
        object_location = [0, 0, 0]

    print(f"\nObject at: {object_location}")
    print("\nNow add cameras observing this object:")

    camera_idx = 0

    while True:
        print(f"\n--- Camera {camera_idx} ---")

        cont = input("Add camera? (y/n): ").strip().lower()
        if cont != 'y':
            break

        # Measurements
        distance = float(input("Distance to object (cm): "))
        angle_h = float(input("Horizontal angle from North/reference (0-360 deg): "))
        angle_v = float(input("Vertical angle from horizontal (-90=down, 0=level, 90=up): "))
        height = float(input("Camera height above ground (cm): "))
        fov = float(input("Field of view (degrees, typical 50-70): ") or "60")

        # Image file
        image_file = input("Image filename: ").strip()

        calibrator.add_camera_from_measurement(
            camera_index=camera_idx,
            frame_index=0,
            distance_to_object=distance,
            angle_horizontal=angle_h,
            angle_vertical=angle_v,
            height_above_ground=height,
            fov_degrees=fov,
            image_file=image_file,
            object_location=object_location
        )

        # Show calculated position
        last_entry = calibrator.metadata[-1]
        print(f"\n✓ Camera {camera_idx} added")
        print(f"  Calculated position: {last_entry['camera_position']}")
        print(f"  Orientation: yaw={last_entry['yaw']:.1f}°, "
              f"pitch={last_entry['pitch']:.1f}°, roll={last_entry['roll']:.1f}°")

        camera_idx += 1


def setup_sky_observation(calibrator):
    """Setup for sky observation (satellites, meteors, aircraft)."""
    print("\n" + "-"*70)
    print("Sky Observation Setup")
    print("-"*70)
    print("For detecting moving objects in the sky (satellites, meteors, aircraft)")
    print("Cameras point at overlapping regions of sky - no central object needed")
    print()

    camera_idx = 0

    while True:
        print(f"\n--- Camera {camera_idx} ---")

        cont = input("Add camera? (y/n): ").strip().lower()
        if cont != 'y':
            break

        # Camera position (usually on ground, spread out for triangulation)
        print("\nCamera position (any consistent units - meters, feet, etc.):")
        pos_input = input("Position [x y z] (e.g., '0 0 0' for first camera): ").strip()
        try:
            position = [float(x) for x in pos_input.split()]
            if len(position) != 3:
                print("Error: Need 3 values for x, y, z")
                continue
        except ValueError:
            print("Error: Invalid numbers")
            continue

        # Sky pointing direction
        print("\nSky pointing direction:")
        print("  Azimuth: Compass direction (0=North, 90=East, 180=South, 270=West)")
        print("  Altitude: Angle above horizon (0=horizon, 45=halfway up, 90=straight up)")

        azimuth = float(input("Azimuth (0-360 degrees): "))
        altitude = float(input("Altitude (0-90 degrees): "))
        roll = float(input("Roll/tilt (usually 0): ") or "0")

        # FOV
        fov = float(input("Field of view (degrees, typical 50-70): ") or "60")

        # Image file
        image_file = input("Image filename: ").strip()

        calibrator.add_sky_camera(
            camera_index=camera_idx,
            frame_index=0,
            position=position,
            azimuth=azimuth,
            altitude=altitude,
            roll=roll,
            fov_degrees=fov,
            image_file=image_file
        )

        # Show result
        last_entry = calibrator.metadata[-1]
        print(f"\n✓ Camera {camera_idx} added")
        print(f"  Position: {last_entry['camera_position']}")
        print(f"  Pointing: Azimuth {azimuth}°, Altitude {altitude}°")
        print(f"  Reference point in sky: {last_entry['object_location']}")

        camera_idx += 1

    if camera_idx < 2:
        print("\nWarning: You need at least 2 cameras for 3D reconstruction!")
        print("3+ cameras recommended for better coverage and accuracy.")


def print_usage_instructions(metadata_path):
    """Print next steps for the user."""
    print("\n" + "="*70)
    print("Next Steps")
    print("="*70)
    print(f"\n1. Your camera metadata is saved in: {metadata_path}")
    print("\n2. To build the voxel grid, compile and run:")
    print("   g++ -std=c++17 -O2 ray_voxel.cpp -o ray_voxel")
    print(f"   ./ray_voxel {metadata_path} <image_directory> voxel_grid.bin")
    print("\n3. To visualize the voxel grid:")
    print("   python voxelmotionviewer.py")
    print("\n4. Make sure all image files referenced in the metadata exist!")
    print("="*70 + "\n")


def example_simple_setup():
    """Generate example metadata for a simple 3-camera setup."""
    print("\nGenerating example 3-camera setup...")

    calibrator = CameraCalibrator()

    # Object at origin
    object_location = [0, 0, 0]

    # Three cameras around the object at 120-degree intervals
    # All at distance=500cm, height=100cm, looking slightly down
    for i, angle in enumerate([0, 120, 240]):
        calibrator.add_camera_from_measurement(
            camera_index=i,
            frame_index=0,
            distance_to_object=500,
            angle_horizontal=angle,
            angle_vertical=-15,  # Looking down 15 degrees
            height_above_ground=100,
            fov_degrees=60,
            image_file=f"camera_{i}_frame_000.png",
            object_location=object_location
        )

    calibrator.save_metadata("example_metadata.json")
    print("\nExample metadata created: example_metadata.json")
    print("Camera positions:")
    for entry in calibrator.metadata:
        print(f"  Camera {entry['camera_index']}: {entry['camera_position']}")


def example_sky_observation_setup():
    """Generate example metadata for sky observation (satellite/meteor detection)."""
    print("\nGenerating example sky observation setup...")
    print("Use case: Detecting satellites, meteors, or aircraft with overlapping sky coverage")

    calibrator = CameraCalibrator()

    # All cameras at ground level, spread apart to triangulate sky objects
    # Camera positions in meters (you can use any consistent unit)
    camera_positions = [
        [0, 0, 0],        # Camera 0 at origin
        [100, 0, 0],      # Camera 1: 100m East
        [50, 86.6, 0],    # Camera 2: 100m at 60° (forms triangle)
    ]

    # Each camera points toward a shared overlapping region of sky
    # Pointing roughly North-Northeast at 45° elevation
    sky_directions = [
        {"azimuth": 30, "altitude": 45},   # Camera 0: NNE, 45° up
        {"azimuth": 340, "altitude": 45},  # Camera 1: NNW, 45° up (overlaps with 0)
        {"azimuth": 0, "altitude": 50},    # Camera 2: N, 50° up (overlaps both)
    ]

    for i, (pos, direction) in enumerate(zip(camera_positions, sky_directions)):
        calibrator.add_sky_camera(
            camera_index=i,
            frame_index=0,
            position=pos,
            azimuth=direction["azimuth"],
            altitude=direction["altitude"],
            roll=0,
            fov_degrees=60,
            image_file=f"sky_camera_{i}_frame_000.png"
        )

    calibrator.save_metadata("example_sky_metadata.json")
    print("\nSky observation metadata created: example_sky_metadata.json")
    print("\nCamera setup:")
    for i, entry in enumerate(calibrator.metadata):
        print(f"  Camera {i}:")
        print(f"    Position: {entry['camera_position']}")
        print(f"    Pointing: Azimuth {entry['yaw']}°, Altitude {entry['pitch']}°")
        print(f"    FOV: {entry['fov_degrees']}°")
    print("\nThis setup creates overlapping fields of view in the northern sky.")
    print("Objects moving through this region will be visible from multiple cameras.")


def main():
    parser = argparse.ArgumentParser(
        description='Camera calibration and position tracking for voxel reconstruction',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive setup
  python webcam_calibration.py --interactive

  # Generate example 3-camera setup (object tracking)
  python webcam_calibration.py --example

  # Generate example sky observation setup (satellite/meteor detection)
  python webcam_calibration.py --example-sky

  # Estimate FOV from checkerboard
  python webcam_calibration.py --estimate-fov checkerboard.jpg --checkerboard 9 6

  # Manual entry (object tracking mode)
  python webcam_calibration.py --add-camera \\
      --position 0 500 100 \\
      --orientation 180 -15 0 \\
      --fov 60 \\
      --image camera0.png

  # Manual entry (sky observation mode)
  python webcam_calibration.py --add-sky-camera \\
      --position 0 0 0 \\
      --azimuth 30 \\
      --altitude 45 \\
      --fov 60 \\
      --image sky_north.png
        """
    )

    parser.add_argument('--interactive', action='store_true',
                       help='Interactive camera setup')
    parser.add_argument('--example', action='store_true',
                       help='Generate example 3-camera metadata (object tracking)')
    parser.add_argument('--example-sky', action='store_true',
                       help='Generate example sky observation setup (satellite/meteor detection)')
    parser.add_argument('--estimate-fov', type=str, metavar='IMAGE',
                       help='Estimate FOV from checkerboard calibration image')
    parser.add_argument('--checkerboard', type=int, nargs=2,
                       metavar=('COLS', 'ROWS'), default=[9, 6],
                       help='Checkerboard inner corners (default: 9 6)')
    parser.add_argument('--square-size', type=float, default=25.0,
                       help='Checkerboard square size in mm (default: 25.0)')

    # Manual entry options
    parser.add_argument('--add-camera', action='store_true',
                       help='Add a single camera manually (object tracking mode)')
    parser.add_argument('--add-sky-camera', action='store_true',
                       help='Add a single sky observation camera')
    parser.add_argument('--position', type=float, nargs=3, metavar=('X', 'Y', 'Z'),
                       help='Camera position')
    parser.add_argument('--orientation', type=float, nargs=3,
                       metavar=('YAW', 'PITCH', 'ROLL'),
                       help='Camera orientation in degrees (for --add-camera)')
    parser.add_argument('--azimuth', type=float,
                       help='Azimuth/compass direction in degrees (for --add-sky-camera)')
    parser.add_argument('--altitude', type=float,
                       help='Altitude/elevation angle in degrees (for --add-sky-camera)')
    parser.add_argument('--fov', type=float, help='Field of view in degrees')
    parser.add_argument('--image', type=str, help='Image filename')
    parser.add_argument('--output', type=str, default='metadata.json',
                       help='Output metadata file (default: metadata.json)')

    args = parser.parse_args()

    if args.interactive:
        interactive_camera_setup()

    elif args.example:
        example_simple_setup()

    elif args.example_sky:
        example_sky_observation_setup()

    elif args.estimate_fov:
        calibrator = CameraCalibrator()
        fov = calibrator.estimate_fov_from_calibration(
            args.estimate_fov,
            tuple(args.checkerboard),
            args.square_size
        )
        print(f"\nUse --fov {fov:.1f} when adding cameras")

    elif args.add_camera:
        if not all([args.position, args.orientation, args.fov, args.image]):
            parser.error("--add-camera requires --position, --orientation, --fov, and --image")

        calibrator = CameraCalibrator()
        if Path(args.output).exists():
            calibrator.load_metadata(args.output)

        calibrator.add_manual_camera(
            camera_index=len(calibrator.metadata),
            frame_index=0,
            position=args.position,
            yaw=args.orientation[0],
            pitch=args.orientation[1],
            roll=args.orientation[2],
            fov_degrees=args.fov,
            image_file=args.image
        )

        calibrator.save_metadata(args.output)

    elif args.add_sky_camera:
        if not all([args.position, args.azimuth is not None, args.altitude is not None, args.fov, args.image]):
            parser.error("--add-sky-camera requires --position, --azimuth, --altitude, --fov, and --image")

        calibrator = CameraCalibrator()
        if Path(args.output).exists():
            calibrator.load_metadata(args.output)

        calibrator.add_sky_camera(
            camera_index=len(calibrator.metadata),
            frame_index=0,
            position=args.position,
            azimuth=args.azimuth,
            altitude=args.altitude,
            roll=0,
            fov_degrees=args.fov,
            image_file=args.image
        )

        calibrator.save_metadata(args.output)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
