"""Cityscapes train IDs and dashboard display categories (colour legend)."""

from dataclasses import dataclass

# Cityscapes 19-class trainId -> name (model output indices)
CITYSCAPES_TRAIN_ID_TO_NAME: dict[int, str] = {
    0: "road",
    1: "sidewalk",
    2: "building",
    3: "wall",
    4: "fence",
    5: "pole",
    6: "traffic light",
    7: "traffic sign",
    8: "vegetation",
    9: "terrain",
    10: "sky",
    11: "person",
    12: "rider",
    13: "car",
    14: "truck",
    15: "bus",
    16: "train",
    17: "motorcycle",
    18: "bicycle",
}


@dataclass(frozen=True)
class DisplayCategory:
    key: str
    label: str
    color_rgb: tuple[int, int, int]
    cityscapes_labels: tuple[str, ...]


# Module 4 + architecture diagram legend
DISPLAY_CATEGORIES: tuple[DisplayCategory, ...] = (
    DisplayCategory("road", "Road", (128, 64, 128), ("road",)),
    DisplayCategory(
        "vehicles",
        "Vehicles",
        (0, 0, 142),
        ("car", "truck", "bus", "train", "motorcycle", "bicycle", "rider"),
    ),
    DisplayCategory("pedestrians", "Pedestrians", (220, 20, 60), ("person",)),
    DisplayCategory(
        "lane_markings",
        "Lane Markings",
        (250, 170, 30),
        ("road",),  # model has no lane class; road-adjacent emphasis in post-process
    ),
    DisplayCategory("traffic_signs", "Traffic Signs", (220, 120, 60), ("traffic sign",)),
    DisplayCategory("traffic_lights", "Traffic Lights", (70, 70, 120), ("traffic light",)),
    DisplayCategory("buildings", "Buildings", (70, 70, 70), ("building", "wall", "fence")),
    DisplayCategory("sidewalks", "Sidewalks", (244, 35, 232), ("sidewalk",)),
    DisplayCategory("trees", "Trees", (107, 142, 35), ("vegetation", "terrain")),
    DisplayCategory("sky", "Sky", (70, 130, 180), ("sky",)),
)

CITYSCAPES_NAME_TO_DISPLAY: dict[str, str] = {}
for cat in DISPLAY_CATEGORIES:
    for label in cat.cityscapes_labels:
        if cat.key == "lane_markings" and label == "road":
            continue
        CITYSCAPES_NAME_TO_DISPLAY[label] = cat.key


def legend_payload() -> list[dict]:
    return [
        {
            "key": c.key,
            "label": c.label,
            "color_rgb": c.color_rgb,
            "color_hex": "#{:02x}{:02x}{:02x}".format(*c.color_rgb),
        }
        for c in DISPLAY_CATEGORIES
    ]
