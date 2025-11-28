import pymesh
import numpy
"""
read_ply.py: Save a ply file to disk using pymesh and load the attributes used by MaSIF. 
Pablo Gainza - LPDI STI EPFL 2019
Released under an Apache License 2.0
"""


def save_ply(
    filename,
    vertices,
    faces=[],
    normals=None,
    charges=None,
    vertex_cb=None,
    hbond=None,
    hphob=None,
    iface=None,
    shape_index=None,
    normalize_charges=False,
):
    """ Save vertices, mesh in ply format.
        vertices: coordinates of vertices
        faces: mesh
    """
    mesh = pymesh.form_mesh(vertices, faces)
    if normals is not None:
        n1 = normals[:, 0]
        n2 = normals[:, 1]
        n3 = normals[:, 2]
        mesh.add_attribute("vertex_nx")
        mesh.set_attribute("vertex_nx", n1)
        mesh.add_attribute("vertex_ny")
        mesh.set_attribute("vertex_ny", n2)
        mesh.add_attribute("vertex_nz")
        mesh.set_attribute("vertex_nz", n3)
    if charges is not None:
        mesh.add_attribute("charge")
        # Note: Removed /10 normalization that caused double normalization issues.
        # APBS outputs in kT/e units. Values are typically in [-30, 30] range.
        # Downstream code (read_data_from_surface.py) clips to [-3, 3] and normalizes.
        # The normalize_charges flag is kept for backwards compatibility but no longer
        # performs division - it's a no-op marker that charges should be processed.
        mesh.set_attribute("charge", charges)
    if hbond is not None:
        mesh.add_attribute("hbond")
        mesh.set_attribute("hbond", hbond)
    if vertex_cb is not None:
        mesh.add_attribute("vertex_cb")
        mesh.set_attribute("vertex_cb", vertex_cb)
    if hphob is not None:
        mesh.add_attribute("vertex_hphob")
        # Normalize Kyte-Doolittle hydrophobicity scale from [-4.5, 4.5] to [-1, 1]
        # This ensures consistent scale with other features for visualization
        hphob_normalized = numpy.array(hphob) / 4.5
        mesh.set_attribute("vertex_hphob", hphob_normalized)
    if iface is not None:
        mesh.add_attribute("vertex_iface")
        mesh.set_attribute("vertex_iface", iface)

    if shape_index is not None:
        mesh.add_attribute("vertex_si")
        mesh.set_attribute("vertex_si", shape_index)

    pymesh.save_mesh(
        filename, mesh, *mesh.get_attribute_names(), use_float=True, ascii=True
    )

