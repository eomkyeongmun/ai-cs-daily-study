---
date: 2026-05-21
category: 백엔드 - 데이터베이스
topic: RDBMS 기초
subtopic: ACID 특성, 트랜잭션 격리 수준과 이상 현상(Dirty Read 등)
tags: [CS, 백엔드---데이터베이스, study]
---

# RDBMS 기초 - ACID 특성, 트랜잭션 격리 수준과 이상 현상(Dirty Read 등)

## 핵심 개념

RDBMS(Relational Database Management System)는 데이터를 테이블, 행, 열의 관계형 구조로 저장하고 SQL을 통해 조회·수정하는 데이터베이스 관리 시스템이다. RDBMS에서 가장 중요한 개념 중 하나가 **트랜잭션(Transaction)** 이다. 트랜잭션은 논리적으로 하나의 작업 단위로 묶인 데이터베이스 연산들의 집합이며, 성공하면 모두 반영되고 실패하면 모두 취소되어야 한다.

트랜잭션이 신뢰성 있게 동작하기 위해 만족해야 하는 대표적인 성질이 **ACID**이다.

- **Atomicity, 원자성**
  - 트랜잭션의 모든 연산은 전부 성공하거나 전부 실패해야 한다.
  - 예: 계좌 A에서 출금하고 계좌 B에 입금하는 작업 중 입금이 실패하면 출금도 취소되어야 한다.

- **Consistency, 일관성**
  - 트랜잭션 수행 전후에 데이터베이스는 정의된 제약 조건, 무결성 규칙, 비즈니스 규칙을 만족해야 한다.
  - 예: 잔액은 음수가 될 수 없다는 제약이 있다면 트랜잭션 후에도 이를 만족해야 한다.

- **Isolation, 격리성**
  - 동시에 실행되는 트랜잭션들이 서로에게 부정확한 중간 상태를 노출하지 않아야 한다.
  - 격리 수준에 따라 동시성과 정합성의 균형이 달라진다.

- **Durability, 지속성**
  - 커밋된 트랜잭션의 결과는 시스템 장애가 발생하더라도 보존되어야 한다.
  - 일반적으로 WAL, redo log, fsync, 체크포인트 등의 메커니즘과 관련된다.

ACID가 중요한 이유는 데이터베이스가 단순 저장소가 아니라 **정확한 상태 전이를 보장하는 시스템**이기 때문이다. 특히 금융, 주문, 재고, 예약, 결제 시스템에서는 일부 데이터만 반영되거나 동시에 실행된 트랜잭션 때문에 잘못된 결과가 발생하면 심각한 장애로 이어질 수 있다.

트랜잭션 격리 수준은 ACID 중 **Isolation**을 얼마나 강하게 보장할지 결정하는 기준이다. SQL 표준에서는 대표적으로 다음 격리 수준을 정의한다.

1. **Read Uncommitted**
2. **Read Committed**
3. **Repeatable Read**
4. **Serializable**

격리 수준이 낮을수록 동시성은 높아질 수 있지만, Dirty Read, Non-repeatable Read, Phantom Read 같은 이상 현상이 발생할 가능성이 커진다. 반대로 격리 수준이 높을수록 데이터 정합성은 강해지지만 락 경합, 대기, 데드락, 성능 저하가 발생할 수 있다.

---

---

## 내부 동작 원리

트랜잭션은 보통 다음 흐름으로 처리된다.

```text
BEGIN
  SQL 실행 1
  SQL 실행 2
  SQL 실행 3
COMMIT 또는 ROLLBACK
```

예를 들어 계좌 이체 트랜잭션은 다음과 같다.

```sql
BEGIN;

UPDATE account
SET balance = balance - 10000
WHERE id = 'A';

UPDATE account
SET balance = balance + 10000
WHERE id = 'B';

COMMIT;
```

만약 두 번째 UPDATE가 실패하면 ROLLBACK을 통해 첫 번째 UPDATE도 되돌려야 한다. 이것이 원자성이다.

## ACID 내부 구현 개념

### 1. Atomicity와 Undo

원자성은 일반적으로 **Undo 로그** 또는 그와 유사한 복구 정보를 통해 구현된다.

```text
[트랜잭션 시작]
   ↓
[변경 전 데이터 기록: Undo 정보]
   ↓
[데이터 변경]
   ↓
성공 → COMMIT
실패 → Undo 정보로 ROLLBACK
```

