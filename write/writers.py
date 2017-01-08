import csv

def write(records):
	with open("files/Avito.csv", 'w') as f:
		writer = csv.writer(f)
		writer.writerow(["Имя", "Дата публикации", "Цена", "Описание", "Ссылка"])
		for record in sorted(records, key=lambda rec: rec["raiting"]):
			writer.writerow([record["name"], record["publication_time"], record["price"], record["title"], record["link"]])
		f.close()

def writeText(records):
	with open("files/Avito.txt", 'w') as f:
		for record in records:
			for key in record:
				f.write("{0}: {1}".format(key, record[key]))
				f.write('\n')
			f.write('\n\n')
		f.close()