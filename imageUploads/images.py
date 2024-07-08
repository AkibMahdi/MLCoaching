import openai
import requests
import os

# Set your OpenAI API key
api_key = 'sk-your-api-key-here'

openai.api_key = api_key

def generate_image(prompt, n=1, size='1024x1024'):
    response = openai.Image.create(
        prompt=prompt,
        n=n,
        size=size
    )
    return response['data']

def save_image(url, file_path):
    response = requests.get(url)
    with open(file_path, 'wb') as file:
        file.write(response.content)

def generator(prompt_dynamic, n_dynamic=1, size_dynamic='1024x1024'):
    images = generate_image(prompt_dynamic, n_dynamic, size_dynamic)

    output_dir = 'generated_images'
    os.makedirs(output_dir, exist_ok=True)

    file_paths = []
    for i, image_info in enumerate(images):
        image_url = image_info['url']
        file_path = os.path.join(output_dir, f'image_{i+1}.png')
        save_image(image_url, file_path)
        file_paths.append(file_path)
        print(f"Saved image {i+1} to {file_path}")

    return file_paths

# Example usage
if __name__ == '__main__':
    # Dynamic parameters
    prompt_dynamic = "A futuristic city skyline at sunset"
    n_dynamic = 2
    size_dynamic = '1024x1024'

    # Generate and save images
    saved_images = generator(prompt_dynamic, n_dynamic, size_dynamic)
    print(f"Images saved: {saved_images}")
