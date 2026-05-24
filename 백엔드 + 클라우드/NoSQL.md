---
date: 2026-05-25
category: 백엔드 - 데이터베이스
topic: NoSQL
subtopic: Key-Value(Redis), Document(MongoDB), CAP 정리, PACELC 정리
tags: [CS, 백엔드---데이터베이스, study]
---

# NoSQL - Key-Value(Redis), Document(MongoDB), CAP 정리, PACELC 정리

## 핵심 개념

# NoSQL: Key-Value, Document, CAP, PACELC 핵심 개념

NoSQL은 전통적인 관계형 데이터베이스가 제공하는 고정 스키마, SQL 중심 질의, 강한 정규화 모델만으로는 처리하기 어려운 대규모 트래픽, 유연한 데이터 구조, 수평 확장 요구를 해결하기 위해 사용되는 데이터베이스 계열이다. NoSQL은 하나의 기술이 아니라 데이터 모델에 따라 Key-Value, Document, Column-Family, Graph 등으로 나뉜다.

## Key-Value Store: Redis

Key-Value 데이터베이스는 데이터를 `key → value` 형태로 저장한다. 애플리케이션은 특정 key를 통해 value를 빠르게 조회한다. Redis는 대표적인 Key-Value 저장소이며, 단순 문자열뿐 아니라 List, Set, Sorted Set, Hash, Stream 같은 다양한 자료구조를 지원한다. Redis는 주로 메모리 기반으로 동작하기 때문에 매우 빠른 읽기/쓰기 성능을 제공하며, 캐시, 세션 저장소, 분산 락, 랭킹 시스템, 메시지 큐 보조 수단 등에 널리 사용된다.

Redis가 중요한 이유는 데이터베이스의 부하를 줄이고, 응답 지연 시간을 낮추며, 짧은 시간 안에 많은 요청을 처리할 수 있게 해주기 때문이다. 다만 메모리 기반 특성상 데이터 크기 관리, eviction 정책, 영속화 설정, 장애 복구 전략을 반드시 고려해야 한다.

## Document Store: MongoDB

Document 데이터베이스는 데이터를 행과 열이 아닌 문서 단위로 저장한다. MongoDB는 대표적인 Document DB이며, JSON과 유사한 BSON 형식으로 데이터를 저장한다. 하나의 문서 안에 중첩 객체와 배열을 포함할 수 있어 애플리케이션의 객체 모델과 잘 맞는다. 예를 들어 사용자 프로필, 주문 내역, 게시글과 댓글처럼 구조가 유연하거나 필드가 자주 바뀌는 데이터에 적합하다.

MongoDB가 중요한 이유는 스키마 변경 비용을 줄이고, 수평 확장과 복제 기능을 통해 대규모 데이터를 처리할 수 있기 때문이다. 하지만 Document DB라고 해서 항상 조인이 필요 없는 것은 아니며, 데이터 중복, 문서 크기 증가, 인덱스 설계, 일관성 수준을 신중하게 고려해야 한다.

## CAP 정리

CAP 정리는 분산 시스템에서 다음 세 가지 특성을 동시에 완벽히 만족할 수 없다는 이론이다.

- **Consistency, 일관성**: 모든 노드가 같은 시점에 같은 데이터를 보여준다.
- **Availability, 가용성**: 모든 요청은 실패하지 않고 응답을 받는다.
- **Partition Tolerance, 네트워크 분할 허용성**: 노드 간 네트워크 장애가 발생해도 시스템이 계속 동작한다.

현실의 분산 시스템에서는 네트워크 분할 가능성을 완전히 제거할 수 없으므로, 장애 상황에서는 보통 Consistency와 Availability 사이의 절충이 발생한다. 즉 CAP는 “평상시 선택”이라기보다 “네트워크 분할이 발생했을 때 무엇을 희생할 것인가”를 설명하는 모델로 이해하는 것이 중요하다.

## PACELC 정리

PACELC는 CAP를 확장한 관점이다. CAP가 네트워크 분할 상황에 초점을 둔다면, PACELC는 정상 상황에서도 일관성과 지연 시간 사이의 선택이 존재한다고 설명한다.

- **P**artition이 발생하면 **A**vailability와 **C**onsistency 중 선택
- **E**lse, 즉 partition이 없을 때도 **L**atency와 **C**onsistency 중 선택

