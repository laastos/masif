"""
simple_mesh.py: Simple ply loading class.
I created this class to avoid the need to install pymesh if the only goal is to load ply files.
Use this only for the pymol plugin. Currently only supports ascii ply files.
Pablo Gainza - LPDI STI EPFL 2019
This file is part of MaSIF.
Released under an Apache License 2.0
"""
import numpy as np

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


class Simple_mesh:
    def __init__(self):
        self.vertices = []
        self.faces = []

    def load_mesh(self, filename):
        lines = open(filename, "r").readlines()
        # Read header
        self.attribute_names = []
        self.num_verts = 0
        line_ix = 0
        while "end_header" not in lines[line_ix]:
            line = lines[line_ix]
            if line.startswith("element vertex"):
                self.num_verts = int(line.split(" ")[2])
            if line.startswith("property float"):
                self.attribute_names.append("vertex_" + line.split(" ")[2].rstrip())
            if line.startswith("element face"):
                self.num_faces = int(line.split(" ")[2])
            line_ix += 1
        line_ix += 1
        header_lines = line_ix
        self.attributes = {}
        for at in self.attribute_names:
            self.attributes[at] = []
        self.vertices = []
        self.normals = []
        self.faces = []
        # Read vertex attributes.
        for i in range(header_lines, self.num_verts + header_lines):
            cur_line = lines[i].split(" ")
            vert_att = [float(x) for x in cur_line]
            # Organize by attributes
            for jj, att in enumerate(vert_att):
                self.attributes[self.attribute_names[jj]].append(att)
            line_ix += 1
        # Set up vertices
        for jj in range(len(self.attributes["vertex_x"])):
            self.vertices = np.vstack(
                [
                    self.attributes["vertex_x"],
                    self.attributes["vertex_y"],
                    self.attributes["vertex_z"],
                ]
            ).T
        # Read faces.
        face_line_start = line_ix
        for i in range(face_line_start, face_line_start + self.num_faces):
            try:
                fields = lines[i].split(" ")
            except:
                ipdb.set_trace()
            face = [int(x) for x in fields[1:]]
            self.faces.append(face)
        self.faces = np.array(self.faces)
        self.vertices = np.array(self.vertices)
        # Convert to numpy array all attributes.
        for key in self.attributes.keys():
            self.attributes[key] = np.array(self.attributes[key])

    def get_attribute_names(self):
        return list(self.attribute_names)

    def get_attribute(self, attribute_name):
        return np.copy(self.attributes[attribute_name])

    def build_surface_graph(self):
        """
        Build a NetworkX graph from mesh for geodesic distance computation.
        Edge weights are Euclidean distances between connected vertices.
        Returns the graph object.
        """
        if not HAS_NETWORKX:
            raise ImportError("NetworkX is required for patch computation. Install with: pip install networkx")

        graph = nx.Graph()
        for face in self.faces:
            # Handle triangular faces
            if len(face) >= 3:
                for i in range(len(face)):
                    u = int(face[i])
                    v = int(face[(i + 1) % len(face)])
                    if not graph.has_edge(u, v):
                        weight = float(np.linalg.norm(self.vertices[u] - self.vertices[v]))
                        graph.add_edge(u, v, weight=weight)
        return graph

    def extract_patch(self, graph, center_vertex, radius):
        """
        Extract patch vertices within geodesic radius using Dijkstra's algorithm.

        Args:
            graph: NetworkX graph built from mesh
            center_vertex: Index of the patch center vertex
            radius: Geodesic radius in Angstroms

        Returns:
            List of vertex indices within the patch
        """
        if not HAS_NETWORKX:
            raise ImportError("NetworkX is required for patch computation.")

        lengths = nx.single_source_dijkstra_path_length(graph, center_vertex, cutoff=radius, weight='weight')
        return list(lengths.keys())

    def compute_all_patches(self, radius=9.0, progress_callback=None):
        """
        Compute patches for all vertices.

        Args:
            radius: Geodesic radius in Angstroms
            progress_callback: Optional callback function(current, total) for progress updates

        Returns:
            List of patches, where each patch is a list of vertex indices
        """
        graph = self.build_surface_graph()
        patches = []
        n_verts = len(self.vertices)

        for i in range(n_verts):
            patch = self.extract_patch(graph, i, radius)
            patches.append(patch)
            if progress_callback and i % 1000 == 0:
                progress_callback(i, n_verts)

        return patches

    def compute_patch_scores(self, patches, weights=None):
        """
        Compute scores for all patches based on vertex features.

        Args:
            patches: List of patches (each patch is a list of vertex indices)
            weights: Feature weights [iface, charge, hphob, hbond]. Default: [1.0, 0.3, 0.5, 0.8]

        Returns:
            Array of scores, one per patch
        """
        if weights is None:
            weights = np.array([1.0, 0.3, 0.5, 0.8])
        else:
            weights = np.array(weights)

        # Get available features
        features = []
        feature_names = ['vertex_iface', 'vertex_charge', 'vertex_hphob', 'vertex_hbond']
        alt_names = ['iface', 'charge', 'hphob', 'hbond']

        for i, (name, alt) in enumerate(zip(feature_names, alt_names)):
            if name in self.attribute_names:
                features.append(self.get_attribute(name))
            elif alt in self.attribute_names:
                features.append(self.get_attribute(alt))
            else:
                # Use zeros if feature not available
                features.append(np.zeros(len(self.vertices)))

        feature_matrix = np.vstack(features).T  # Shape: (n_vertices, 4)

        scores = []
        for patch in patches:
            if len(patch) == 0:
                scores.append(0.0)
            else:
                patch_features = feature_matrix[patch]
                weighted_mean = np.mean(patch_features * weights, axis=0)
                scores.append(float(np.sum(weighted_mean)))

        return np.array(scores)

    def get_top_patches(self, top_k=100, radius=9.0, iface_cutoff=0.0, weights=None):
        """
        Compute and return top-K patches ranked by score.

        Args:
            top_k: Number of top patches to return
            radius: Geodesic radius in Angstroms
            iface_cutoff: Minimum iface score for patch center (filter low-scoring centers)
            weights: Feature weights [iface, charge, hphob, hbond]

        Returns:
            Dictionary with 'centers', 'scores', 'vertex_indices'
        """
        print(f"Computing patches with radius={radius}A...")
        patches = self.compute_all_patches(radius)

        print("Computing patch scores...")
        scores = self.compute_patch_scores(patches, weights)

        # Filter by iface_cutoff if iface attribute exists
        valid_indices = np.arange(len(scores))
        if iface_cutoff > 0:
            iface_name = 'vertex_iface' if 'vertex_iface' in self.attribute_names else 'iface'
            if iface_name in self.attribute_names:
                iface = self.get_attribute(iface_name)
                valid_indices = np.where(iface >= iface_cutoff)[0]

        # Get top-K from valid indices
        valid_scores = scores[valid_indices]
        top_local_idx = np.argsort(-valid_scores)[:top_k]
        top_idx = valid_indices[top_local_idx]

        result = {
            "centers": [int(i) for i in top_idx],
            "scores": [float(scores[i]) for i in top_idx],
            "vertex_indices": [[int(x) for x in patches[i]] for i in top_idx],
        }

        return result

