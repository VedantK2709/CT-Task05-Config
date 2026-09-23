import json
import math
from dataclasses import dataclass, asdict, field
from typing import Optional, Tuple

import numpy as np
import matplotlib.pyplot as plt


@dataclass
class CTConfiguration:
    """
    CT System Configuration

    This class stores the CT scanner parameters and calculates
    derived acquisition parameters required by other modules.
    """

    # ---------------------------------------------------------
    # BASIC SCAN CONFIGURATION
    # ---------------------------------------------------------
    scan_geometry: str = "helical"

    # ---------------------------------------------------------
    # SOURCE / ACQUISITION PARAMETERS
    # ---------------------------------------------------------
    kvp: float = 120.0
    tube_current_ma: float = 200.0

    ma_min: float = 60.0
    ma_max: float = 660.0

    exposure_time_s: float = 1.0
    total_mas: float = 200.0

    # ---------------------------------------------------------
    # CT GEOMETRY
    # ---------------------------------------------------------
    sid_mm: float = 541.0
    sdd_mm: float = 949.0

    bore_diameter_mm: float = 820.0
    display_fov_mm: float = 500.0

    # ---------------------------------------------------------
    # ROTATION PARAMETERS
    # ---------------------------------------------------------
    rotation_time_s: float = 0.28
    rotation_angle_deg: float = 360.0

    num_views_per_rotation: int = 984

    # ---------------------------------------------------------
    # HELICAL PARAMETERS
    # ---------------------------------------------------------
    pitch: float = 0.516
    collimation_mm: float = 40.0

    scan_range_mm: float = 350.0

    # ---------------------------------------------------------
    # TCM
    # ---------------------------------------------------------
    tcm_enabled: bool = True
    tcm_modulation_depth: float = 0.25
    tcm_phase_deg: float = 0.0

    # ---------------------------------------------------------
    # 3D VOLUME INFORMATION
    # ---------------------------------------------------------
    volume_shape: Optional[Tuple[int, int, int]] = None

    voxel_spacing_mm: Optional[Tuple[float, float, float]] = None

    # ---------------------------------------------------------
    # DERIVED PARAMETERS
    # ---------------------------------------------------------
    magnification: float = field(init=False, default=0.0)

    angle_increment_deg: float = field(init=False, default=0.0)

    table_feed_per_rotation_mm: float = field(
        init=False,
        default=0.0
    )

    table_speed_mm_s: float = field(
        init=False,
        default=0.0
    )

    total_scan_time_s: float = field(
        init=False,
        default=0.0
    )

    num_rotations: int = field(
        init=False,
        default=0
    )

    total_views: int = field(
        init=False,
        default=0
    )

    physical_volume_size_mm: Optional[Tuple[float, float, float]] = field(
        init=False,
        default=None
    )

    required_fov_mm: Optional[float] = field(
        init=False,
        default=None
    )

    tcm_profile_ma: Optional[np.ndarray] = field(
        init=False,
        default=None,
        repr=False
    )

    # ---------------------------------------------------------
    # INITIALIZATION
    # ---------------------------------------------------------

    def __post_init__(self):

        self.validate_parameters()

        self.calculate_all_derived_parameters()

        if self.tcm_enabled:
            self.generate_tcm_profile()

    # =========================================================
    # 1. VALIDATION
    # =========================================================

    def validate_parameters(self):
        """
        Validate the CT configuration parameters.
        """

        if self.scan_geometry.lower() not in ["axial", "helical"]:
            raise ValueError(
                "scan_geometry must be 'axial' or 'helical'"
            )

        if self.kvp <= 0:
            raise ValueError("kVp must be greater than zero.")

        if self.tube_current_ma <= 0:
            raise ValueError(
                "Tube current must be greater than zero."
            )

        if self.ma_min <= 0:
            raise ValueError("Minimum mA must be positive.")

        if self.ma_max <= self.ma_min:
            raise ValueError(
                "ma_max must be greater than ma_min."
            )

        if self.sid_mm <= 0:
            raise ValueError("SID must be positive.")

        if self.sdd_mm <= 0:
            raise ValueError("SDD must be positive.")

        if self.sdd_mm <= self.sid_mm:
            raise ValueError(
                "SDD should be greater than SID."
            )

        if self.rotation_time_s <= 0:
            raise ValueError(
                "Rotation time must be positive."
            )

        if self.rotation_angle_deg <= 0:
            raise ValueError(
                "Rotation angle must be positive."
            )

        if self.num_views_per_rotation <= 0:
            raise ValueError(
                "Number of views must be positive."
            )

        if self.collimation_mm <= 0:
            raise ValueError(
                "Collimation must be positive."
            )

        if self.scan_geometry.lower() == "helical":

            if self.pitch <= 0:
                raise ValueError(
                    "Pitch must be positive for helical CT."
                )

        if self.scan_range_mm <= 0:
            raise ValueError(
                "Scan range must be positive."
            )

        if not 0 <= self.tcm_modulation_depth <= 1:
            raise ValueError(
                "TCM modulation depth must be between 0 and 1."
            )

        if self.volume_shape is not None:

            if len(self.volume_shape) != 3:
                raise ValueError(
                    "Volume shape must contain 3 dimensions."
                )

            if any(x <= 0 for x in self.volume_shape):
                raise ValueError(
                    "Volume dimensions must be positive."
                )

        if self.voxel_spacing_mm is not None:

            if len(self.voxel_spacing_mm) != 3:
                raise ValueError(
                    "Voxel spacing must contain 3 values."
                )

            if any(x <= 0 for x in self.voxel_spacing_mm):
                raise ValueError(
                    "Voxel spacing values must be positive."
                )

    # =========================================================
    # 2. CALCULATE ALL DERIVED PARAMETERS
    # =========================================================

    def calculate_all_derived_parameters(self):
        """
        Calculate all parameters derived from the input values.
        """

        self.calculate_magnification()

        self.calculate_angle_increment()

        self.calculate_table_feed()

        self.calculate_table_speed()

        self.calculate_scan_time()

        self.calculate_num_rotations()

        self.calculate_total_views()

        if (
            self.volume_shape is not None
            and self.voxel_spacing_mm is not None
        ):
            self.calculate_volume_information()

    # =========================================================
    # 3. MAGNIFICATION
    # =========================================================

    def calculate_magnification(self):
        """
        Calculate geometric magnification.

        M = SDD / SID
        """

        self.magnification = (
            self.sdd_mm / self.sid_mm
        )

        return self.magnification

    # =========================================================
    # 4. ANGULAR INCREMENT
    # =========================================================

    def calculate_angle_increment(self):
        """
        Calculate angular distance between consecutive views.

        angle increment =
        rotation angle / number of views
        """

        self.angle_increment_deg = (
            self.rotation_angle_deg
            / self.num_views_per_rotation
        )

        return self.angle_increment_deg

    # =========================================================
    # 5. VIEW ANGLES
    # =========================================================

    def view_angles_deg(self):
        """
        Generate gantry view angles in degrees.

        Example:
        360 views over 360 degrees
        gives approximately 1 degree spacing.

        Returns
        -------
        numpy.ndarray
            Array containing the view angles.
        """

        angles = np.arange(
            self.num_views_per_rotation
        ) * self.angle_increment_deg

        return angles

    # =========================================================
    # 6. TABLE FEED
    # =========================================================

    def calculate_table_feed(self):
        """
        Calculate table movement per gantry rotation.

        For helical CT:

        table feed =
        pitch × total collimation
        """

        if self.scan_geometry.lower() == "helical":

            self.table_feed_per_rotation_mm = (
                self.pitch
                * self.collimation_mm
            )

        else:

            self.table_feed_per_rotation_mm = 0.0

        return self.table_feed_per_rotation_mm

    # =========================================================
    # 7. TABLE SPEED
    # =========================================================

    def calculate_table_speed(self):
        """
        Calculate longitudinal table speed.

        table speed =
        table feed per rotation / rotation time
        """

        if self.scan_geometry.lower() == "helical":

            self.table_speed_mm_s = (
                self.table_feed_per_rotation_mm
                / self.rotation_time_s
            )

        else:

            self.table_speed_mm_s = 0.0

        return self.table_speed_mm_s

    # =========================================================
    # 8. NUMBER OF ROTATIONS
    # =========================================================

    def calculate_num_rotations(self):
        """
        Calculate the number of gantry rotations
        required to cover the scan range.
        """

        if self.scan_geometry.lower() == "helical":

            rotations = (
                self.scan_range_mm
                / self.table_feed_per_rotation_mm
            )

            self.num_rotations = math.ceil(rotations)

        else:

            self.num_rotations = 1

        return self.num_rotations

    # =========================================================
    # 9. TOTAL SCAN TIME
    # =========================================================

    def calculate_scan_time(self):
        """
        Calculate total scan time.

        total scan time =
        number of rotations × rotation time
        """

        if self.scan_geometry.lower() == "helical":

            self.total_scan_time_s = (
                self.num_rotations
                * self.rotation_time_s
            )

        else:

            self.total_scan_time_s = (
                self.rotation_time_s
            )

        return self.total_scan_time_s

    # =========================================================
    # 10. TOTAL VIEWS
    # =========================================================

    def calculate_total_views(self):
        """
        Calculate total number of projection views.
        """

        self.total_views = (
            self.num_rotations
            * self.num_views_per_rotation
        )

        return self.total_views

    # =========================================================
    # 11. SET 3D VOLUME
    # =========================================================

    def set_volume(
        self,
        volume: np.ndarray,
        voxel_spacing_mm: Tuple[float, float, float]
    ):
        """
        Attach a 3D voxel volume to the CT configuration.

        Parameters
        ----------
        volume : numpy.ndarray
            3D voxelized organ.

        voxel_spacing_mm : tuple
            Physical size of each voxel in mm.

        Example
        -------
        volume.shape = (128, 256, 256)
        spacing = (2.0, 0.8, 0.8)
        """

        if volume.ndim != 3:
            raise ValueError(
                "Input volume must be a 3D NumPy array."
            )

        if len(voxel_spacing_mm) != 3:
            raise ValueError(
                "Voxel spacing must have 3 values."
            )

        if any(
            spacing <= 0
            for spacing in voxel_spacing_mm
        ):
            raise ValueError(
                "Voxel spacing must be positive."
            )

        self.volume_shape = tuple(
            int(x) for x in volume.shape
        )

        self.voxel_spacing_mm = tuple(
            float(x)
            for x in voxel_spacing_mm
        )

        self.calculate_volume_information()

        return self.physical_volume_size_mm

    # =========================================================
    # 12. CALCULATE VOLUME INFORMATION
    # =========================================================

    def calculate_volume_information(self):
        """
        Calculate physical dimensions of the 3D volume.

        physical size =
        number of voxels × voxel spacing
        """

        if (
            self.volume_shape is None
            or self.voxel_spacing_mm is None
        ):
            return None

        self.physical_volume_size_mm = tuple(
            shape * spacing
            for shape, spacing
            in zip(
                self.volume_shape,
                self.voxel_spacing_mm
            )
        )

        self.calculate_required_fov()

        return self.physical_volume_size_mm

    # =========================================================
    # 13. REQUIRED FOV
    # =========================================================

    def calculate_required_fov(self):
        """
        Estimate a conservative transverse FOV
        based on the X-Y dimensions of the volume.
        """

        if self.physical_volume_size_mm is None:
            return None

        x_size = self.physical_volume_size_mm[0]
        y_size = self.physical_volume_size_mm[1]

        self.required_fov_mm = math.sqrt(
            x_size ** 2 +
            y_size ** 2
        )

        return self.required_fov_mm

    # =========================================================
    # 14. VOLUME CENTER
    # =========================================================

    def calculate_volume_center(self):
        """
        Calculate the center of the physical volume,
        assuming its origin is (0,0,0).
        """

        if self.physical_volume_size_mm is None:
            return None

        center = tuple(
            size / 2
            for size in self.physical_volume_size_mm
        )

        return center

    # =========================================================
    # 15. TCM PROFILE
    # =========================================================

    def generate_tcm_profile(self):
        """
        Generate a simple parameterized Tube Current
        Modulation profile.

        This is a simulation surrogate, not a
        vendor-specific clinical TCM algorithm.

        Formula:

        mA(theta) =
        base_mA × [1 + A sin(theta + phase)]
        """

        angles_deg = self.view_angles_deg()

        angles_rad = np.deg2rad(
            angles_deg +
            self.tcm_phase_deg
        )

        profile = (
            self.tube_current_ma
            *
            (
                1.0
                +
                self.tcm_modulation_depth
                * np.sin(angles_rad)
            )
        )

        # Clamp values to allowed mA range
        profile = np.clip(
            profile,
            self.ma_min,
            self.ma_max
        )

        self.tcm_profile_ma = profile

        return self.tcm_profile_ma

    # =========================================================
    # 16. GET TCM VALUE FOR A VIEW
    # =========================================================

    def get_tcm_current(self, view_index: int):
        """
        Return tube current for a specific view.
        """

        if not self.tcm_enabled:
            return self.tube_current_ma

        if self.tcm_profile_ma is None:
            self.generate_tcm_profile()

        if not (
            0 <= view_index
            < len(self.tcm_profile_ma)
        ):
            raise IndexError(
                "View index is outside the available "
                "views per rotation."
            )

        return float(
            self.tcm_profile_ma[view_index]
        )

    # =========================================================
    # 17. SOURCE POSITIONS
    # =========================================================

    def source_positions(
        self,
        z_start_mm: float = 0.0
    ):
        """
        Calculate X-ray source positions.

        For axial CT:
            circular trajectory

        For helical CT:
            helical trajectory

        Returns
        -------
        numpy.ndarray
            Shape: (N, 3)

            Columns:
            x, y, z
        """

        total_views = self.total_views

        if total_views <= 0:
            return np.empty(
                (0, 3)
            )

        angles_per_rotation = (
            self.rotation_angle_deg
        )

        angle_increment = (
            angles_per_rotation
            / self.num_views_per_rotation
        )

        view_indices = np.arange(
            total_views
        )

        angles_deg = (
            view_indices
            * angle_increment
        )

        angles_rad = np.deg2rad(
            angles_deg
        )

        # Circular coordinates
        x = (
            self.sid_mm
            * np.cos(angles_rad)
        )

        y = (
            self.sid_mm
            * np.sin(angles_rad)
        )

        if self.scan_geometry.lower() == "helical":

            # Number of completed rotations
            rotation_number = (
                view_indices
                / self.num_views_per_rotation
            )

            z = (
                z_start_mm
                +
                rotation_number
                * self.table_feed_per_rotation_mm
            )

        else:

            z = np.full(
                total_views,
                z_start_mm
            )

        positions = np.column_stack(
            (x, y, z)
        )

        return positions

    # =========================================================
    # 18. PROJECTION CONFIGURATION
    # =========================================================

    def get_projection_configuration(self):
        """
        Return the configuration required by
        the projection team.
        """

        return {
            "scan_geometry": self.scan_geometry,

            "sid_mm": self.sid_mm,

            "sdd_mm": self.sdd_mm,

            "magnification": self.magnification,

            "rotation_angle_deg":
                self.rotation_angle_deg,

            "num_views_per_rotation":
                self.num_views_per_rotation,

            "angle_increment_deg":
                self.angle_increment_deg,

            "pitch": self.pitch,

            "collimation_mm":
                self.collimation_mm,

            "table_feed_per_rotation_mm":
                self.table_feed_per_rotation_mm,

            "table_speed_mm_s":
                self.table_speed_mm_s,

            "num_rotations":
                self.num_rotations,

            "total_views":
                self.total_views
        }

    # =========================================================
    # 19. SUMMARY
    # =========================================================

    def summary(self):
        """
        Print a human-readable CT configuration summary.
        """

        print("\n")
        print("=" * 60)
        print("           CT SYSTEM CONFIGURATION")
        print("=" * 60)

        print(
            f"Scan geometry              : "
            f"{self.scan_geometry}"
        )

        print(
            f"kVp                       : "
            f"{self.kvp:.1f}"
        )

        print(
            f"Tube current              : "
            f"{self.tube_current_ma:.1f} mA"
        )

        print(
            f"SID                       : "
            f"{self.sid_mm:.2f} mm"
        )

        print(
            f"SDD                       : "
            f"{self.sdd_mm:.2f} mm"
        )

        print(
            f"Magnification             : "
            f"{self.magnification:.4f}"
        )

        print(
            f"Rotation time             : "
            f"{self.rotation_time_s:.3f} s"
        )

        print(
            f"Rotation angle            : "
            f"{self.rotation_angle_deg:.1f}°"
        )

        print(
            f"Views / rotation          : "
            f"{self.num_views_per_rotation}"
        )

        print(
            f"Angular increment         : "
            f"{self.angle_increment_deg:.6f}°"
        )

        print(
            f"Collimation               : "
            f"{self.collimation_mm:.2f} mm"
        )

        print(
            f"Pitch                     : "
            f"{self.pitch:.3f}"
        )

        print(
            f"Table feed / rotation     : "
            f"{self.table_feed_per_rotation_mm:.3f} mm"
        )

        print(
            f"Table speed               : "
            f"{self.table_speed_mm_s:.3f} mm/s"
        )

        print(
            f"Scan range                : "
            f"{self.scan_range_mm:.2f} mm"
        )

        print(
            f"Number of rotations       : "
            f"{self.num_rotations}"
        )

        print(
            f"Total scan time           : "
            f"{self.total_scan_time_s:.3f} s"
        )

        print(
            f"Total views               : "
            f"{self.total_views}"
        )

        print(
            f"TCM enabled               : "
            f"{self.tcm_enabled}"
        )

        if self.tcm_enabled:

            print(
                f"TCM modulation depth     : "
                f"{self.tcm_modulation_depth * 100:.1f}%"
            )

        if self.volume_shape is not None:

            print(
                f"Volume shape              : "
                f"{self.volume_shape}"
            )

        if self.voxel_spacing_mm is not None:

            print(
                f"Voxel spacing            : "
                f"{self.voxel_spacing_mm} mm"
            )

        if self.physical_volume_size_mm is not None:

            print(
                f"Physical volume size     : "
                f"{self.physical_volume_size_mm} mm"
            )

        if self.required_fov_mm is not None:

            print(
                f"Estimated required FOV   : "
                f"{self.required_fov_mm:.2f} mm"
            )

            if (
                self.required_fov_mm
                <= self.display_fov_mm
            ):

                print(
                    "FOV check                 : PASS"
                )

            else:

                print(
                    "FOV check                 : "
                    "WARNING - volume exceeds "
                    "display FOV"
                )

        print("=" * 60)

    # =========================================================
    # 20. PLOT VIEW ANGLES
    # =========================================================

    def plot_view_angles(self):
        """
        Plot gantry angle against view number.
        """

        angles = self.view_angles_deg()

        plt.figure(figsize=(10, 5))

        plt.plot(
            np.arange(len(angles)),
            angles
        )

        plt.xlabel("View Number")
        plt.ylabel("Gantry Angle (degrees)")

        plt.title(
            "CT Gantry View Angles"
        )

        plt.grid(True)

        plt.tight_layout()

        plt.show()

    # =========================================================
    # 21. PLOT TCM
    # =========================================================

    # def plot_tcm_profile(self):
        """
        Plot tube current modulation profile.
        """

        if not self.tcm_enabled:
            print(
                "TCM is disabled."
            )
            return

        if self.tcm_profile_ma is None:
            self.generate_tcm_profile()

        angles = self.view_angles_deg()

        plt.figure(figsize=(10, 5))

        plt.plot(
            angles,
            self.tcm_profile_ma
        )

        plt.xlabel(
            "Gantry Angle (degrees)"
        )

        plt.ylabel(
            "Tube Current (mA)"
        )

        plt.title(
            "Tube Current Modulation Profile"
        )

        plt.grid(True)

        plt.tight_layout()

        plt.show()

    # =========================================================
    # 22. EXPORT JSON
    # =========================================================

    def export_json(
        self,
        filename="ct_configuration.json"
    ):
        """
        Export configuration to JSON.
        """

        data = {
            "system_config": {
                "scan_geometry":
                    self.scan_geometry,

                "sid_mm":
                    self.sid_mm,

                "sdd_mm":
                    self.sdd_mm,

                "magnification":
                    self.magnification,

                "bore_diameter_mm":
                    self.bore_diameter_mm,

                "display_fov_mm":
                    self.display_fov_mm,

                "rotation_time_s":
                    self.rotation_time_s,

                "rotation_angle_deg":
                    self.rotation_angle_deg,

                "num_views_per_rotation":
                    self.num_views_per_rotation,

                "angle_increment_deg":
                    self.angle_increment_deg,

                "pitch":
                    self.pitch,

                "collimation_mm":
                    self.collimation_mm,

                "table_feed_per_rotation_mm":
                    self.table_feed_per_rotation_mm,

                "table_speed_mm_s":
                    self.table_speed_mm_s,

                "scan_range_mm":
                    self.scan_range_mm,

                "total_scan_time_s":
                    self.total_scan_time_s,

                "num_rotations":
                    self.num_rotations,

                "total_views":
                    self.total_views
            },

            "volume": {
                "shape":
                    self.volume_shape,

                "voxel_spacing_mm":
                    self.voxel_spacing_mm,

                "physical_size_mm":
                    self.physical_volume_size_mm,

                "required_fov_mm":
                    self.required_fov_mm
            },

            "tcm": {
                "enabled":
                    self.tcm_enabled,

                "modulation_depth":
                    self.tcm_modulation_depth,

                "phase_deg":
                    self.tcm_phase_deg
            }
        }

        # Convert tuples to lists for JSON
        def convert(obj):

            if isinstance(obj, tuple):
                return list(obj)

            return obj

        with open(
            filename,
            "w"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                default=convert
            )

        print(
            f"\nConfiguration saved to: "
            f"{filename}"
        )

    # =========================================================
    # 23. GET COMPLETE CONFIGURATION
    # =========================================================

    def get_complete_configuration(self):
        """
        Return a Python dictionary containing
        the complete configuration.
        """

        return {
            "system_config": {
                "scan_geometry":
                    self.scan_geometry,

                "sid_mm":
                    self.sid_mm,

                "sdd_mm":
                    self.sdd_mm,

                "magnification":
                    self.magnification,

                "bore_diameter_mm":
                    self.bore_diameter_mm,

                "display_fov_mm":
                    self.display_fov_mm,

                "rotation_time_s":
                    self.rotation_time_s,

                "rotation_angle_deg":
                    self.rotation_angle_deg,

                "num_views_per_rotation":
                    self.num_views_per_rotation,

                "angle_increment_deg":
                    self.angle_increment_deg,

                "pitch":
                    self.pitch,

                "collimation_mm":
                    self.collimation_mm,

                "table_feed_per_rotation_mm":
                    self.table_feed_per_rotation_mm,

                "table_speed_mm_s":
                    self.table_speed_mm_s,

                "scan_range_mm":
                    self.scan_range_mm,

                "total_scan_time_s":
                    self.total_scan_time_s,

                "num_rotations":
                    self.num_rotations,

                "total_views":
                    self.total_views
            },

            "volume": {
                "shape":
                    self.volume_shape,

                "voxel_spacing_mm":
                    self.voxel_spacing_mm,

                "physical_size_mm":
                    self.physical_volume_size_mm,

                "required_fov_mm":
                    self.required_fov_mm
            },

            "tcm": {
                "enabled":
                    self.tcm_enabled,

                "modulation_depth":
                    self.tcm_modulation_depth,

                "phase_deg":
                    self.tcm_phase_deg
            }
        }