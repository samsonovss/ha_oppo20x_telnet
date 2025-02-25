"""Oppo Telnet Media Player."""
import asyncio
import socket
from homeassistant.components.media_player import MediaPlayerEntity, MediaPlayerDeviceClass
from homeassistant.components.media_player.const import (
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.const import CONF_HOST
from homeassistant.helpers.entity import DeviceInfo
import logging

DOMAIN = "oppo_telnet"
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Oppo Telnet media player from a config entry."""
    host = config_entry.data[CONF_HOST]
    async_add_entities([OppoTelnetMediaPlayer(host)])

class OppoTelnetMediaPlayer(MediaPlayerEntity):
    """Representation of an Oppo Telnet media player."""

    def __init__(self, host):
        """Initialize the Oppo Telnet media player."""
        self._host = host
        self._port = 23
        self._state = MediaPlayerState.OFF
        self._volume = 0.0
        self._is_muted = False

    @property
    def unique_id(self):
        """Return a unique ID for the device."""
        return f"oppo_telnet_{self._host}"

    @property
    def name(self):
        """Return the name of the device."""
        return f"Oppo Telnet {self._host}"

    @property
    def state(self):
        """Return the current state of the device."""
        return self._state

    @property
    def volume_level(self):
        """Return the current volume level (0..1)."""
        return self._volume

    @property
    def is_volume_muted(self):
        """Return True if volume is muted."""
        return self._is_muted

    @property
    def device_class(self):
        """Return the device class."""
        return MediaPlayerDeviceClass.TV

    @property
    def supported_features(self):
        """Return the supported features."""
        return (
            MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.STOP
            | MediaPlayerEntityFeature.PAUSE
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.NEXT_TRACK
            | MediaPlayerEntityFeature.PREVIOUS_TRACK
        )

    @property
    def device_info(self):
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=self.name,
            manufacturer="Oppo",
            model="UDP-203",
        )

    async def _send_command(self, command, expect_response=False):
        """Send a command to the Oppo device via Telnet."""
        try:
            reader, writer = await asyncio.open_connection(self._host, self._port)
            writer.write(f"{command}\r".encode())
            await writer.drain()
            if expect_response:
                response = await reader.read(2048)
                writer.close()
                await writer.wait_closed()
                return response.decode().strip()
            writer.close()
            await writer.wait_closed()
            return True
        except Exception as e:
            _LOGGER.error(f"Failed to send command {command}: {e}")
            return False

    async def async_set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        new_volume = int(volume * 100)
        response = await self._send_command(f"#SVL {new_volume}", expect_response=True)
        if response and "@OK" in response:
            self._volume = volume
            self.async_write_ha_state()
        else:
            _LOGGER.warning(f"Failed to set volume to {new_volume}: {response}")
        # Запрос текущей громкости для синхронизации
        await self.async_update()

    async def async_media_play(self):
        """Play media."""
        if await self._send_command("#PLA"):
            self._state = MediaPlayerState.PLAYING
            self.async_write_ha_state()

    async def async_media_stop(self):
        """Stop media."""
        if await self._send_command("#STP"):
            self._state = MediaPlayerState.IDLE
            self.async_write_ha_state()

    async def async_media_pause(self):
        """Pause media."""
        if await self._send_command("#PAU"):
            self._state = MediaPlayerState.PAUSED
            self.async_write_ha_state()

    async def async_media_next_track(self):
        """Skip to next track."""
        await self._send_command("#NXT")

    async def async_media_previous_track(self):
        """Skip to previous track."""
        await self._send_command("#PRE")

    async def async_turn_on(self):
        """Turn the media player on."""
        if await self._send_command("#PON"):
            self._state = MediaPlayerState.IDLE
            self.async_write_ha_state()

    async def async_turn_off(self):
        """Turn the media player off."""
        if await self._send_command("#POF"):
            self._state = MediaPlayerState.OFF
            self.async_write_ha_state()

    async def async_mute_volume(self, mute):
        """Mute or unmute the volume."""
        if await self._send_command("#MUT"):
            self._is_muted = mute
            self.async_write_ha_state()

    async def async_update(self):
        """Fetch the current state from the device."""
        # Проверка питания
        power_status = await self._send_command("#QPW", expect_response=True)
        if power_status:
            if "@OK ON" in power_status:
                self._state = MediaPlayerState.IDLE if self._state == MediaPlayerState.OFF else self._state
            elif "@OK OFF" in power_status:
                self._state = MediaPlayerState.OFF

        # Проверка громкости
        volume_status = await self._send_command("#VOL", expect_response=True)
        if volume_status and "@OK" in volume_status:
            try:
                volume = int(volume_status.split()[-1]) / 100.0
                self._volume = volume
            except (ValueError, IndexError):
                _LOGGER.warning(f"Failed to parse volume: {volume_status}")

        # Проверка состояния воспроизведения
        play_status = await self._send_command("#QPL", expect_response=True)
        if play_status and "@OK" in play_status:
            status = play_status.split()[-1].lower()
            if "play" in status:
                self._state = MediaPlayerState.PLAYING
            elif "pause" in status:
                self._state = MediaPlayerState.PAUSED
            elif "stop" in status:
                self._state = MediaPlayerState.IDLE

        self.async_write_ha_state()