예를 들어 balance가 10000에서 5000으로 변경되었다면, 롤백을 위해 이전 값 10000을 기록해 둔다.

### 2. Durability와 Redo / WAL

지속성은 일반적으로 **Write-Ahead Logging, WAL** 원칙과 관련된다. WAL은 실제 데이터 페이지를 디스크에 반영하기 전에 로그를 먼저 안정적인 저장소에 기록하는 방식이다.

```text
트랜잭션 변경 발생
   ↓
로그 버퍼에 변경 내용 기록
   ↓
COMMIT 시 로그를 디스크에 flush
   ↓
이후 데이터 페이지는 적절한 시점에 디스크 반영
```

장애 발생 시 데이터 파일에 일부 변경만 반영되었더라도, redo 로그를 사용해 커밋된 변경을 재적용할 수 있다.

### 3. Isolation과 락 / MVCC

격리성은 주로 다음 두 방식 또는 조합으로 구현된다.

- **Lock 기반 동시성 제어**
  - 읽기 락, 쓰기 락, 행 락, 테이블 락 등을 사용한다.
  - 충돌 가능성이 있는 작업을 대기시킨다.

- **MVCC, Multi-Version Concurrency Control**
  - 데이터의 여러 버전을 유지하여 읽기 작업이 쓰기 작업을 막지 않도록 한다.
  - 트랜잭션은 특정 시점의 스냅샷을 읽는다.
  - PostgreSQL, MySQL InnoDB 등 주요 RDBMS에서 사용된다.
  - 단, 구현 세부 사항과 격리 수준별 동작은 DBMS마다 다르다.

## 트랜잭션 이상 현상

### 1. Dirty Read

아직 커밋되지 않은 다른 트랜잭션의 변경 내용을 읽는 현상이다.

```text
T1: UPDATE account SET balance = 0 WHERE id = 'A';  -- 아직 COMMIT 안 함
T2: SELECT balance FROM account WHERE id = 'A';     -- 0을 읽음
T1: ROLLBACK;
```

T2는 실제로 존재하지 않게 된 값을 읽은 셈이다.

### 2. Non-repeatable Read

한 트랜잭션 안에서 같은 행을 두 번 읽었는데, 중간에 다른 트랜잭션이 커밋하여 값이 달라지는 현상이다.

```text
T1: SELECT balance FROM account WHERE id = 'A';  -- 10000
T2: UPDATE account SET balance = 5000 WHERE id = 'A';
T2: COMMIT;
T1: SELECT balance FROM account WHERE id = 'A';  -- 5000
```

T1 입장에서는 같은 트랜잭션 내부에서 동일한 조회 결과가 반복되지 않는다.

### 3. Phantom Read

한 트랜잭션 안에서 같은 조건으로 범위 조회를 두 번 했는데, 중간에 다른 트랜잭션이 행을 삽입 또는 삭제하여 결과 집합의 행 개수가 달라지는 현상이다.

```text
T1: SELECT * FROM orders WHERE amount >= 10000;  -- 10건
T2: INSERT INTO orders(amount) VALUES (20000);
T2: COMMIT;
T1: SELECT * FROM orders WHERE amount >= 10000;  -- 11건
```

### 4. Lost Update

두 트랜잭션이 같은 데이터를 읽고 각각 수정한 뒤, 한쪽의 변경이 다른 쪽에 의해 덮어써지는 현상이다.

```text
초기값: stock = 10

T1: stock 읽음 → 10
T2: stock 읽음 → 10
T1: stock = 9로 UPDATE
T2: stock = 9로 UPDATE

결과: 실제로는 2개가 차감되어야 하지만 stock은 9
```

SQL 표준의 대표 이상 현상 분류에는 Dirty Read, Non-repeatable Read, Phantom Read가 자주 언급되며, Lost Update는 실무에서 매우 중요한 동시성 문제로 다뤄진다.

## 격리 수준별 일반적 특성

DBMS별 구현 차이가 있으므로 아래는 일반적인 설명이다.

