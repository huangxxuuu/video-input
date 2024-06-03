import cv2
import configparser
import pathlib

class YJ_Camera:
    def __init__(self, config_file="configs/camera.ini"):
        self.root_path = pathlib.Path(__file__).absolute().parent.parent
        self.config_file = self.root_path / config_file
        self.config = self.read_config()
        self.camera = None

    def __del__(self):
        if self.camera != None:
            self.camera.release()
            del self.camera
            self.camera = None
        cv2.destroyAllWindows()

    def read_config(self):
        config = configparser.ConfigParser()

        config.read(str(self.config_file))
        return {
            'camera_index': int(config['Camera']['camera_index']),
            'photo_save_path': self.root_path / config['Camera']['photo_save_path'],
            'video_save_path': self.root_path / config['Camera']['video_save_path'],
            'video_filename': config['Camera']['video_filename']
        }

    def get_photo_save_path(self):
        if self.ensure_directory_exists(self.config["photo_save_path"]):
            return self.config["photo_save_path"]
        return None
    
    def get_video_save_path(self):
        if self.ensure_directory_exists(self.config["video_save_path"]):
            return self.config["video_save_path"]
        return None

    def get_video_filename(self):
        return self.config["video_filename"]

    def get_camera_index(self):
        return self.config["camera_index"]

    def ensure_directory_exists(self, directory):
        path = pathlib.Path(directory)
        if not path.exists():
            path.mkdir(parents=True)
            return True
        if not path.is_dir():
            return False 
        return True

    def open_camera(self):
        self.camera = cv2.VideoCapture(self.get_camera_index())
        return self.camera

    def read_camera(self):
        if self.camera == None:
            return False, 0
        return self.camera.read()
    
    def is_opened(self):
        if self.camera == None or not self.camera.isOpened():
            return False
        return True

    def capture_photo(self, save_photo_name="photo.jpg"):
        if self.camera == None and not self.camera.isOpened():
            return None
        ret, frame = self.camera.read()
        if ret:
            photo_path = pathlib.Path(self.get_photo_save_path() / save_photo_name)
            cv2.imwrite(str(photo_path), frame)
            return photo_path
        return None

    def record_video(self):
        if self.camera == None and not self.camera.isOpened():
            return None
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(str(pathlib.Path(self.get_video_save_path() / self.get_video_filename()))
                              , fourcc, 20.0, (640,480))

        while self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                out.write(frame)
                cv2.imshow('Recording...', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break

        out.release()
        cv2.destroyAllWindows()

def main():
    camera = YJ_Camera()
    camera.open_camera()
    if not camera.is_opened():
        print("Error: Could not open camera.")
        return camera
    
    try:
        print("Press 'p' to take a photo, 'r' to start/stop recording, and 'q' to quit.")
        recording = False
        while True:
            ret, frame = camera.read_camera()
            if not ret:
                print("Failed to grab frame.")
                break

            cv2.imshow('Camera', frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('p'):
                photo_path = camera.capture_photo()
                if photo_path:
                    print(f"Photo saved at {photo_path}")

            elif key == ord('r'):
                if recording:
                    recording = False
                else:
                    recording = True
                    camera.record_video()

            elif key == ord('q'):
                break
    
    finally:
        del camera


if __name__ == "__main__" :
    main()