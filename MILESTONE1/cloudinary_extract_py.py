

import cloudinary
import cloudinary.api

# Configure Cloudinary
cloudinary.config(
    cloud_name="deg42enyf",  # Replace with your Cloud Name
    api_key="942296943917836",  # Replace with your API Key
    api_secret="sw3uVuzO4jxc8sEo4KWB1rk5p24"  # Replace with your API Secret
)

def fetch_all_images():
    try:
        # Initialize a list to store all image URLs
        all_images = []
        next_cursor = None

        # Loop to handle pagination
        while True:
            # Fetch images with pagination support
            if next_cursor:
                resources = cloudinary.api.resources(type="upload", next_cursor=next_cursor)
            else:
                resources = cloudinary.api.resources(type="upload")

            # Append the images from the current page to the list
            all_images.extend(resources.get('resources', []))

            # Check if there is another page
            next_cursor = resources.get('next_cursor')
            if not next_cursor:
                break  # Exit the loop if no more pages are available

        return all_images
    except cloudinary.api.Error as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    images = fetch_all_images()
    if images:
        print(f"Total Images Found: {len(images)}")
        print("Uploaded Images:")
        for resource in images:
            print(f"Public ID: {resource['public_id']}, URL: {resource['url']}")
    else:
        print("No images found or an error occurred.")