"""
Webcam Recorder for Pixel-to-Voxel Projector
Records video from webcam(s) to be processed by PixelationDecensorer.py
"""

import cv2
import numpy as np
import argparse
from datetime import datetime
import os


def list_available_cameras(max_cameras=10):
    """Detect all available cameras on the system."""
    available_cameras = []

    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                height, width = frame.shape[:2]
                available_cameras.append({
                    'index': i,
                    'resolution': f"{width}x{height}"
                })
            cap.release()

    return available_cameras


def record_webcam(camera_index=0, output_file=None, fps=30, resolution=None,
                  show_preview=True, max_duration=None):
    """
    Record video from webcam.

    Args:
        camera_index: Camera device index (0 for default webcam)
        output_file: Output video filename (auto-generated if None)
        fps: Frames per second for recording
        resolution: Tuple (width, height) or None for camera default
        show_preview: Show live preview window
        max_duration: Maximum recording duration in seconds (None = unlimited)
    """

    # Initialize camera
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"Error: Could not open camera {camera_index}")
        return False

    # Set resolution if specified
    if resolution:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    # Get actual resolution
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Try to set the requested FPS
    cap.set(cv2.CAP_PROP_FPS, fps)

    # Generate output filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"webcam_recording_{timestamp}.mp4"

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Check if this is a single image capture (based on extension)
    is_image_capture = output_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))

    if is_image_capture:
        # Single image capture mode
        print(f"\n{'='*60}")
        print(f"Capturing single frame from camera {camera_index}")
        print(f"Resolution: {width}x{height}")
        print(f"Output: {output_file}")
        print(f"{'='*60}\n")

        # Capture a single frame
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(output_file, frame)
            print(f"Image captured successfully: {output_file}")
            cap.release()
            return True
        else:
            print("Error: Failed to capture frame")
            cap.release()
            return False

    # Video recording mode
    # Measure actual FPS by capturing a few test frames
    print("Detecting camera FPS...")
    test_start = cv2.getTickCount()
    test_frames = 0
    for _ in range(30):  # Capture 30 frames to measure FPS
        ret, _ = cap.read()
        if ret:
            test_frames += 1
    test_time = (cv2.getTickCount() - test_start) / cv2.getTickFrequency()

    if test_frames > 0 and test_time > 0:
        measured_fps = test_frames / test_time
        print(f"Camera actual FPS: {measured_fps:.2f}")
        fps = measured_fps

    # Initialize video writer with actual FPS
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    if not out.isOpened():
        print(f"Error: Could not create video file {output_file}")
        cap.release()
        return False

    print(f"\n{'='*60}")
    print(f"Recording from camera {camera_index}")
    print(f"Resolution: {width}x{height}")
    print(f"FPS: {fps:.2f}")
    print(f"Output: {output_file}")
    if max_duration:
        print(f"Max duration: {max_duration} seconds")
    print(f"{'='*60}")
    print("\nPress 'q' to stop recording")
    print("Press 's' to take a screenshot\n")

    frame_count = 0
    start_time = cv2.getTickCount()

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("Error: Failed to capture frame")
                break

            # Write frame to video file
            out.write(frame)
            frame_count += 1

            # Calculate elapsed time
            elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()

            # Add recording indicator to preview
            if show_preview:
                display_frame = frame.copy()

                # Recording indicator (red circle)
                cv2.circle(display_frame, (30, 30), 10, (0, 0, 255), -1)

                # Time and frame counter
                time_text = f"Time: {elapsed_time:.1f}s | Frames: {frame_count}"
                cv2.putText(display_frame, time_text, (60, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                cv2.imshow('Webcam Recording', display_frame)

            # Check for key press
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                print("\nRecording stopped by user")
                break
            elif key == ord('s'):
                screenshot_name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                cv2.imwrite(screenshot_name, frame)
                print(f"Screenshot saved: {screenshot_name}")

            # Check max duration based on captured frames and target FPS
            # This ensures video duration matches requested duration
            if max_duration:
                target_frames = max_duration * fps
                if frame_count >= target_frames:
                    print(f"\nReached maximum duration ({max_duration}s, {frame_count} frames)")
                    break

    except KeyboardInterrupt:
        print("\nRecording interrupted by user")

    finally:
        # Clean up
        cap.release()
        out.release()
        cv2.destroyAllWindows()

        # Final statistics
        final_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        actual_fps = frame_count / final_time if final_time > 0 else 0

        print(f"\n{'='*60}")
        print(f"Recording completed!")
        print(f"Total frames: {frame_count}")
        print(f"Duration: {final_time:.2f} seconds")
        print(f"Average FPS: {actual_fps:.2f}")
        print(f"File saved: {output_file}")
        print(f"File size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
        print(f"{'='*60}\n")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Record video from webcam for Pixel-to-Voxel processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available cameras
  python webcam_recorder.py --list

  # Record from default webcam
  python webcam_recorder.py

  # Record from specific camera with custom settings
  python webcam_recorder.py --camera 1 --fps 60 --resolution 1920 1080

  # Record to specific file for 30 seconds
  python webcam_recorder.py --output targetvideo.mp4 --duration 30

  # Record without preview (headless)
  python webcam_recorder.py --no-preview --duration 60
        """
    )

    parser.add_argument('--list', action='store_true',
                       help='List available cameras and exit')
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera index (default: 0)')
    parser.add_argument('--output', type=str,
                       help='Output video filename (auto-generated if not specified)')
    parser.add_argument('--fps', type=int, default=30,
                       help='Frames per second (default: 30)')
    parser.add_argument('--resolution', type=int, nargs=2, metavar=('WIDTH', 'HEIGHT'),
                       help='Video resolution (e.g., 1920 1080)')
    parser.add_argument('--duration', type=int,
                       help='Maximum recording duration in seconds')
    parser.add_argument('--no-preview', action='store_true',
                       help='Disable preview window')

    args = parser.parse_args()

    # List cameras mode
    if args.list:
        print("\nScanning for available cameras...\n")
        cameras = list_available_cameras()

        if not cameras:
            print("No cameras found!")
            return

        print(f"Found {len(cameras)} camera(s):\n")
        for cam in cameras:
            print(f"  Camera {cam['index']}: {cam['resolution']}")
        print()
        return

    # Record mode
    resolution = tuple(args.resolution) if args.resolution else None

    record_webcam(
        camera_index=args.camera,
        output_file=args.output,
        fps=args.fps,
        resolution=resolution,
        show_preview=not args.no_preview,
        max_duration=args.duration
    )


if __name__ == "__main__":
    main()
