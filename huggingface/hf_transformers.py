# This function is a high-level, easy-to-use API for performing various tasks with transformer models, such as text classification, named entity recognition, and sentiment analysis.
from transformers import pipeline

# Creating the Sentiment Analysis Pipeline: This means that the pipeline will use a default model for sentiment analysis.
classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions")

response = classifier("I'm sad that pavan encountered a bug")

print(response)