예를 들어 강한 일관성을 위해 여러 노드의 확인을 기다리면 지연 시간이 늘어날 수 있고, 빠른 응답을 우선하면 최신 데이터 반영이 늦어질 수 있다. 따라서 NoSQL 시스템을 설계할 때는 CAP뿐 아니라 PACELC 관점으로 장애 상황과 정상 상황 모두에서의 트레이드오프를 이해해야 한다.

---

---

## 내부 동작 원리

# 내부 동작 원리

## 1. Redis Key-Value 저장 구조

Redis는 클라이언트가 보낸 명령을 받아 key를 기준으로 데이터를 조회하거나 변경한다. 기본적으로 단일 명령은 Redis 서버의 이벤트 루프에서 처리된다. Redis는 자료구조별로 최적화된 내부 표현을 사용하며, 사용자는 `GET`, `SET`, `HGET`, `LPUSH`, `ZADD` 같은 명령으로 접근한다.

### Redis 기본 흐름

```text
[Client]
   |
   | SET user:1 "kim"
   v
[Redis Server]
   |
   | key hash lookup
   v
[In-Memory Data Structure]
   |
   | optional persistence
   v
[RDB Snapshot / AOF Log]
```

동작 과정은 다음과 같다.

1. 클라이언트가 Redis 서버에 TCP 연결을 맺는다.
2. 클라이언트가 명령을 전송한다.
3. Redis는 key를 해시 테이블에서 찾는다.
4. value의 자료구조 타입에 맞게 명령을 실행한다.
5. 필요하면 만료 시간 TTL을 설정하거나 갱신한다.
6. 영속화 설정에 따라 RDB 스냅샷 또는 AOF 로그에 반영한다.
7. 복제 구성이 있다면 replica 노드로 변경 사항을 전달한다.

Redis는 캐시로 사용할 때 보통 다음 패턴을 사용한다.

```text
[Application]
   |
   | 1. cache lookup
   v
[Redis]
   |
   | miss
   v
[Primary DB]
   |
   | 2. read from DB
   v
[Application]
   |
   | 3. write cache
   v
[Redis]
```

이를 **Cache-Aside 패턴**이라고 한다. 애플리케이션이 먼저 Redis를 조회하고, cache miss가 발생하면 원본 DB에서 읽은 뒤 Redis에 다시 저장한다.

## 2. Redis 영속화와 복제

Redis는 메모리 기반이지만 영속화를 통해 재시작 후 데이터를 복구할 수 있다.

- **RDB**: 특정 시점의 데이터를 스냅샷으로 저장한다.
- **AOF**: 실행된 쓰기 명령을 로그 형태로 기록한다.
- **Replication**: primary 노드의 데이터를 replica 노드로 복제한다.
- **Sentinel 또는 Cluster 구성**: 장애 감지, failover, 분산 저장 등에 사용된다.

주의할 점은 Redis 영속화가 설정되어 있어도 모든 장애 상황에서 데이터 손실이 전혀 없다고 보장되는 것은 아니라는 점이다. 설정 방식, fsync 정책, 장애 시점에 따라 유실 가능성이 달라진다.

## 3. MongoDB Document 저장 구조

MongoDB는 데이터를 database → collection → document 구조로 저장한다.

```text
[Database]
   |
   +-- [Collection: users]
          |
          +-- { _id: 1, name: "kim", roles: ["admin"] }
          +-- { _id: 2, name: "lee", profile: { age: 30 } }
```

MongoDB의 문서는 BSON 형식으로 저장된다. BSON은 JSON과 유사하지만 바이너리 표현이며, 날짜, ObjectId, 이진 데이터 같은 타입을 표현할 수 있다.

### MongoDB 읽기/쓰기 흐름

```text
[Client / Driver]
   |
   | insertOne({name: "kim"})
   v
[mongod]
   |
   | validate / assign _id / write
   v
[Storage Engine]
   |
   | journal / data file / index update
   v
[Replica Set Replication]
```

일반적인 쓰기 과정은 다음과 같다.

1. 클라이언트가 MongoDB 드라이버를 통해 요청한다.
2. primary 노드가 쓰기 요청을 받는다.
3. 문서에 `_id`가 없으면 생성한다.
4. 스토리지 엔진이 데이터와 인덱스를 갱신한다.
5. journal 설정에 따라 장애 복구용 로그를 기록한다.
6. replica set 구성에서는 secondary 노드가 oplog를 통해 변경 사항을 복제한다.

