import csv
from app.models import SourceCodeSmell
from app.repository.database import DataBase


def insert_into_tb_source_code_smell(csv_source_path: str) -> None:
    print("inserting...")
    with open(csv_source_path, newline='', encoding='utf-8') as arquivo_csv:
        result = csv.reader(arquivo_csv, delimiter=';')
        for index, row in enumerate(result):
            if index != 0:
                data = SourceCodeSmell(
                    id_base=int(row[0]),
                    reviewer_id=int(row[1]),
                    sample_id=int(row[2]),
                    smell=row[3],
                    severity=row[4],
                    review_timestamp=row[5],
                    type=row[6],
                    code_name=row[7],
                    repository=row[8],
                    commit_hash=row[9],
                    path=row[10],
                    start_line=int(row[11]),
                    end_line=int(row[12]),
                    link=row[13],
                    is_from_industry_relevant_project=float(str(row[14]).replace(",", "."))
                )
                DataBase.insert_source_code_smell(data)


if __name__ == '__main__':
    insert_into_tb_source_code_smell("source.csv")
