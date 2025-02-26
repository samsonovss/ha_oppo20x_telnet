# Oppo UDP-20x Telnet

Custom Home Assistant integration for controlling Oppo UDP-20x series media players (e.g., UDP-203, UDP-205) via Telnet. Unlike the original UDP-based integration, this version uses Telnet protocol (port 23) for reliable command execution, eliminating the need for a web interface.

## Features
- **Power Control**: Turn the player on or off.
- **Volume Control**: Adjust volume (0-100), increase/decrease, mute/unmute. Volume displays both as a percentage (0.0-1.0) and in Oppo's native range (0-100).
- **Playback**: Play, stop, pause, skip to next or previous track.
- **Navigation**: Up, Down, Left, Right, Enter, and Home buttons via service calls.
- **Source Selection**: Switch between Disc, HDMI In, and ARC: HDMI Out directly from the media player card.
- **Status Polling**: Real-time updates for power, volume, mute, and playback status.

## Attributes
The integration provides the following extra state attributes for use in automations:
- `up`: "Move cursor up"
- `down`: "Move cursor down"
- `left`: "Move cursor left"
- `right`: "Move cursor right"
- `enter`: "Select/Enter"
- `home`: "Return to home screen"
- `volume_level_oppo`: Current volume level in Oppo's native range (0-100)

Additional attributes displayed in the card:
- `volume_level`: Volume level as a percentage (0.0-1.0) for Home Assistant compatibility.
- `is_volume_muted`: Indicates if mute is active (true/false).
- `source`: Current input source (e.g., "Disc", "HDMI In").

## Installation
1. **Via HACS**:
   - Add this repository as a custom repository in HACS.
   - Install "Oppo UDP-20x Telnet".
2. **Manual Installation**:
   - Copy the `oppo_telnet` folder to `/config/custom_components/`.
3. **Add Integration**:
   - Go to "Settings" → "Devices & Services" → "Add Integration".
   - Search for "Oppo UDP-20x Telnet" and configure with your device's IP (e.g., `192.168.1.124`).
4. **Restart Home Assistant**.

## Usage
- **Media Player Card**: Control power, volume, playback, and select input sources (Disc, HDMI In, ARC: HDMI Out) directly from the card.
- **Service Calls**: Use the `oppo_telnet.send_command` service to send navigation commands.
  - Example: Move cursor up:
    ```json
    {
      "entity_id": "media_player.oppo_telnet_192_168_1_124",
      "command": "up"
    }

## Supported commands: up, down, left, right, enter, home.
## 