## 4. MongoDB Replica Set

MongoDB의 replica set은 고가용성을 위한 복제 구성이다.

```text
              write
[Application] -----> [Primary]
                       |
                       | oplog replication
                       v
                  [Secondary]
                       |
                       v
                  [Secondary]
```

- 모든 쓰기는 primary에서 처리된다.
- secondary는 primary의 변경 로그를 따라가며 데이터를 복제한다.
- primary 장애 시 선거를 통해 새로운 primary가 선출될 수 있다.
- 읽기 설정에 따라 secondary에서 읽을 수도 있지만, 이 경우 최신 데이터가 아닐 수 있다.

## 5. MongoDB Sharding

Sharding은 데이터를 여러 노드에 나누어 저장하는 수평 확장 방식이다.

```text
[Application]
     |
     v
  [mongos Router]
     |
     +----> [Shard A]
     |
     +----> [Shard B]
     |
     +----> [Shard C]
```

동작 과정은 다음과 같다.

1. 애플리케이션은 mongos 라우터에 요청한다.
2. mongos는 shard key를 기준으로 데이터가 위치한 shard를 찾는다.
3. 해당 shard에 읽기/쓰기 요청을 전달한다.
4. 여러 shard에 걸친 쿼리라면 결과를 병합한다.

Shard key 선택은 매우 중요하다. 잘못된 shard key는 특정 shard에 트래픽이 몰리는 hot shard 문제를 만들 수 있다.

## 6. CAP 관점의 내부 동작

분산 DB에서 네트워크 분할이 발생하면 노드 간 통신이 끊길 수 있다.

```text
정상 상태:

[Node A] <----> [Node B] <----> [Node C]

네트워크 분할:

[Node A] <----X----> [Node B] <----> [Node C]
```

이때 시스템은 선택해야 한다.

- **CP 선택**: 일관성을 지키기 위해 일부 요청을 거부하거나 대기시킨다.
- **AP 선택**: 응답 가능성을 우선하여 요청을 처리하되, 나중에 데이터 충돌이나 불일치를 해결한다.

Redis나 MongoDB를 사용할 때도 배포 구성, 복제 지연, 장애 조치 정책에 따라 일관성과 가용성의 체감 특성이 달라진다.

## 7. PACELC 관점의 내부 동작

PACELC는 장애 상황뿐 아니라 정상 상황에서도 선택이 필요하다고 본다.

```text
요청 발생
   |
   v
네트워크 분할 발생?
   |
   +-- Yes --> Availability vs Consistency
   |
   +-- No  --> Latency vs Consistency
```

예를 들어 다중 노드에 동기적으로 쓰기 확인을 받으면 더 강한 일관성을 얻을 수 있지만 지연 시간이 증가한다. 반대로 primary에만 빠르게 쓰고 replica 반영을 기다리지 않으면 응답은 빠르지만 replica에서 읽을 때 오래된 데이터를 볼 수 있다.

---

---

## 실제 시스템 연결

# 실제 시스템 연결

## 1. Linux와 Redis

Redis는 Linux 서버에서 자주 운영된다. Redis는 메모리를 적극적으로 사용하므로 Linux의 메모리 관리, 파일 디스크립터 제한, 네트워크 소켓, 프로세스 관리와 밀접하다.

실제 운영에서 고려할 점은 다음과 같다.

- Redis 프로세스가 사용할 수 있는 메모리 제한
- swap 사용 여부
- TCP backlog 및 connection 수 제한
- RDB/AOF 저장 시 디스크 I/O
- systemd를 통한 서비스 관리
- 로그 수집 및 모니터링

Redis가 캐시로 사용될 때 메모리 한도를 초과하면 eviction 정책에 따라 key가 제거될 수 있다. 따라서 `maxmemory`와 eviction 정책은 서비스 특성에 맞게 설정해야 한다.

## 2. Linux와 MongoDB

MongoDB는 디스크 기반 저장소이며, 메모리 캐시와 디스크 I/O가 성능에 큰 영향을 준다. Linux 환경에서는 다음 요소가 중요하다.

- 파일 시스템 성능
- 디스크 IOPS
- 메모리 캐시
- 네트워크 대역폭
- 프로세스 및 파일 디스크립터 제한
- 시간 동기화

