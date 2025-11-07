import time

import numpy as np


class BaseEmulatorController:
    """
    Base class for emulator controllers.
    This class is used to define the interface for all emulator controllers.
    """

    def __init__(self):
        raise NotImplementedError

    def __del__(self):
        # Avoid raising in destructor, subclasses may optionally implement cleanup.
        # Allow controllers to opt out by setting "_auto_stop_on_del = False".
        try:
            if getattr(self, "_auto_stop_on_del", True):  # type: ignore[attr-defined]
                self.stop()  # type: ignore[attr-defined]
        except Exception:
            pass

    def create(self):
        """
        This method is used to create the emulator.
        """
        raise NotImplementedError

    def configure(self):
        """
        This method is used to configure the emulator.
        """
        raise NotImplementedError

    def restart(self):
        """
        This method is used to restart the emulator.
        """
        raise NotImplementedError

    def start(self):
        """
        This method is used to start the emulator.
        """
        raise NotImplementedError

    def stop(self):
        """
        This method is used to stop the emulator.
        """
        raise NotImplementedError

    def click(self, x_coord: int, y_coord: int, clicks: int, interval: float):
        """
        This method is used to click on the emulator screen.
        """
        raise NotImplementedError

    def swipe(
        self,
        x_coord1: int,
        y_coord1: int,
        x_coord2: int,
        y_coord2: int,
    ):
        """
        This method is used to swipe on the emulator screen.
        """
        raise NotImplementedError

    def screenshot(self) -> np.ndarray:
        """
        This method is used to take a screenshot of the emulator screen.
        """
        raise NotImplementedError

    def install_apk(self, apk_path: str):
        """
        This method is used to install an APK on the emulator.
        """
        raise NotImplementedError

    def start_app(self, package_name: str):
        """
        This method is used to start an app on the emulator.
        """
        raise NotImplementedError

    def _is_package_installed(self, package_name: str) -> bool:
        """
        Check if a package is installed on the emulator.
        Subclasses must implement this method.

        Args:
            package_name: The package name to check (e.g., "com.supercell.clashroyale")

        Returns:
            True if the package is installed, False otherwise
        """
        raise NotImplementedError

    def _wait_for_clash_installation(self, package_name: str):
        """Wait for user to install Clash Royale using the logger action system"""
        self.current_package_name = package_name  # Store for retry logic
        self.logger.show_temporary_action(  # type: ignore[attr-defined]
            message=f"{package_name} not installed - please install it and complete tutorial",
            action_text="Retry",
            callback=self._retry_installation_check,
        )

        self.logger.log(f"[!] {package_name} not installed.")  # type: ignore[attr-defined]
        self.logger.log("Please install it in the emulator, complete tutorial, then click Retry in the GUI")  # type: ignore[attr-defined]

        # Wait for the callback to be triggered
        self.installation_waiting = True  # type: ignore[attr-defined]
        while self.installation_waiting:  # type: ignore[attr-defined]
            time.sleep(0.5)

        self.logger.log("[+] Installation confirmed, continuing...")  # type: ignore[attr-defined]
        return True

    def _retry_installation_check(self):
        """Callback method triggered when user clicks Retry button"""
        self.logger.change_status("Checking for Clash Royale installation...")  # type: ignore[attr-defined]

        # Check if app is now installed
        package_name = getattr(self, "current_package_name", "com.supercell.clashroyale")

        if self._is_package_installed(package_name):
            # Installation successful!
            self.installation_waiting = False  # type: ignore[attr-defined]
            self.logger.change_status("Installation complete - continuing...")  # type: ignore[attr-defined]
        else:
            # Still not installed, show the retry button again
            self.logger.show_temporary_action(  # type: ignore[attr-defined]
                message=f"{package_name} still not found - please install it and complete tutorial",
                action_text="Retry",
                callback=self._retry_installation_check,
            )
            self.logger.log(f"[!] {package_name} still not installed. Please try again.")  # type: ignore[attr-defined]
