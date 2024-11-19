import asyncio
import os

from dotenv import load_dotenv
from runware import IImageInference, Runware, 

load_dotenv()

RUNWARE_API_KEY = os.getenv("RUNWARE_API_KEY")


async def main() -> None:
    runware = Runware(api_key=RUNWARE_API_KEY)
    await runware.connect()
    request_image = IImageInference(
        positivePrompt="RAW photo of a modern parametric building in the city, tower building, other huge modern office buildings, urban city at background, public square, glass windows with frames, early morning view, cinematic shot, architectural photo, 8k, film grain, high quality",
        model="civitai:139562@344487", #RealVisXL V4.0 V4.0 (BakedVAE)
        numberResults=1,
        negativePrompt="cloudy, rainy",
        height=832,
        width=1216,
    )
    images = await runware.imageInference(requestImage=request_image)
    for image in images:
        print(f"Image URL: {image.imageURL}")


if __name__ == "__main__":

    asyncio.run(main())
