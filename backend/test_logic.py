
potential = "https://allevents.in/img/og-logo.jpg"
p_list = ["og-logo", "logo.jpg", "logo.png", "placeholder", "blank.gif", "data:image"]

print(f"Potential: {potential}")
is_logo = any(p in potential.lower() for p in p_list)
print(f"Any match? {is_logo}")
if "http" in potential and not is_logo:
    print("MATCH! (Setting as event image)")
else:
    print("NO MATCH (Skipping)")