MongoDB는 인덱스가 메모리에 잘 올라와 있을수록 읽기 성능이 좋아지는 경향이 있다. 반대로 인덱스 설계가 부적절하면 collection scan이 발생하고 CPU와 디스크 I/O가 증가할 수 있다.

## 3. AWS에서의 연결

AWS에서는 Redis와 MongoDB를 직접 EC2에 설치할 수도 있고, 관리형 서비스를 사용할 수도 있다.

- **Redis 관련**: Amazon ElastiCache for Redis 또는 Redis 호환 서비스 사용 가능
- **MongoDB 관련**: EC2 직접 설치, MongoDB Atlas on AWS, 또는 DocumentDB 사용 가능
- **네트워크**: VPC, Security Group, Subnet, Route Table과 연결
- **고가용성**: Multi-AZ 구성, replica 구성, 자동 장애 조치 옵션 활용
- **모니터링**: CloudWatch, 로그 수집, 메트릭 알람

⚠️ 확인 필요: Amazon DocumentDB는 MongoDB API 호환을 목표로 하는 서비스이지만, MongoDB의 모든 기능과 동작이 완전히 동일하다고 가정하면 안 된다. 실제 호환 범위는 사용하는 버전과 기능별로 확인해야 한다.

## 4. GCP에서의 연결

GCP에서는 Redis와 MongoDB를 다음 방식으로 사용할 수 있다.

- **Redis**: Memorystore for Redis
- **MongoDB**: Compute Engine 직접 설치, GKE 배포, MongoDB Atlas on GCP
- **네트워크**: VPC, 방화벽 규칙, Private Service Connect 등
- **모니터링**: Cloud Monitoring, Cloud Logging

관리형 Redis는 운영 부담을 줄여주지만, 세부 설정 가능 범위가 직접 운영보다 제한될 수 있다. MongoDB 역시 직접 설치와 관리형 서비스를 비교할 때 백업, 복구, 패치, 확장, 보안 설정 책임 범위를 명확히 해야 한다.

## 5. Nginx와의 연결

Nginx는 직접 NoSQL 데이터베이스를 대체하지는 않지만, 백엔드 API 앞단에서 트래픽을 제어하는 역할을 한다.

```text
[Client]
   |
   v
[Nginx]
   |
   v
[Backend API]
   |
   +--> [Redis Cache]
   |
   +--> [MongoDB]
```

Nginx는 다음과 같은 방식으로 NoSQL 시스템의 안정성에 기여한다.

- Rate limiting으로 과도한 요청 방지
- Reverse proxy로 백엔드 서버 보호
- TLS 종료 지점 구성
- Load balancing
- 장애 서버 우회

예를 들어 로그인 API가 Redis 세션 저장소를 사용한다면, Nginx rate limiting을 통해 brute-force 공격을 완화할 수 있다.

## 6. 실제 아키텍처 예시

```text
[User]
  |
  v
[CDN / WAF]
  |
  v
[Nginx / Load Balancer]
  |
  v
[Backend API Servers]
  |
  +--> [Redis: session, cache, rate limit counter]
  |
  +--> [MongoDB: user profile, posts, flexible documents]
```

이 구조에서 Redis는 빠른 조회와 임시 상태 저장에 적합하고, MongoDB는 영속적인 문서 데이터를 저장한다. CAP/PACELC 관점에서는 Redis replica 읽기, MongoDB secondary 읽기, 다중 리전 복제 여부에 따라 일관성과 지연 시간의 균형을 설계해야 한다.

---

---

## 클라우드 연결

# 클라우드 연결

## 1. Docker에서 Redis와 MongoDB

개발 환경에서는 Docker로 Redis와 MongoDB를 쉽게 실행할 수 있다.

```text
[Docker Host]
   |
   +-- [redis container]
   |
   +-- [mongodb container]
   |
   +-- [backend container]
```

Docker 사용 시 중요한 점은 컨테이너가 삭제되면 내부 파일 시스템의 데이터도 사라질 수 있다는 것이다. 따라서 MongoDB나 Redis 영속화 데이터를 유지하려면 volume을 사용해야 한다.

예시 개념:

```text
[Container]
   |
   v
[Docker Volume]
   |
   v
[Host Storage]
```

Redis를 단순 캐시로만 사용한다면 데이터 손실을 감수할 수 있지만, 세션이나 큐처럼 중요한 데이터를 저장한다면 volume, 백업, 복구 전략이 필요하다.

