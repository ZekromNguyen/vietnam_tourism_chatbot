import os

# Ensure data directory exists
data_dir = "d:\\Tour AI\\data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    print(f"Created directory: {data_dir}")

# Read the content from the existing file if it exists
file_path = os.path.join(data_dir, "vietnam_tourism_guide.txt")
content = ""

try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"Successfully read existing file: {file_path}")
except Exception as e:
    print(f"Could not read existing file: {e}")
    # Use the content from your data
    content = """# Comprehensive Guide to Vietnam Tourism

## Overview
Vietnam is a Southeast Asian country known for its beautiful landscapes, rich history, vibrant culture, and delicious cuisine. The country stretches along the eastern coast of the Indochinese Peninsula and is bordered by China to the north, Laos and Cambodia to the west, and the South China Sea to the east and south.

## Major Tourist Destinations

### Hanoi (Hà Nội)
The capital city of Vietnam, Hanoi is over 1000 years old and features a unique blend of Eastern and Western cultures.

**Famous attractions:**
- Hoan Kiem Lake (Hồ Hoàn Kiếm): A scenic lake in the center with the iconic Turtle Tower.
- Old Quarter (Phố cổ Hà Nội): 36 ancient streets, each named after the goods once sold there.
- Temple of Literature (Văn Miếu): Vietnam's first national university, built in 1070.
- Ho Chi Minh Mausoleum (Lăng Chủ tịch Hồ Chí Minh): Final resting place of Vietnam's revolutionary leader.
- Thang Long Imperial Citadel (Hoàng thành Thăng Long): UNESCO World Heritage site.
- West Lake (Hồ Tây): The largest lake in Hanoi with many temples around its shores."""

# Write the content to the file with UTF-8 encoding
try:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully wrote to file: {file_path}")
except Exception as e:
    print(f"Error writing to file: {e}")