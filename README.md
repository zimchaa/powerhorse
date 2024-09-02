# powerhorse
New Bright Power Horse + Robot Arm Thingabob

## Power Horse Control API
This system will control the power horse via a REST API. 

### Prerequisites
- Python 3.9+
- FastAPI
- Uvicorn

### Installation
1. Clone the repository
2. Install the dependencies

```bash
pip install fastapi
```

### Running the API
dev mode:
```bash
fastapi dev powerhorse_control_api.py
```

production mode:
```bash
fastapi run powerhorse_control_api.py
```


The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

### Root
- `GET /`
    - Returns a welcome message.

### Tracks
- `GET /powerhorse/tracks`
    - Returns the current throttle and differential values of the tracks.
- `PUT /powerhorse/tracks/{throttle}/{differential}`
    - Sets the throttle and differential values of the tracks.
- `PUT /powerhorse/tracks/throttle/{throttle}`
    - Sets the throttle value of the tracks.
- `PUT /powerhorse/tracks/differential/{differential}`
    - Sets the differential value of the tracks.
- `PUT /powerhorse/tracks/stop`
    - Stops the tracks by setting throttle and differential to 0.

### Arm
- `GET /powerhorse/arm`
    - Returns the current power values of all arm joints.
- `GET /powerhorse/arm/{joint}`
    - Returns the current power value of a specific arm joint.
- `PUT /powerhorse/arm/{joint}/{power}`
    - Sets the power value of a specific arm joint.
- `PUT /powerhorse/arm/stop`
    - Stops all arm joints by setting their power to 0.
- `PUT /powerhorse/arm/stop/{joint}`
    - Stops a specific arm joint by setting its power to 0.

### Light
- `GET /powerhorse/light`
    - Returns the current state of the light (on/off).
- `PUT /powerhorse/light/on`
    - Turns the light on.
- `PUT /powerhorse/light/off`
    - Turns the light off.
- `PUT /powerhorse/light/toggle`
    - Toggles the state of the light.

### Camera
- `GET /powerhorse/camera`
    - Returns the current angle of the camera.
- `PUT /powerhorse/camera/rotate/{angle}`
    - Rotates the camera to a specified angle.
- `PUT /powerhorse/camera/stop`
    - Stops the camera by setting its angle to 0.
- `PUT /powerhorse/camera/home`
    - Resets the camera to its home position (angle 0).

### Emergency Stop
- `PUT /powerhorse/stop`
    - Stops all components (tracks, arm, light, camera) immediately.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For any questions or suggestions, please contact [yourname@yourdomain.com](mailto:yourname@yourdomain.com).