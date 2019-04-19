import csv


class ScoreScreen:

    def score_read(self):
        with open('scores.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                line_count += 1
            if row:
                print("Name: " + row[0] + " Score: " + row[1])
                return row[0] + row[1]


    def score_save(self, username, score):
        with open('scores.csv', mode='w') as scores:
            print("Saving score....")
            employee_writer = csv.writer(scores, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            employee_writer.writerow([username, score])

