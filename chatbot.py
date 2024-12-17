import json
import nltk
import random
import pickle
import numpy as np 
import tensorflow as tf
from nltk.stem.lancaster import LancasterStemmer
from tensorflow import keras
from tensorflow.keras import layers

#Initializing Lancaster Stemmer
stemmer = LancasterStemmer()

#Loading dataset
with open('dataset/dataset.json') as file:
	data = json.load(file)

with open('data.pickle', 'rb') as f:
    words, labels = pickle.load(f)


# Build the model using TensorFlow Keras
model = keras.Sequential([
    layers.Input(shape=(len(words),)),
    layers.Dense(128, activation='relu'),
    layers.Dense(64, activation='relu'),  # Changed from 128 to 64
    layers.Dense(len(labels), activation='softmax')
])

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Load weights if available
model.load_weights('models/chatbot-model.h5')


def bag_of_words(s, words):

	bag = [0 for _ in range(len(words))]

	s_words = nltk.word_tokenize(s)
	s_words = [stemmer.stem(word.lower()) for word in s_words]

	for se in s_words:
		for i, w in enumerate(words):
			if(w == se):
				bag[i] = 1

	return np.array(bag)


def chat(inputText):

	print('[INFO] Start talking...(type quit to exit)')
	
	while True:

		inp = inputText

		#Type quit to exit
		if inp.lower() == 'quit':
			break

			# Predict the input sentence tag
		predict = model.predict(np.array([bag_of_words(inp, words)]))
		predictions = np.argmax(predict)
		
		tag = labels[predictions]
		#Printing response
		for t in data['intents']:
			#print(t['tag'])
			if t['tag'] == tag:
				responses = t['responses']
				
		outputText = random.choice(responses)		
		return outputText