## 2. Kubernetes에서의 운영

Kubernetes에서는 Redis와 MongoDB를 Pod로 실행할 수 있지만, 상태를 가진 데이터베이스 운영은 stateless 애플리케이션보다 복잡하다.

관련 리소스는 다음과 같다.

- **StatefulSet**: 안정적인 네트워크 ID와 스토리지 식별자 제공
- **PersistentVolume / PersistentVolumeClaim**: 데이터 저장소 연결
- **Service**: Pod 접근 경로 제공
- **ConfigMap / Secret**: 설정과 인증 정보 관리
- **PodDisruptionBudget**: 자발적 중단 시 가용성 보호
- **Readiness Probe**: 준비되지 않은 DB 인스턴스로 트래픽 유입 방지

```text
[Backend Deployment]
        |
        v
[Redis Service] ---> [Redis StatefulSet + PVC]

[Mongo Service] ---> [Mongo StatefulSet + PVC]
```

Kubernetes에서 데이터베이스를 직접 운영할 경우 백업, 복구, 장애 조치, 버전 업그레이드, 스토리지 성능, 노드 재배치에 따른 영향까지 직접 관리해야 한다. 운영 부담을 줄이기 위해 클라우드 관리형 서비스를 함께 사용하는 경우도 많다.

## 3. AWS 서비스와 Redis

AWS에서 Redis는 일반적으로 다음 구성과 연결된다.

```text
[Application on ECS/EKS/EC2/Lambda]
        |
        v
[ElastiCache for Redis]
        |
        v
[VPC Subnet / Security Group]
```

활용 사례:

- API 응답 캐시
- 세션 저장소
- 분산 락
- Rate limiting counter
- 실시간 랭킹
- Pub/Sub 기반 이벤트 전달 보조

주의할 점:

- Redis는 기본적으로 인터넷에 공개하지 않는 것이 원칙이다.
- Security Group으로 접근 가능한 애플리케이션만 허용한다.
- 클러스터 구성, replica, 백업, 자동 장애 조치 옵션을 서비스 요구사항에 맞게 선택한다.
- 메모리 사용량과 eviction을 모니터링한다.

## 4. AWS 서비스와 MongoDB

MongoDB는 다음 방식으로 AWS와 연결될 수 있다.

```text
[Application]
   |
   +--> [MongoDB on EC2]
   |
   +--> [MongoDB Atlas]
   |
   +--> [Amazon DocumentDB]
```

선택 기준:

- 직접 운영이 필요한가?
- MongoDB 기능 호환성이 중요한가?
- 백업과 장애 조치를 직접 관리할 수 있는가?
- VPC 내부 통신이 필요한가?
- 글로벌 복제나 다중 리전 요구사항이 있는가?

⚠️ 확인 필요: MongoDB Atlas, Amazon DocumentDB, 직접 설치 MongoDB는 기능, 성능 특성, 백업 방식, 네트워크 연결 방식이 다르므로 실제 도입 전 공식 문서와 PoC로 검증해야 한다.

## 5. CAP/PACELC와 클라우드 아키텍처

클라우드에서는 리전, 가용 영역, 네트워크 장애, 지연 시간이 CAP/PACELC 판단에 직접적인 영향을 준다.

```text
[Region A] <---- network latency ----> [Region B]
```

- 단일 리전 내부 구성: 지연 시간은 낮지만 리전 장애에 취약할 수 있다.
- 다중 AZ 구성: 가용성을 높일 수 있으나 네트워크와 스토리지 비용이 증가할 수 있다.
- 다중 리전 구성: 재해 복구에 유리하지만 일관성과 지연 시간 문제가 커진다.

PACELC 관점에서 다중 리전 쓰기 시스템은 특히 어렵다. 모든 리전에 강한 일관성을 제공하려면 합의 비용과 네트워크 왕복 시간이 증가할 수 있다. 반대로 각 리전에서 빠르게 쓰기를 허용하면 충돌 해결과 eventual consistency를 다뤄야 한다.

---

---

## 보안 연결

# 보안 연결

## 1. Redis 보안 이슈

Redis는 빠른 내부 네트워크 접근을 전제로 많이 사용되므로, 외부 인터넷에 노출되면 매우 위험하다. 인증 없이 접근 가능한 Redis 인스턴스는 데이터 유출, 데이터 삭제, 악성 명령 실행 시도 등의 위험에 노출될 수 있다.

