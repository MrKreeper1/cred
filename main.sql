--
-- ���� ������������ � ������� SQLiteStudio v3.4.3 � �� ��� 23 23:16:58 2023
--
-- �������������� ��������� ������: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- �������: credits
CREATE TABLE IF NOT EXISTS credits (cred_id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT NOT NULL, num INTEGER NOT NULL DEFAULT (1), start_date DATE, finish_date DATE, "desc" TEXT, status NUMBER NOT NULL DEFAULT (1));
INSERT INTO credits (cred_id, user, num, start_date, finish_date, "desc", status) VALUES (1, 'admin', 1, NULL, NULL, NULL, 1);
INSERT INTO credits (cred_id, user, num, start_date, finish_date, "desc", status) VALUES (2, 'admin', 1, NULL, NULL, NULL, 1);

-- �������: users
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, surname TEXT NOT NULL, class TEXT NOT NULL, login TEXT NOT NULL, password TEXT NOT NULL, balance INTEGER NOT NULL DEFAULT (0), privilege INTEGER DEFAULT (1));
INSERT INTO users (id, name, surname, class, login, password, balance, privilege) VALUES (1, '������', '�������', '8�', 'admin', 'qwerty123', 0, 2);
INSERT INTO users (id, name, surname, class, login, password, balance, privilege) VALUES (2, '������', '������', '8�', 'VictorS', 'victor_ass9999', 0, 1);
INSERT INTO users (id, name, surname, class, login, password, balance, privilege) VALUES (3, '����', '�������', '8�', 'Ivan', '12345', 0, 1);
INSERT INTO users (id, name, surname, class, login, password, balance, privilege) VALUES (4, '����', '��������', '1�', 'test', 'test', 0, 1);
INSERT INTO users (id, name, surname, class, login, password, balance, privilege) VALUES (5, 'name', 'default', '0A', 'default', 'default', 0, 1);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