| 격리 수준 | Dirty Read | Non-repeatable Read | Phantom Read | 설명 |
|---|---:|---:|---:|---|
| Read Uncommitted | 가능 | 가능 | 가능 | 커밋되지 않은 데이터 읽기 가능 |
| Read Committed | 방지 | 가능 | 가능 | 커밋된 데이터만 읽음 |
| Repeatable Read | 방지 | 방지 | DBMS별 차이 | 같은 행 반복 읽기 보장 |
| Serializable | 방지 | 방지 | 방지 | 직렬 실행과 같은 결과 보장 |

⚠️ 확인 필요: 특정 DBMS의 특정 버전에서는 위 표와 다른 동작을 보일 수 있다. 예를 들어 MySQL InnoDB의 Repeatable Read는 MVCC와 next-key lock 등으로 일부 phantom 문제를 방지할 수 있지만, 쿼리 형태와 락 사용 방식에 따라 동작이 달라질 수 있다.

## 다이어그램 설명

```text
동시 트랜잭션 처리 구조

Client A ── SQL ──┐
                  │
Client B ── SQL ──┼── Transaction Manager
                  │          │
Client C ── SQL ──┘          │
                             ↓
                     Concurrency Control
                     ├─ Lock Manager
                     ├─ MVCC Snapshot
                     └─ Deadlock Detection
                             ↓
                       Storage Engine
                     ├─ Buffer Pool
                     ├─ Undo Log
                     ├─ Redo/WAL Log
                     └─ Data File
```

- Transaction Manager는 BEGIN, COMMIT, ROLLBACK을 관리한다.
- Concurrency Control은 동시에 접근하는 트랜잭션 사이의 충돌을 제어한다.
- Lock Manager는 행, 인덱스, 테이블 등에 대한 락을 관리한다.
- MVCC Snapshot은 트랜잭션이 읽어야 할 데이터 버전을 결정한다.
- Storage Engine은 실제 데이터 페이지와 로그를 관리한다.

---

---

## 실제 시스템 연결

실제 RDBMS에서는 ACID와 격리 수준이 시스템 안정성과 성능에 직접적인 영향을 준다.

## PostgreSQL

PostgreSQL은 MVCC를 사용한다. 일반적인 SELECT는 읽기 작업이 쓰기 작업을 직접적으로 막지 않도록 동작한다. 각 트랜잭션은 적절한 스냅샷을 기준으로 데이터를 읽는다.

예시:

```sql
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;

SELECT * FROM products WHERE id = 1;

-- 같은 트랜잭션 내에서 다시 조회

SELECT * FROM products WHERE id = 1;

COMMIT;
```

Repeatable Read에서는 트랜잭션 시작 이후의 일관된 스냅샷을 읽는 방식으로 동작한다. 다만 Serializable 격리 수준에서는 동시성 충돌을 감지하여 특정 트랜잭션을 실패시킬 수 있으며, 애플리케이션은 재시도 로직을 준비해야 한다.

## MySQL InnoDB

MySQL의 InnoDB 스토리지 엔진은 트랜잭션, 행 수준 락, MVCC, redo log, undo log를 제공한다. 일반적으로 InnoDB는 MySQL에서 트랜잭션이 필요한 테이블에 널리 사용된다.

예시:

```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
START TRANSACTION;

SELECT stock FROM item WHERE id = 10;

UPDATE item
SET stock = stock - 1
WHERE id = 10;

COMMIT;
```

재고 차감 같은 경우 단순히 SELECT 후 UPDATE를 분리하면 Lost Update 문제가 발생할 수 있다. 따라서 다음과 같이 원자적 UPDATE를 사용하는 것이 더 안전하다.

```sql
UPDATE item
SET stock = stock - 1
WHERE id = 10
  AND stock > 0;
```

이후 영향받은 행 수를 확인하여 재고 차감 성공 여부를 판단한다.

## Linux와 파일 시스템

RDBMS의 지속성은 운영체제와 저장장치에 의존한다. COMMIT 시점에 로그를 디스크에 안전하게 기록하려면 DBMS는 OS의 파일 시스템, 페이지 캐시, 디스크 flush 동작과 상호작용한다.

대표적으로 다음 요소들이 관련된다.

- OS 페이지 캐시
- fsync 또는 fdatasync 계열 시스템 콜
- 디스크 write cache
- 파일 시스템 저널링
- 블록 디바이스와 스토리지 컨트롤러

⚠️ 확인 필요: 특정 DBMS 설정, OS, 파일 시스템, 스토리지 장비에 따라 COMMIT 시점의 실제 내구성 보장 수준은 달라질 수 있다.