Redis 보안 모범 사례:

- 인터넷에 직접 노출하지 않는다.
- VPC 내부 또는 사설 네트워크에서만 접근하게 한다.
- 방화벽, Security Group, Network ACL로 접근 IP를 제한한다.
- 인증을 활성화한다.
- TLS 사용 가능 환경에서는 전송 암호화를 적용한다.
- 위험한 관리 명령의 사용을 제한한다.
- 중요한 데이터를 평문으로 저장하지 않는다.
- 백업 파일과 AOF/RDB 파일 권한을 보호한다.
- 최소 권한 원칙에 따라 애플리케이션별 계정을 분리한다.

Redis에 세션이나 토큰을 저장할 경우 TTL을 반드시 설정하는 것이 좋다. 만료되지 않는 인증 정보는 탈취 시 피해가 커질 수 있다.

## 2. MongoDB 보안 이슈

MongoDB는 문서 기반으로 유연하게 데이터를 저장할 수 있지만, 보안 설정이 부실하면 민감 정보가 그대로 노출될 수 있다.

MongoDB 보안 모범 사례:

- 인증과 권한 관리를 활성화한다.
- role-based access control을 적용한다.
- 관리자 계정과 애플리케이션 계정을 분리한다.
- 네트워크 접근을 제한한다.
- TLS로 클라이언트와 서버 간 통신을 암호화한다.
- 디스크 암호화 또는 클라우드 스토리지 암호화를 검토한다.
- 감사 로그를 활성화한다.
- 백업 파일을 암호화하고 접근 권한을 제한한다.
- 쿼리 입력값을 검증하여 NoSQL Injection을 방지한다.

## 3. NoSQL Injection

NoSQL Injection은 SQL Injection과 유사하게, 사용자의 입력이 쿼리 객체나 조건식에 안전하지 않게 삽입될 때 발생한다.

취약한 예시 개념:

```javascript
// 위험한 개념 예시
db.users.findOne({
  username: input.username,
  password: input.password
})
```

문제는 공격자가 단순 문자열 대신 연산자 객체를 주입할 수 있는 경우다.

```json
{
  "username": "admin",
  "password": { "$ne": null }
}
```

이런 입력이 필터링 없이 쿼리 조건으로 사용되면 인증 우회 같은 문제가 발생할 수 있다.

방어 방법:

- 입력 타입을 명확히 검증한다.
- 사용자 입력에서 허용하지 않는 연산자 키를 차단한다.
- ODM/ORM의 안전한 API를 사용한다.
- 인증 로직에서 해시된 비밀번호 비교를 애플리케이션 레벨에서 안전하게 수행한다.
- 최소 권한 DB 계정을 사용한다.

## 4. 캐시 보안

Redis 같은 캐시에는 DB에서 읽은 데이터가 저장될 수 있으므로, 캐시도 민감 정보 저장소로 취급해야 한다.

주의 사항:

- 개인정보, 토큰, 결제 정보 저장을 최소화한다.
- 반드시 필요한 경우 암호화 또는 마스킹을 고려한다.
- TTL을 설정한다.
- key naming에 민감 정보를 포함하지 않는다.
- tenant 간 key 충돌을 방지한다.
- 캐시 무효화 정책을 명확히 한다.

예를 들어 `user:email:someone@example.com` 같은 key는 로그나 모니터링 도구에 노출될 수 있으므로 민감 정보를 key에 직접 포함하지 않는 것이 좋다.

## 5. CAP/PACELC와 보안

CAP/PACELC는 성능과 가용성뿐 아니라 보안 설계에도 영향을 준다.

- 강한 일관성이 필요한 보안 데이터: 권한, 계정 잠금, 결제 상태
- eventual consistency를 허용하기 어려운 데이터: 인증 실패 횟수, 관리자 권한 변경
- 지연 시간 우선 처리가 가능한 데이터: 추천 결과, 조회수, 비핵심 캐시

예를 들어 관리자 권한을 박탈했는데 replica 반영이 늦어 secondary에서 오래된 권한을 읽는다면 보안 문제가 될 수 있다. 따라서 권한 확인, 인증, 결제와 같은 보안 민감 경로에서는 읽기 일관성 설정을 보수적으로 가져가는 것이 좋다.

