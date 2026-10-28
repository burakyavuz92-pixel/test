# Optional OCCT experiment

This module is deliberately separate from the existing SheetPreview renderer. No existing production command switches to it. To stop using it, do not call `occt-demo`; existing commands keep their previous backend. No OpenRouter call is made. This is a local Python native-CAD worker called through a C# process adapter (`IIsometricBackend`). A future CAD backend can implement the same interface.

## Installed stack

- Python 3.12, cadquery-ocp 7.9.3.1 (OCCT bindings), VTK 9.5.2, Pillow 12.2.0.
- Exact environment versions: requirements.lock. OCCT itself is loaded from precompiled wheels, not compiled from its C++ source here. The C# application/adapter was compiled with .NET 8.
- Dependencies were installed from PyPI over verified HTTPS. Installation needs network access; geometry/rendering does not.

From repository root in this cloud environment:

```bash
UV_CACHE_DIR=/workspace/.uv-cache uv venv --allow-existing /workspace/occt-venv
UV_CACHE_DIR=/workspace/.uv-cache uv pip sync --python /workspace/occt-venv/bin/python experiments/occt/requirements.lock
/workspace/occt-venv/bin/python experiments/occt/test_geometry.py
DOTNET_CLI_HOME=/workspace/.dotnet-home NUGET_PACKAGES=/workspace/.nuget/packages /workspace/.dotnet/dotnet build src/DrawingTool.csproj
DOTNET_CLI_HOME=/workspace/.dotnet-home NUGET_PACKAGES=/workspace/.nuget/packages /workspace/.dotnet/dotnet run --no-build --project src/DrawingTool.csproj -- occt-demo experiments/occt/plate-160.json output/occt-new-demo
```

Output directory must be empty or absent. OCCT_PYTHON can override the Python executable; on Windows point it to the matching local venv's python.exe. Worker and native wheels must also be installed there. Windows distribution has NOT been tested. Run from repository root. No font is needed for this standalone image (existing drawing commands still use Arial).

## Geometry

Example is the known 11-30-212: diameter 160, total depth 33, base/side thickness 3, outer bend R8 and inner bend R5; 10/10/5 mm holes. X/Y coordinates are on the front face, Z=0 outside front, the open cup extends toward negative Z. The R5 follows the uniform-thickness assumption, not a separately measured dimension.

A profile with true circular arcs is revolved 360 degrees by OCCT; cylinders are subtracted with OCCT Boolean operations. Verification: valid BRep, exactly one solid, each hole-volume change matches pi*r²*thickness, hole interiors classify outside material, intact base classifies inside. STEP is exported then reloaded and validity/volume rechecked.

OCCT tessellates for display at 0.08 mm linear and 0.08 rad angular deflection. VTK uses real depth testing and mesh silhouettes/feature edges. Smooth tangent transitions are shaded rather than painted as concentric black ellipse bands. Display triangulation and lighting are approximations; STEP retains analytic geometry. Camera and shading are still visual choices subject to user review. Current standalone JPEG is 1400×1100 at 150 DPI, not an A4 dimensioned sheet and not assigned a manufacturing print scale. Integrating the view into the source-DPI sheet comes only after accepting its appearance.

## Verified in this instance

- Six geometry regression tests passed (three/two-hole, asymmetric, overlap/bend/radius rejection).
- C# -> Python -> OCCT -> STEP/STL -> VTK -> JPEG succeeded.
- STEP roundtrip and hole volumes verified.
- Offscreen rendering used vtkEGLRenderWindow selected by VTK's factory. Mesa llvmpipe renderer confirms CPU software rendering; no dedicated GPU was required.
- Constructing vtkEGLRenderWindow directly crashed in this environment; factory selection is retained. A harmless X connection warning can precede EGL fallback on headless Linux.
- Existing drawing backend remains available. No Excel batch or automatic JPEG interpretation was tested with this new backend. The example parameters are supplied explicitly, from the already-known row.

## Licensing/distribution

OCCT is LGPL-2.1 with its additional exception; the installed cadquery-ocp binding's LICENSE is Apache-2.0, VTK is BSD and Pillow is MIT-CMU. The worker uses these components locally and requires no paid CAD service or per-image license. Redistributing native binaries still requires their applicable notices/licenses and LGPL obligations; a ready-to-distribute Windows installer and complete third-party notice bundle are not part of this experiment. Do not copy the user's Arial font into a public distribution.
