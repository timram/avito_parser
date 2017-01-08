import csv

def write(records):
	with open("files/Avito.csv", 'w') as f:
		writer = csv.writer(f)
		writer.writerow(["Имя", "Дата публикации", "Цена", "Описание", "Ссылка"])
		for record in sorted(records, key=lambda rec: rec["raiting"]):
			writer.writerow([record["name"], record["publication_time"], record["price"], record["title"], record["link"]])
		f.close()