---

---

## 면접 질문

# 면접 질문

**Q1. Redis를 RDBMS 대신 메인 데이터베이스로 사용해도 되나요?**  
> 핵심 답변: Redis는 메모리 기반 Key-Value 저장소로 매우 빠르지만, 일반적인 관계형 모델, 복잡한 질의, 트랜잭션 요구, 데이터 영속성 보장 수준이 RDBMS와 다르다. 캐시, 세션, 랭킹, 임시 데이터에 적합하며, 메인 저장소로 사용할 경우 영속화, 복제, 백업, 장애 시 데이터 손실 가능성, 메모리 비용을 반드시 검토해야 한다.

**Q2. MongoDB가 RDBMS보다 항상 더 빠른가요?**  
> 핵심 답변: 항상 그렇지 않다. MongoDB는 문서 단위 조회, 유연한 스키마, 수평 확장에 강점이 있지만, 쿼리 패턴, 인덱스 설계, 데이터 모델링, 조인 필요 여부에 따라 성능이 달라진다. 정규화된 관계와 복잡한 조인이 많은 시스템은 RDBMS가 더 적합할 수 있다.

**Q3. CAP 정리에서 CA 시스템은 가능한가요?**  
> 핵심 답변: 단일 노드나 네트워크 분할을 고려하지 않는 환경에서는 일관성과 가용성을 동시에 달성하는 것처럼 보일 수 있다. 하지만 분산 시스템에서 네트워크 분할을 현실적으로 피할 수 없다면, partition 발생 시 consistency와 availability 사이에서 선택해야 한다. 따라서 CAP는 장애 상황에서의 트레이드오프로 이해해야 한다.

**Q4. PACELC가 CAP보다 더 설명력이 있는 이유는 무엇인가요?**  
> 핵심 답변: CAP는 네트워크 분할 상황에서 C와 A의 선택을 설명한다. PACELC는 partition이 없을 때도 latency와 consistency 사이의 선택이 존재한다고 본다. 실제 운영에서는 장애 상황보다 정상 상황이 더 많으므로, 평상시 성능과 일관성 절충까지 설명하는 PACELC가 실무 아키텍처 판단에 유용하다.

**Q5. Redis cache stampede 문제는 무엇이고 어떻게 완화하나요?**  
> 핵심 답변: 특정 인기 key가 만료되는 순간 다수 요청이 동시에 DB로 몰리는 현상이다. 완화 방법으로 TTL에 random jitter 추가, mutex 또는 분산 락 사용, stale cache 제공, background refresh, 요청 coalescing 등이 있다. 핵심은 동시에 많은 요청이 원본 DB를 직접 때리지 않도록 제어하는 것이다.

---

---

## 관련 개념

# 관련 개념

- [[Redis]] - 대표적인 Key-Value NoSQL로 캐시, 세션, 랭킹 등에 사용된다.
- [[MongoDB]] - 대표적인 Document NoSQL로 BSON 기반 문서 저장 모델을 제공한다.
- [[CAP 정리]] - 분산 시스템에서 일관성, 가용성, 네트워크 분할 허용성의 트레이드오프를 설명한다.
- [[PACELC 정리]] - CAP를 확장하여 정상 상황의 지연 시간과 일관성 절충까지 설명한다.
- [[Eventual Consistency]] - AP 계열 시스템이나 비동기 복제에서 자주 등장하는 일관성 모델이다.
- [[Strong Consistency]] - 읽기 요청이 항상 최신 쓰기 결과를 보장해야 하는 상황과 관련된다.
- [[Cache-Aside Pattern]] - 애플리케이션이 캐시 조회와 원본 DB 조회를 직접 제어하는 대표 캐싱 패턴이다.
- [[Redis Persistence]] - RDB, AOF 등 Redis 데이터 영속화 방식과 관련된다.
- [[MongoDB Replica Set]] - MongoDB의 고가용성 복제 구성을 이해하는 핵심 개념이다.
- [[MongoDB Sharding]] - MongoDB 수평 확장과 shard key 설계에 직접 연결된다.
- [[NoSQL Injection]] - MongoDB 같은 NoSQL 쿼리 구조에서 발생할 수 있는 입력 검증 취약점이다.
- [[Distributed Lock]] - Redis를 이용해 구현하는 경우가 많으며 동시성 제어와 관련된다.
