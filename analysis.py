import nltk
import pandas
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
import numpy as np

# nltk.download('stopwords')

joke = "Whats brown and sticky? A stick"

jokes = pandas.read_json("stupidstuff.json")

commonwords = [e.upper() for e in set(nltk.corpus.stopwords.words('english'))] # <- Need to download the corpus: import nltk; nltk.download()

tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')  # To be able to strip out unwanted things in strings
def string_to_list(x):
    return [el.upper() for el in tokenizer.tokenize(x) if el.upper() not in commonwords]

jokes["joketoken"] = jokes["body"].apply(string_to_list)
joke = string_to_list(joke)
# print(jokes["joketoken"])

def get_words():
    words = []
    for jk in jokes['joketoken']:
        words.extend(jk)
    return words

all_words = get_words()

def extract_features(joke, all_words):
    words = set(joke)
    features = {}
    for word in words:
        features['contains(%s)' % word] = (word in all_words)
    return features

def sigmoid(z): 
    '''
    Input:
        z: is the input (can be a scalar or an array)
    Output:
        h: the sigmoid of z
    '''
    # calculate the sigmoid of z
    h = 1/(1 + np.exp(-z))
    
    return h

jokes['features'] = jokes['joketoken'].apply(lambda x:extract_features(x, all_words))

funny_threshhold = 3.0

jokes["rating"] = jokes["rating"].apply(float)
jokes["funny"] = jokes["rating"] >= funny_threshhold

jokes["labeled_feature"] = list(zip(jokes["features"], jokes["funny"]))

# print(jokes.head(5))

# classifier = nltk.NaiveBayesClassifier.train(jokes["labeled_feature"])

# for label in classifier.labels():
#   print(f'\n\n{label}:')
#   for (fname, fval) in classifier.most_informative_features(50):
#     print(f"   {fname}({fval}): ", end="")
#     print("{0:.2f}%".format(100*classifier._feature_probdist[label, fname].prob(fval)))

# nltk.classify.util.

# classifier.show_most_informative_features(10)

joke = 'Why was 10 afraid of 7? Because 7 8 9 France Girl'
# print(classifier.prob_classify(extract_features(string_to_list(joke), all_words)).samples)

# temp = classifier.prob_classify(extract_features(string_to_list(joke), all_words))
# print(list(temp.samples()))
# print(temp.prob("True"))
# print(temp.prob("False"))

# print(jokes["labeled_feature"])

# print(jokes["funny"])

x = jokes["body"]
y = jokes["funny"]

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 42)

vectorizer = CountVectorizer()
x_train_vec = vectorizer.fit_transform(x_train)
x_test_vec = vectorizer.transform(x_test)
modal = LogisticRegression(max_iter=500)
modal.fit(x_train_vec, y_train)

y_pred = modal.predict(x_test_vec)
accuracy = accuracy_score(y_test, y_pred)
print("accuracy", accuracy)
Report = classification_report(y_test, y_pred)
print(Report)

new_joke = ["a sentence is here FRANCE"]
new_joke_vec = vectorizer.transform(new_joke)
pred_sentiment = modal.predict_proba(new_joke_vec)
print("Predictful sentiment",pred_sentiment)
pred_sentiment = modal.predict(new_joke_vec)
print("Predictful sentiment",pred_sentiment)