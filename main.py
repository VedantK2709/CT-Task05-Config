import numpy as np

from ct_configuration import CTConfiguration
from cylinder_voxel import create_cylinder_voxel


def main():

    print("\nStarting CT Configuration Module...")

    # =====================================================
    # STEP 1: CREATE 3D VOXEL ORGAN
    # =====================================================

    organ, material = create_cylinder_voxel(
        radius_mm=25.0,
        height_mm=50.0,
        voxel_size_mm=1.0,
        density=1.0,
        material_id=1
    )

    print("\nVoxel data loaded successfully.")

    print("Voxel shape:", organ.shape)
    print("Voxel data type:", organ.dtype)
    print("Minimum density:", np.min(organ))
    print("Maximum density:", np.max(organ))
    print("Number of occupied voxels:", np.count_nonzero(organ))

    # Since voxel_size_mm = 1.0
    voxel_spacing_mm = (
        1.0,
        1.0,
        1.0
    )

    # =====================================================
    # STEP 2: CREATE CT CONFIGURATION
    # =====================================================

    config = CTConfiguration(

        scan_geometry="helical",

        kvp=120.0,

        tube_current_ma=200.0,

        ma_min=60.0,

        ma_max=660.0,

        exposure_time_s=1.0,

        total_mas=200.0,

        sid_mm=541.0,

        sdd_mm=949.0,

        bore_diameter_mm=820.0,

        display_fov_mm=500.0,

        rotation_time_s=0.28,

        rotation_angle_deg=360.0,

        num_views_per_rotation=984,

        pitch=0.516,

        collimation_mm=40.0,

        scan_range_mm=350.0,

        tcm_enabled=False,

        tcm_modulation_depth=0.25,

        tcm_phase_deg=0.0
    )

    # =====================================================
    # STEP 3: PROVIDE THE VOXEL DATA
    # =====================================================

    config.set_volume(
        organ,
        voxel_spacing_mm
    )

    # =====================================================
    # STEP 4: PRINT CONFIGURATION
    # =====================================================

    config.summary()

    # =====================================================
    # STEP 5: VIEW ANGLES
    # =====================================================

    angles = config.view_angles_deg()

    print("\nFirst 10 view angles:")
    print(angles[:10])

    print(
        "\nNumber of views per rotation:",
        len(angles)
    )

    # =====================================================
    # STEP 6: SOURCE POSITIONS
    # =====================================================

    positions = config.source_positions()

    print(
        "\nSource position array shape:",
        positions.shape
    )

    print("\nFirst 5 source positions:")
    print(positions[:5])

    # =====================================================
    # STEP 7: TCM PROFILE
    # =====================================================

    # tcm = config.generate_tcm_profile()

    # print("\nFirst 10 TCM values:")
    # print(tcm[:10])

    # print(
    #     "\nMinimum TCM current:",
    #     np.min(tcm),
    #     "mA"
    # )

    # print(
    #     "Maximum TCM current:",
    #     np.max(tcm),
    #     "mA"
    # )

    # =====================================================
    # STEP 8: PROJECTION CONFIGURATION
    # =====================================================

    projection_config = (
        config.get_projection_configuration()
    )

    print(
        "\nConfiguration sent to Projection Team:"
    )

    for key, value in projection_config.items():
        print(f"{key}: {value}")

    # =====================================================
    # STEP 9: EXPORT JSON
    # =====================================================

    config.export_json(
        "ct_configuration.json"
    )

    # =====================================================
    # STEP 10: PLOTS
    # =====================================================

    config.plot_view_angles()

    config.plot_tcm_profile()

    print(
        "\nCT Configuration Module "
        "completed successfully."
    )


if __name__ == "__main__":
    main()