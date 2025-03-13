from transformers import TrOCRProcessor, VisionEncoderDecoderModel, VisionEncoderDecoderConfig
from PIL import Image
from glob import glob

modelName = "trocrOriginal"
modelPath = f"./pretrained/{modelName}/processor"
procPath = f"./pretrained/{modelName}/model"


# cache processor and model to local system
# processor = TrOCRProcessor.from_pretrained('openthaigpt/thai-trocr')
# model = VisionEncoderDecoderModel.from_pretrained('openthaigpt/thai-trocr')
# processor.save_pretrained(procPath)
# model.save_pretrained(modelPath)

# load model
processor = TrOCRProcessor.from_pretrained(procPath)
encoder_decoder_config = VisionEncoderDecoderConfig.from_pretrained(modelPath)
model = VisionEncoderDecoderModel.from_pretrained(modelPath, config=encoder_decoder_config)

# # # Load an image
for path in glob('./imageForTesting/*.png'):
    image = Image.open(path).convert("RGB")

    # # # Process and generate text
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print(generated_text)