## Nginx와 백엔드 서버

Nginx 자체가 RDBMS 트랜잭션을 처리하지는 않지만, API 서버 앞단의 reverse proxy로 사용될 때 트랜잭션 처리 시간과 연결 관리에 영향을 줄 수 있다.

예를 들어 주문 API가 다음 흐름을 가진다고 가정할 수 있다.

```text
Client
  ↓
Nginx
  ↓
Application Server
  ↓
RDBMS Transaction
```

트랜잭션이 오래 유지되면 다음 문제가 발생할 수 있다.

- DB 커넥션 점유 시간 증가
- 락 보유 시간 증가
- API 응답 지연
- Nginx upstream timeout 가능성
- 애플리케이션 스레드 또는 워커 고갈

따라서 트랜잭션 내부에서는 외부 API 호출, 파일 업로드 처리, 긴 계산 작업을 피하는 것이 일반적인 모범 사례다.

---

---

## 클라우드 연결

클라우드 환경에서도 ACID와 트랜잭션 격리 수준은 매우 중요하다. 특히 컨테이너, 오토스케일링, 관리형 데이터베이스를 사용하는 환경에서는 애플리케이션 인스턴스가 여러 개로 늘어나면서 동시성 문제가 더 자주 드러난다.

## Docker

Docker 컨테이너 안에서 애플리케이션과 DB를 실행할 수 있지만, 운영 환경에서는 데이터 영속성을 위해 볼륨을 반드시 고려해야 한다.

```yaml
services:
  db:
    image: postgres
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

컨테이너가 삭제되어도 볼륨에 데이터가 남아야 지속성이 유지된다. 다만 ACID의 Durability는 DBMS 로그, 스토리지 flush, 볼륨 드라이버, 호스트 파일 시스템 등 여러 계층에 영향을 받는다.

## Kubernetes

Kubernetes에서 RDBMS를 직접 운영할 경우 다음 요소가 중요하다.

- StatefulSet
- PersistentVolume
- PersistentVolumeClaim
- StorageClass
- Pod 재시작과 장애 복구
- Readiness Probe
- 백업 및 복구 전략

RDBMS는 상태를 가진 시스템이므로 Stateless 애플리케이션보다 운영 난도가 높다. 트랜잭션 중인 Pod가 종료되면 DBMS는 재시작 시 로그를 기반으로 복구를 수행한다. 커밋되지 않은 트랜잭션은 롤백되고, 커밋된 트랜잭션은 복구되어야 한다.

## AWS RDS / Aurora

AWS RDS는 MySQL, PostgreSQL, MariaDB, Oracle, SQL Server 등 여러 관계형 데이터베이스 엔진을 관리형으로 제공한다. 사용자는 인스턴스, 스토리지, 백업, 복제, 모니터링 등을 관리형 기능으로 활용할 수 있다.

트랜잭션 관점에서 중요한 요소는 다음과 같다.

- 엔진별 격리 수준 설정
- 파라미터 그룹 설정
- 자동 백업과 스냅샷
- Multi-AZ 구성
- 읽기 복제본 사용 시 복제 지연
- 장애 조치 시 커넥션 재연결 처리

읽기 복제본을 사용할 때는 Primary에서 커밋한 데이터가 Replica에서 즉시 보이지 않을 수 있다. 이 경우 애플리케이션에서 read-after-write 일관성을 고려해야 한다.

## GCP Cloud SQL / AlloyDB

GCP Cloud SQL은 MySQL, PostgreSQL, SQL Server용 관리형 관계형 데이터베이스 서비스다. AlloyDB는 PostgreSQL 호환 관리형 데이터베이스 서비스로 제공된다.

트랜잭션 설계 관점에서 중요한 점은 AWS와 유사하다.

- 격리 수준은 DB 엔진의 특성에 따른다.
- 장애 조치 시 애플리케이션 재시도 로직이 필요하다.
- 커넥션 풀 설정이 중요하다.
- 장기 트랜잭션은 vacuum, lock, 복제 지연 등에 영향을 줄 수 있다.

## 클라우드 네이티브 애플리케이션에서 주의할 점

```text
User Request
   ↓
Load Balancer
   ↓
App Pod 1 / App Pod 2 / App Pod 3
   ↓
Connection Pool
   ↓
