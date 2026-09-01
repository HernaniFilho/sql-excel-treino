import random
import sqlite3

import pandas as pd
from faker import Faker

conn = sqlite3.connect(":memory:")
_ = conn.execute("PRAGMA foreign_keys = ON;")
cursor = conn.cursor()
fake = Faker("pt_BR")


def create_tables() -> None:
    print("\nCriando tabelas!")
    try:
        _ = cursor.execute("""CREATE TABLE servidores (
                id INTEGER PRIMARY KEY,
                nome TEXT,
                cargo TEXT,
                lotacao TEXT
            );
            """)

        _ = cursor.execute("""CREATE TABLE processos (
                id INTEGER PRIMARY KEY,
                servidor_id INTEGER,
                tipo TEXT,
                status TEXT,
                data_abertura DATE,
                FOREIGN KEY (servidor_id) REFERENCES servidores(id)
            );
            """)

        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Erro Operacional no SQLite: {e}")
    except sqlite3.Error as e:
        print(f"Erro genérico do banco de dados: {e}")

    print("\nTabelas criadas!")


def create_data(num_servidores: int = 10, num_processos: int = 25) -> None:
    print("\nCriando dados para as tabelas!")
    CARGOS = ["Analista", "Tecnico", "Assessor"]
    LOTACOES = ["STI", "Corregedoria", "SGE", "Secretaria-Geral"]
    TIPOS_PROCESSO = ["Sindicância", "Processo Administrativo Disciplinar", "Correição"]
    STATUS = ["Em andamento", "Concluído", "Arquivado", "Suspenso"]

    servidores_dados = []
    for i in range(num_servidores):
        servidores_dados.append(
            (i, fake.name(), random.choice(CARGOS), random.choice(LOTACOES))
        )

    processos_dados = []
    for i in range(num_processos):
        processos_dados.append(
            (
                i,
                random.randint(0, num_servidores - 1),
                random.choice(TIPOS_PROCESSO),
                random.choice(STATUS),
                str(fake.date_between(start_date="-1y", end_date="today")),
            )
        )

    try:
        _ = cursor.executemany(
            "INSERT INTO servidores (id, nome, cargo, lotacao) VALUES (?, ?, ?, ?)",
            servidores_dados,
        )

        _ = cursor.executemany(
            "INSERT INTO processos (id, servidor_id, tipo, status, data_abertura) VALUES (?, ?, ?, ?, ?)",
            processos_dados,
        )
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Erro Operacional no SQLite: {e}")
    except sqlite3.Error as e:
        print(f"Erro genérico do banco de dados: {e}")

    print("\nDados criados!")


def basic_operation() -> None:
    print("\nTestando operações!")
    try:
        query = """SELECT
            s.id AS servidor_id,
            s.nome,
            s.cargo,
            s.lotacao,
            p.id AS processo_id,
            p.tipo,
            p.status,
            p.data_abertura
            FROM servidores s
            JOIN processos p ON s.id = p.servidor_id;
            """
        df = pd.read_sql_query(query, conn)
        df.to_csv(
            "processos_por_servidor.csv", index=False, sep=";", encoding="utf-8-sig"
        )

        query = """SELECT lotacao, COUNT(*) as total_processos
            FROM processos p
            JOIN servidores s ON s.id = p.servidor_id
            GROUP BY s.lotacao;
            """
        df = pd.read_sql_query(query, conn)
        df.to_csv(
            "total_processos_por_lotacao.csv",
            index=False,
            sep=";",
            encoding="utf-8-sig",
        )

    except sqlite3.OperationalError as e:
        print(f"Erro Operacional no SQLite: {e}")
    except sqlite3.Error as e:
        print(f"Erro genérico do banco de dados: {e}")

    print("\nOperações feitas!")


def export_all_tables() -> None:
    print("\nExportando todas as tabelas!")
    try:
        df_servidores = pd.read_sql_query(
            "SELECT id AS servidor_id, nome, cargo, lotacao FROM servidores;", conn
        )
        df_servidores.to_csv(
            "servidores.csv", index=False, sep=";", encoding="utf-8-sig"
        )

        df_processos = pd.read_sql_query(
            "SELECT id AS processo_id, servidor_id, tipo, status, data_abertura FROM processos;",
            conn,
        )
        df_processos.to_csv("processos.csv", index=False, sep=";", encoding="utf-8-sig")
    except sqlite3.OperationalError as e:
        print(f"Erro Operacional no SQLite: {e}")
    except sqlite3.Error as e:
        print(f"Erro genérico do banco de dados: {e}")

    print("\nExportacao concluida!")


def main() -> None:
    create_tables()
    create_data()
    basic_operation()
    export_all_tables()
    conn.close()
    print("\nPrograma finalizado!")


if __name__ == "__main__":
    main()
