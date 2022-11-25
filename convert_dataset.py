import csv

with open("abcnews-date-text.csv") as f:
    with open("dataset.txt", "w") as dataset:
        reader = csv.reader(f)

        dataset.writelines([row[1] + "\n" for row in reader if row[1] != "headline_text"])

print("Write complete")

with open("dataset.txt", "r") as f:
    read = f.read()
    print("Lines: " + str(len(read.split("\n"))))

    amount_of_words = len(read.replace("\n", " ").split(" "))
    print("Words: " + str(amount_of_words))