Managed RDBMS
```

애플리케이션 인스턴스가 여러 개이면 같은 데이터를 동시에 수정할 가능성이 증가한다. 따라서 다음 전략이 필요하다.

- DB 트랜잭션을 최종 정합성 보장의 핵심 경계로 사용
- 낙관적 락 또는 비관적 락 적용
- 재고, 포인트, 잔액 등은 원자적 UPDATE 사용
- Serializable 사용 시 재시도 로직 구현
- 커넥션 풀 크기를 DB 허용 연결 수에 맞게 제한
- 트랜잭션을 짧게 유지

---

---

## 보안 연결

트랜잭션과 격리 수준은 보안과도 연결된다. 보안은 단순히 인증·인가만의 문제가 아니라, 데이터 무결성과 일관성을 공격 또는 장애 상황에서도 유지하는 문제를 포함한다.

## 1. 데이터 무결성 보호

ACID는 데이터 무결성의 기반이다. 예를 들어 결제 시스템에서 결제 승인과 주문 상태 변경이 하나의 트랜잭션으로 묶이지 않으면, 결제는 되었지만 주문은 생성되지 않는 상태가 발생할 수 있다. 이는 보안 사고와 고객 피해로 이어질 수 있다.

모범 사례:

- 금전, 포인트, 재고 관련 변경은 단일 트랜잭션으로 묶기
- DB 제약 조건을 적극적으로 사용
  - PRIMARY KEY
  - FOREIGN KEY
  - UNIQUE
  - CHECK
  - NOT NULL
- 애플리케이션 검증만 믿지 않고 DB 레벨 제약도 설정

## 2. Race Condition 취약점

웹 애플리케이션에서는 동시 요청을 악용한 Race Condition 공격이 발생할 수 있다.

예를 들어 쿠폰을 한 번만 사용할 수 있어야 하는데, 공격자가 동시에 여러 요청을 보내면 다음 문제가 생길 수 있다.

```text
요청 1: 쿠폰 사용 여부 확인 → 미사용
요청 2: 쿠폰 사용 여부 확인 → 미사용
요청 1: 쿠폰 사용 처리
요청 2: 쿠폰 사용 처리
```

이를 막기 위해 다음 방법을 사용할 수 있다.

- UNIQUE 제약 조건
- 원자적 UPDATE
- SELECT ... FOR UPDATE
- 낙관적 락 버전 컬럼
- 적절한 격리 수준
- idempotency key

## 3. SQL Injection과 트랜잭션

SQL Injection은 공격자가 SQL을 조작하여 데이터를 탈취, 수정, 삭제하는 취약점이다. 트랜잭션 자체가 SQL Injection을 막아주지는 않는다. 하지만 트랜잭션을 사용하면 잘못된 처리 중 일부를 롤백할 수 있다. 근본적인 방어는 다음과 같다.

- Prepared Statement 사용
- ORM 또는 쿼리 빌더의 안전한 바인딩 사용
- 입력값 검증
- 최소 권한 계정 사용
- DDL, DROP 권한을 애플리케이션 계정에 부여하지 않기
- 민감 데이터 접근 로깅

## 4. 권한과 트랜잭션 범위

트랜잭션이 강력하더라도 DB 계정 권한이 과도하면 피해 범위가 커진다.

모범 사례:

- 애플리케이션별 DB 계정 분리
- 읽기 전용 계정과 쓰기 계정 분리
- 운영자 계정과 애플리케이션 계정 분리
- 필요한 테이블과 명령에만 권한 부여
- 감사 로그 활성화
- 마이그레이션 권한과 런타임 권한 분리

## 5. 장기 트랜잭션과 서비스 거부

장기 트랜잭션은 락을 오래 보유하거나 MVCC 버전 정리를 방해할 수 있다. 공격자 또는 비정상 클라이언트가 의도적으로 오래 실행되는 트랜잭션을 많이 만들면 성능 저하 또는 서비스 거부와 유사한 문제가 발생할 수 있다.

대응 방법:

- statement timeout 설정
- idle in transaction timeout 설정
- 커넥션 풀 제한
- 긴 쿼리 모니터링
- 락 대기 모니터링
- 트랜잭션 내부에서 사용자 입력 대기 금지

## 6. 로그와 개인정보

트랜잭션 로그, DB 로그, 애플리케이션 로그에는 민감한 데이터가 포함될 수 있다. 특히 장애 분석을 위해 SQL 파라미터를 그대로 로깅하면 개인정보나 인증 정보가 노출될 수 있다.

모범 사례:

- 민감 정보 마스킹
- 로그 접근 권한 제한
- 로그 보존 기간 관리
- 암호화된 저장소 사용
- 백업과 스냅샷 접근 제어
- 감사 추적 유지

---

---

## 면접 질문

**Q1. ACID 특성이 무엇인지 설명해주세요.**  
> 핵심 답변: ACID는 트랜잭션의 신뢰성을 보장하는 네 가지 성질이다. Atomicity는 모두 성공 또는 모두 실패, Consistency는 제약 조건과 무결성 유지, Isolation은 동시 트랜잭션 간 간섭 제어, Durability는 커밋된 결과의 영구 보존을 의미한다.

**Q2. Dirty Read, Non-repeatable Read, Phantom Read의 차이는 무엇인가요?**  
> 핵심 답변: Dirty Read는 커밋되지 않은 데이터를 읽는 현상이다. Non-repeatable Read는 같은 트랜잭션에서 같은 행을 다시 읽었을 때 값이 달라지는 현상이다. Phantom Read는 같은 조건의 범위 조회 결과에서 행이 추가되거나 사라지는 현상이다.

**Q3. Read Committed와 Repeatable Read의 차이는 무엇인가요?**  
> 핵심 답변: Read Committed는 커밋된 데이터만 읽지만 같은 트랜잭션 내에서 다시 읽을 때 값이 바뀔 수 있다. Repeatable Read는 일반적으로 같은 행에 대한 반복 읽기를 보장한다. 다만 Phantom Read 처리 방식은 DBMS 구현에 따라 달라질 수 있다.

**Q4. MVCC가 무엇이고 왜 사용하는지 설명해주세요.**  
> 핵심 답변: MVCC는 Multi-Version Concurrency Control의 약자로, 데이터의 여러 버전을 유지하여 트랜잭션이 적절한 시점의 스냅샷을 읽게 하는 방식이다. 읽기와 쓰기 간 충돌을 줄이고 동시성을 높이기 위해 사용된다. PostgreSQL, MySQL InnoDB 등에서 사용된다.

**Q5. 재고 차감 로직에서 Lost Update를 어떻게 방지할 수 있나요?**  
> 핵심 답변: SELECT 후 애플리케이션에서 계산하고 UPDATE하는 방식은 Lost Update 위험이 있다. 원자적 UPDATE를 사용하거나 SELECT ... FOR UPDATE로 락을 잡거나, version 컬럼을 이용한 낙관적 락을 사용할 수 있다. 예를 들어 `UPDATE item SET stock = stock - 1 WHERE id = ? AND stock > 0` 후 영향받은 행 수를 확인하는 방식이 안전하다.

---

---

## 관련 개념

- [[트랜잭션]] - ACID와 격리 수준이 적용되는 논리적 작업 단위이다.
- [[ACID]] - RDBMS 트랜잭션 신뢰성을 설명하는 핵심 원칙이다.
- [[MVCC]] - 격리성을 구현하는 대표적인 동시성 제어 방식이다.
- [[락]] - 동시 트랜잭션 간 충돌을 제어하기 위한 기본 메커니즘이다.
- [[데드락]] - 여러 트랜잭션이 서로의 락을 기다리며 진행하지 못하는 상태이다.
- [[WAL]] - 커밋된 변경의 지속성과 장애 복구를 지원하는 로그 기법이다.
- [[Undo Log]] - 롤백과 MVCC 버전 관리를 위해 사용될 수 있는 변경 전 정보이다.
- [[Redo Log]] - 장애 후 커밋된 변경을 재적용하기 위한 로그이다.
- [[낙관적 락]] - 충돌이 드물다고 가정하고 버전 검사를 통해 동시성 문제를 제어한다.
- [[비관적 락]] - 충돌 가능성이 높다고 보고 먼저 락을 획득해 수정 충돌을 막는다.
- [[Serializable]] - 트랜잭션들이 직렬로 실행된 것과 같은 결과를 보장하는 강한 격리 수준이다.
- [[Lost Update]] - 동시 수정으로 한 트랜잭션의 변경이 다른 트랜잭션에 의해 덮어써지는 문제이다.
