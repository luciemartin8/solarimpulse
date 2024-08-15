import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('insert.csv file here')

cm = confusion_matrix(df['EXISTING_RELEVANCY'], df['PREDICTED_RELEVANCY'])
report = classification_report(df['EXISTING_RELEVANCY'], df['PREDICTED_RELEVANCY'])
print("Confusion Matrix")
print(cm)
print("\nClassification Report:")
print(report)



plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.show()