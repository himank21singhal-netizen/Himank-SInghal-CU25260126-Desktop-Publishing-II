# LabSheet-1 Desktop Publishing- II (Photoshop)

## Student Details
- **Name:** HIMANK SINGHAL
- **Roll Number:** 253026107
- **Course:** BCA
- **Semester:** 3rd Sem
- **University:** COER University
- **Course Code:** UAC012P

## Course Outline

### Module 1: Introduction to Adobe Photoshop
- Overview of Adobe Photoshop interface.
- Understanding raster graphics.
- Basic tools and their functions: selection, brush, eraser, etc.
- Creating and saving a new document.
- Basic photo editing and retouching.

### Module 2: Advanced Techniques in Adobe Photoshop
- Working with layers and masks.
- Using color correction and adjustment layers.
- Advanced selection techniques: Quick Selection, Magic Wand, and Lasso.
- Applying filters and effects.
- Text handling and formatting.
- Creating and using custom brushes.
- Working with blending modes and layer styles.

## Practical Index
- [Practical 01 - Photoshop Interface and Basic Tools](Practical-01/) (Module 1)
- [Practical 02 - Photo Editing and Basic Retouching](Practical-02/) (Module 1)
- [Practical 03 - Layers, Masks and Creative Composition](Practical-03/) (Module 2)
- [Practical 04 - Advanced Selection, Color Correction and Adjustment Layers](Practical-04/) (Module 2)
- [Practical 05 - Filters, Effects, Custom Brushes and Blending Modes](Practical-05/) (Module 2)
- [Practical 06 - Complete Photoshop Project - Promotional Poster](Practical-06/) (Module 1 + Module 2)

## Assessment Pattern

| Practical | Main Skills | Marks |
|-----------|-------------|-------|
| [Practical 01](Practical-01/) | Interface & Basic Tools | 05 |
| [Practical 02](Practical-02/) | Photo Editing & Retouching | 05 |
| [Practical 03](Practical-03/) | Layers & Masks | 05 |
| [Practical 04](Practical-04/) | Selection & Color Correction | 05 |
| [Practical 05](Practical-05/) | Filters, Brushes & Effects | 05 |
| [Practical 06](Practical-06/) | Integrated Photoshop Project | 05 |
| -- | GitHub Repository, README & File Organization | -- |
| **Total** | **All Components** | **30** |

## Repository Structure
```text
Adobe-Photoshop-Practicals/
|-- README.md
|-- Practical-01/
|   |-- Practical_01_HIMANK_SINGHAL_253026107.psd
|   |-- Practical_01_HIMANK_SINGHAL_253026107.jpg
|   |-- README.md
|-- Practical-02/
|   |-- Practical_02_HIMANK_SINGHAL_253026107.psd
|   |-- Practical_02_HIMANK_SINGHAL_253026107.jpg
|   |-- Before_After_Practical_02.jpg
|   |-- README.md
|-- Practical-03/
|   |-- Practical_03_HIMANK_SINGHAL_253026107.psd
|   |-- Practical_03_HIMANK_SINGHAL_253026107.jpg
|   |-- README.md
|-- Practical-04/
|   |-- Practical_04_HIMANK_SINGHAL_253026107.psd
|   |-- Practical_04_HIMANK_SINGHAL_253026107.jpg
|   |-- README.md
|-- Practical-05/
|   |-- Practical_05_HIMANK_SINGHAL_253026107.psd
|   |-- Practical_05_HIMANK_SINGHAL_253026107.png
|   |-- README.md
|-- Practical-06/
|   |-- Practical_06_HIMANK_SINGHAL_253026107.psd
|   |-- Practical_06_HIMANK_SINGHAL_253026107.jpg
|   |-- README.md
```

## Pushing Large PSD Files with Git LFS
Photoshop PSD files grow quickly. GitHub's browser upload accepts files up to 25 MiB,
warns above 50 MiB on `git push`, and blocks any normal Git file above 100 MiB. Use
**Git Large File Storage (Git LFS)** so that large PSD files are not rejected.

1. Install Git LFS from <https://git-lfs.com> and enable it once per computer:
   ```bash
   git lfs install
   ```
2. Inside the repository, tell Git LFS to track PSD files **before** adding them:
   ```bash
   git lfs track "*.psd"
   git add .gitattributes
   ```
3. Add, commit and push as usual:
   ```bash
   git add .
   git commit -m "Add Photoshop practicals"
   git push origin main
   ```
4. If a PSD was already committed and the push is rejected, convert the history:
   ```bash
   git lfs migrate import --include="*.psd"
   git push --force-with-lease origin main
   ```
5. Do not use the browser "Upload files" button for PSDs larger than 25 MiB; push from
   the command line instead.

Confirm the instructions with your faculty/IT support before submitting the repository
link through the LMS/ERP portal.
