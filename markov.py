from random import choice
import math
import time
from numba import jit, njit


class MarkovGenerator():
    def __init__(self, file_path, limit):
        self.file_path = file_path

        self.dataset = self.read_file(limit)

        print("Training")
        self.model = self.train(self.dataset)

        self.pickingCache = {}

    def read_file(self, limit):
        outputLines = []

        notifInterval = math.floor(limit / 20)
        lastInterval = 0

        with open(self.file_path, "r") as f:
            lines = f.readlines()

            if not limit:
                limit = len(lines)

            for line in lines[:limit]:
                outputLines.append(["__START__"] + line.replace("\n", "").split(" ") + ["__END__"])

                if len(outputLines) > lastInterval + notifInterval:
                    lastInterval = len(outputLines)
                    percentage = math.floor(100 * (len(outputLines) / limit))
                    print(str(percentage) + "% loaded file")

        return outputLines

    def train(self, dataset):
        words = {}

        for entry in dataset:
            for current_word, next_word in zip(entry[0:-1], entry[1:]):
                if not words.get(current_word):
                    words[current_word] = {}

                if not words[current_word].get(next_word):
                    words[current_word][next_word] = 1
                else:
                    words[current_word][next_word] += 1

        return words

    def generate(self, first_word):
        if self.model.get(first_word):
            word = first_word
            output = []

            while True:
                output.append(word)
                newword = None

                iterations = 0

                while newword == None or (newword == "__END__" and len(output) < 3) or newword == word:
                    newword, typeOf = self.random_next(word)
                    iterations = iterations + 1
                    if iterations > 3:
                        print("Retrying: " + str(iterations))

                    if iterations > 30:
                        break

                if iterations > 30:
                    print("Failed to find valid completion")
                    return output

                word = newword

                print(format(len(output), "02d") + " : " + typeOf + " : " + word)

                if word == "__END__":
                    print("")
                    return output

        else:
            return ["Word", "not", "in", "corpus"]

    def random_next(self, last):
        probabilities = self.model[last]
        pickingArray = []
        typeOf = None

        if self.pickingCache.get(last):
            typeOf = "Cache    "
            pickingArray = self.pickingCache[last]
        else:
            typeOf = "Generated"
            for word, count in probabilities.items():
                pickingArray = pickingArray + ([word] * count)

            self.pickingCache[last] = pickingArray

        return choice(pickingArray), typeOf

    def pregenerate(self, timeAllowed):
        if timeAllowed == "Hardcoded":
            # hardcoded mode
            phrases = ["for", "to", "when", "covid", "coronavirus", "american", "british", "french", "the", "over",
                       "at", "with", "on", "in", "a", "afghan", "afghanistan", "iraq", "iraqi", "trump", "obama",
                       "biden", "US", "police", "removal"]

            for phrase in phrases:
                for i in range(1, 3):
                    print(phrase)
                    self.generate(phrase)

        elif timeAllowed == "Smart":
            self.pregenerate("Hardcoded")

            samples = []

            while True:
                word = choice(list(self.model.keys()))
                if word == "__START__":
                    continue
                print("Pregenning with word: " + word)
                startTime = time.time()
                self.generate(word)
                samples.append(time.time() - startTime)

                if len(samples) > 20:
                    del samples[0]

                avgTime = 0
                for i in samples:
                    avgTime += i

                avgTime = avgTime / len(samples)

                if avgTime < 0.2 and len(samples) > 15:
                    break

                print(avgTime)
        else:
            starttime = time.time()

            while starttime + timeAllowed > time.time():
                word = choice(list(self.model.keys()))
                print("Pregenning with word: " + word)
                self.generate(word)

                amountThrough = time.time() - starttime

                percentage = (amountThrough / timeAllowed) * 100

                print("\n" + str(percentage) + "%\n")


if __name__ == "__main__":
    generator = MarkovGenerator("dataset.txt", int(1244185/1))

    print("Ready to receive input")

    while True:
        prompt = input("> ")

        if prompt.split(" ")[0] == "!pregen-r":
            try:
                amount = int(prompt.split(" ")[1])
            except:
                print("Invalid: Please enter a number")
                continue

            generator.pregenerate(amount)

            print("Done!\n\n\n\n")

            continue

        if prompt.split(" ")[0] == "!pregen-h":
            generator.pregenerate("Hardcoded")

            print("Done!\n\n\n\n")

            continue

        if prompt.split(" ")[0] == "!pregen-s":
            generator.pregenerate("Smart")

            print("Done!\n\n\n\n")

            continue

        lastWord = prompt.split(" ")[-1].lower()

        output = generator.generate(lastWord)

        if len(prompt.split(" ")) == 1:
            output[0] = output[0].capitalize()
            print(" ".join(output))

        else:
            prompt = prompt.split(" ")
            prompt[0] = prompt[0].capitalize()

            print(" ".join(prompt) + " " + " ".join(output[1:]))
