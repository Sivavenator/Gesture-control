import platform
import ctypes
import subprocess

KEYEVENTF_KEYUP = 0x0002

VK_VOLUME_MUTE  = 0xAD
VK_VOLUME_DOWN  = 0xAE
VK_VOLUME_UP    = 0xAF
VK_MEDIA_PLAY_PAUSE = 0xB3


def _press_key(vk):
    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


class TVController:
    def __init__(self, tv_ip=None):
        self._is_muted = False
        self._is_playing = True
        self._current_volume = 50
        print("Laptop audio controller ready (Windows media keys)")

    def set_volume(self, level: int):
        level = max(0, min(100, level))
        diff = level - self._current_volume

        # Each keypress = ~2% volume on Windows
        steps = abs(diff) // 2
        key = VK_VOLUME_UP if diff > 0 else VK_VOLUME_DOWN

        for _ in range(steps):
            _press_key(key)

        self._current_volume = level
        print(f"Volume: {level}%")

    def toggle_mute(self):
        self._is_muted = not self._is_muted
        _press_key(VK_VOLUME_MUTE)
        print(f"Muted: {self._is_muted}")
        return self._is_muted

    def toggle_play_pause(self):
        self._is_playing = not self._is_playing
        _press_key(VK_MEDIA_PLAY_PAUSE)
        print(f"{'Playing' if self._is_playing else 'Paused'}")
        return self._is_playing

    def disconnect(self):
        print("Done.")