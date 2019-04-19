import csv


class ScoreScreen:

    def score_read(self):
        with open('scores.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                line_count += 1
            if row:
                return row[0] + " -> " + row[1]


    def score_save(self, username, score):
        with open('scores.csv', mode='w') as scores:
            if score > row[1]:
                employee_writer = csv.writer(scores, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                employee_writer.writerow([username, score])

