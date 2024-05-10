# This function is a high-level, easy-to-use API for performing various tasks with transformer models, such as text classification, named entity recognition, and sentiment analysis.
from transformers import pipeline

# Creating the Sentiment Analysis Pipeline: This means that the pipeline will use a default model for sentiment analysis.
classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions")

response = classifier("I'm sad that pavan encountered a bug")

print(response)













'''
Default Model: The default model used here is distilbert/distilbert-base-uncased-finetuned-sst-2-english, 
which is a version of the DistilBERT model fine-tuned on the SST-2 dataset for English sentiment analysis. 
The revision af0f99b is specified, which refers to a specific version of the model.

Downloading Model and Tokenizer Files: When you run this code, the Transformers library automatically downloads the necessary files for the model and tokenizer. 

This includes:

config.json: This file contains the configuration settings for the model. It specifies the architecture, hyperparameters, and other settings.

model.safetensors: This is the actual model weights file. It contains the parameters that the model has learned during training.

tokenizer_config.json: This file contains the configuration settings for the tokenizer. It specifies how text should be preprocessed before being fed into the model.

vocab.txt: This file contains the vocabulary that the tokenizer uses to convert text into tokens that the model can understand.

'''