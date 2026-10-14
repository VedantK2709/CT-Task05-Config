# CT-Task05-Config

# Task 4: CT System Configuration

### 1. Module Overview

The **CT System Configuration** module is responsible for defining and managing the parameters required to simulate a CT scanner. It acts as a central configuration and control module between the different stages of the CT simulation pipeline. The module stores scanner parameters such as tube voltage (kVp), tube current (mA), source-to-isocenter distance (SID), source-to-detector distance (SDD), number of views, rotation time, pitch, collimation, and scan range.

The module also calculates important derived parameters required by other teams, including **geometric magnification, angular increment, table feed per rotation, table speed, number of rotations, total scan time, and total number of projections**. For helical CT, it generates the corresponding gantry view angles and helical X-ray source trajectory.

The configuration module can also accept a **3D voxel volume representing the scanned organ/object along with voxel spacing**. From this information, it determines the physical dimensions of the volume and the required field of view. The voxel data itself is passed to the appropriate tissue-interaction module for attenuation calculations. The configuration module therefore focuses on **how the CT scanner acquires the data**, rather than performing the tissue attenuation or reconstruction itself.

---

### 2. Inputs & Outputs

#### Inputs

* **3D voxel volume** — A 3D NumPy array representing the scanned organ or phantom.
* **Voxel spacing** — Physical dimensions of each voxel in mm, specified as `(z, y, x)`.
* **Tube voltage (kVp)** — X-ray tube operating voltage, e.g. `120 kVp`.
* **Tube current (mA)** — X-ray tube current, e.g. `200 mA`.
* **SID (Source-to-Isocenter Distance)** — Distance between the X-ray source and the scanner isocenter.
* **SDD (Source-to-Detector Distance)** — Distance between the X-ray source and detector.
* **Rotation time** — Time required for one complete gantry rotation.
* **Number of views per rotation** — Number of projection measurements acquired during one rotation.
* **Pitch** — Table movement relative to the total beam collimation during helical scanning.
* **Collimation** — Effective width of the X-ray beam along the z-axis.
* **Scan range** — Length of the anatomical region being scanned.
* **TCM parameters** — Parameters controlling the simulated tube-current modulation profile.

#### Outputs

* **Magnification** — Geometric magnification calculated from SDD and SID.
* **View angles** — Gantry angles corresponding to individual projection views.
* **Angular increment** — Angular separation between consecutive views.
* **Table feed per rotation** — Distance travelled by the patient table during one gantry rotation.
* **Table speed** — Calculated table movement per second.
* **Number of rotations** — Number of gantry rotations required to cover the specified scan range.
* **Total scan time** — Estimated duration of the CT acquisition.
* **Total number of views** — Total number of projection views generated for the scan.
* **Helical source positions** — 3D `(x, y, z)` coordinates of the X-ray source for every projection.
* **TCM profile** — Simulated tube-current value for each projection/view.
* **Physical volume dimensions** — Physical size of the input 3D voxel volume.
* **Required FOV** — Estimated field of view required to cover the input volume.
* **Configuration JSON** — Complete scanner configuration and derived parameters exported in JSON format.

---

### 3. Current Progress

* [x] Implemented the CT configuration as a Python class.
* [x] Implemented scanner parameter storage and validation.
* [x] Implemented geometric magnification calculation.
* [x] Implemented angular increment calculation.
* [x] Implemented CT view-angle generation.
* [x] Implemented helical table-feed calculation.
* [x] Implemented table-speed calculation.
* [x] Implemented number-of-rotations calculation.
* [x] Implemented total scan-time calculation.
* [x] Implemented total projection/view calculation.
* [x] Implemented 3D helical X-ray source trajectory generation.
* [x] Implemented 3D voxel-volume input and voxel-spacing handling.
* [x] Implemented physical volume-size and FOV calculations.
* [x] Implemented parameterized tube-current modulation (TCM) profile.
* [x] Implemented configuration export to JSON.
* [x] Implemented visualization of view angles and TCM profile.
* [x] Created an integration example using `main.py`.
* [x] Integrate with the final 3D voxel dataset provided by the project.
* [x] Integrate and test the configuration interface with all other project modules.
* [x] Perform final end-to-end validation of the complete CT simulation pipeline.

---
### 4. How We Will Validate Results

The CT Configuration module will be validated using both **numerical checks and physical consistency checks**.

* Check that all input parameters are within valid physical and simulation ranges.

* Check that the input voxel data is a valid 3D array.

* Check that voxel spacing contains three positive values.

* Check that `SDD > SID`.

* Check that the calculated magnification is physically consistent:

  `Magnification = SDD / SID`

* Check that the angular increment is consistent with the number of views:

  `Angular Increment = Rotation Angle / Number of Views`

* Check that the table feed is consistent with pitch and collimation:

  `Table Feed = Pitch × Collimation`

* Check that the calculated number of rotations covers the complete scan range.

* Check that the generated source trajectory contains the expected number of projection positions.

* Check that the generated source coordinates contain no `NaN` or infinite values.

* Check that the TCM current remains within the specified minimum and maximum mA limits.

* Check that the physical dimensions calculated from the voxel volume match the expected organ dimensions.

* Check that the required FOV is sufficient to cover the input volume.

* Verify that the generated configuration can be successfully passed to the projection, source, tissue-interaction, and reconstruction modules.

* Perform an end-to-end test using the complete CT simulation pipeline.

---

### 5. Code Files

The main implementation files for the CT Configuration module are:

* **`ct_configuration.py`** — Main CT configuration class containing scanner parameters, validation, derived calculations, view-angle generation, helical source trajectory generation, TCM generation, voxel-volume handling, and JSON export.
* **`main.py`** — Demonstration/integration script showing how the CT Configuration module is initialized and used with a 3D voxel volume.

The CT Configuration module is designed to provide a common interface for the other modules in the CT simulation pipeline, allowing them to obtain the required scanner parameters and acquisition geometry without duplicating the configuration calculations.
