from PIL import Image, ImageDraw, ImageFont


image = Image.new(
    "RGB",
    (1200, 600),
    "white"
)

draw = ImageDraw.Draw(image)

try:
    font = ImageFont.truetype(
        "arial.ttf",
        48
    )
except OSError:
    font = ImageFont.load_default()


text = (
    "Document Intelligence System\n"
    "Revenue: Rs 12 crore\n"
    "Growth: 18 percent\n"
    "Project Status: Active"
)


draw.multiline_text(
    (50, 50),
    text,
    fill="black",
    font=font,
    spacing=30
)

image.save(
    "data/input/test_image.png"
)

print("Test image created successfully.")