import os
import xml.etree.ElementTree as ET


# -----------------------------
# LOAD XML FILE
# -----------------------------
def load_xml(path):
    tree = ET.parse(path)
    return tree.getroot()


# -----------------------------
# BASIC INFORMATION
# -----------------------------
def get_basic_info(root):
    return {
        "id": root.find("id").text,
        "anomaly_presence": root.find("anomaly_presence").text,
        "category": root.find("category").text,
        "type": root.find("type").text,
        "criticality": root.find("criticality").text,
        "textual_explanation": root.find("textual_explanation").text,
    }


# -----------------------------
# LIST ALL DIMENSIONS
# -----------------------------
def list_dimensions(root):
    return [
        d.find("name").text
        for d in root.find("dimensions").findall("dimension")
    ]


# -----------------------------
# GET ALL ANOMALIES FOR A GIVEN STORE
# -----------------------------
def get_anomalies_by_store(root, store_id):
    results = []

    for dim in root.find("dimensions").findall("dimension"):
        dim_name = dim.find("name").text
        anomalies = dim.find("anomalies")

        if anomalies is None:
            continue

        for an in anomalies.findall("anomaly"):
            store = an.find("store").text

            if store == str(store_id):
                results.append({
                    "dimension": dim_name,
                    "offset_minutes": an.find("offset_minutes").text,
                    "duration_minutes": an.find("duration_minutes").text,
                    "disk": an.find("disk").text,
                    "degradation": an.find("degradation").text
                })

    return results

def get_related_dimensions_by_dimension(root, dimension_name):
    """
    Returns all related dimensions for a given dimension
    """

    results = set()

    for dim in root.find("dimensions").findall("dimension"):
        if dim.find("name").text != dimension_name:
            continue

        anomalies = dim.find("anomalies")
        if anomalies is None:
            return []

        for an in anomalies.findall("anomaly"):
            rel_node = an.find("related_dimensions")

            if rel_node is None:
                continue

            for d in rel_node.findall("dimension"):
                results.add(d.text)

        return list(results)

    return []


# -----------------------------
# GET DEGRADATION 
# -----------------------------
def get_degradation_by_dimension(root, dimension_name):
    """
    Returns all anomaly entries for a specific dimension,
    including degradation.
    """

    for dim in root.find("dimensions").findall("dimension"):
        name = dim.find("name").text

        # Select only the target dimension
        if name != dimension_name:
            continue

        anomalies = dim.find("anomalies")
        if anomalies is None:
            return []

        results = []

        for an in anomalies.findall("anomaly"):

            degradation = an.find("degradation").text
            if not degradation or not degradation.strip():
                continue

            results.append({
                "offset_minutes": an.find("offset_minutes").text,
                "duration_minutes": an.find("duration_minutes").text,
                "store": an.find("store").text,
                "disk": an.find("disk").text,
                "degradation": degradation,
            })

        return results

    return []


# -----------------------------
# DEMO QUERIES
# -----------------------------
def demo(xml_path):
    root = load_xml(xml_path)

    print("\n=== GLOBAL ANOMALY INFO ===")
    print(get_basic_info(root))

    print("\n=== DIMENSIONS ===")
    print(list_dimensions(root))

    print("\n=== STORE 2 ANOMALIES ===")
    print(get_anomalies_by_store(root, 2))

    print("\n=== DEGRADATION (store2-balance_balanced_tasks) ===")
    print(get_degradation_by_dimension(root, "store2-balance_balanced_tasks"))

    print("\n===  DIMENSIONS INVOLVED IN THE SAME ANOMALY (balance_balanced_tasks) ===")
    print(get_related_dimensions_by_dimension(root, "store2-balance_balanced_tasks"))


# -----------------------------
# RUN SCRIPT
# -----------------------------
if __name__ == "__main__":
    example_file = "Annotations/1774478743.xml"
    demo(example_file)