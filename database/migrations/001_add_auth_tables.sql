-- 001_add_auth_tables.sql
-- WildGuard AI 회원가입/로그인 및 예측 로그 사용자 연결용 DB 변경

-- USERS 테이블
CREATE TABLE users (
    user_id NUMBER PRIMARY KEY,
    username VARCHAR2(50) UNIQUE NOT NULL,
    password_hash VARCHAR2(255) NOT NULL,
    name VARCHAR2(50) NOT NULL,
    organization VARCHAR2(100),
    role VARCHAR2(30) DEFAULT 'citizen',
    created_at DATE DEFAULT SYSDATE
);

-- USERS 시퀀스
CREATE SEQUENCE users_seq
START WITH 1
INCREMENT BY 1
NOCACHE;

-- USERS 트리거
CREATE OR REPLACE TRIGGER trg_users
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    IF :NEW.user_id IS NULL THEN
        SELECT users_seq.NEXTVAL
        INTO :NEW.user_id
        FROM dual;
    END IF;
END;
/

-- 예측 로그 테이블에 user_id 추가
ALTER TABLE risk_prediction_log
ADD user_id NUMBER;