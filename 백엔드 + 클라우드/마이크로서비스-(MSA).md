---
date: 2026-05-20
category: 백엔드 - 아키텍처
topic: 마이크로서비스 (MSA)
subtopic: 모놀리식 비교, API Gateway, Service Discovery, SAGA 패턴
tags: [CS, 백엔드---아키텍처, study]
---

# 마이크로서비스 (MSA) - 모놀리식 비교, API Gateway, Service Discovery, SAGA 패턴

## 핵심 개념

마이크로서비스 아키텍처(Microservices Architecture, MSA)는 하나의 애플리케이션을 작은 독립 서비스들의 집합으로 구성하는 아키텍처 스타일이다. 각 서비스는 특정 비즈니스 기능을 중심으로 설계되며, 독립적으로 개발·배포·확장될 수 있다. 예를 들어 주문, 결제, 배송, 회원 기능을 각각 별도 서비스로 분리할 수 있다.

모놀리식 아키텍처는 하나의 코드베이스와 하나의 배포 단위로 전체 기능을 제공한다. 초기 개발과 배포가 단순하고 트랜잭션 관리가 쉽다는 장점이 있지만, 시스템이 커질수록 코드 결합도가 높아지고 배포 주기가 느려지며 특정 기능만 독립적으로 확장하기 어렵다. 반면 MSA는 서비스별 독립 배포와 장애 격리, 기술 스택 다양화, 조직 단위 확장에 유리하다. 하지만 네트워크 통신, 분산 트랜잭션, 관측성, 보안, 데이터 일관성 관리가 복잡해진다.

MSA에서 중요한 구성 요소로는 API Gateway, Service Discovery, SAGA 패턴이 있다. API Gateway는 클라이언트의 단일 진입점 역할을 하며 인증, 라우팅, 로드밸런싱, 요청 집계 등을 담당한다. Service Discovery는 동적으로 변하는 서비스 인스턴스의 위치를 찾는 메커니즘이다. SAGA 패턴은 여러 서비스에 걸친 분산 트랜잭션을 관리하기 위한 패턴으로, 각 단계의 로컬 트랜잭션과 보상 트랜잭션을 조합해 최종 일관성을 유지한다.

MSA가 중요한 이유는 대규모 서비스에서 빠른 배포, 장애 격리, 유연한 확장, 조직의 독립적 개발을 가능하게 하기 때문이다. 다만 MSA는 단순히 서비스를 잘게 나누는 것이 아니라, 비즈니스 경계와 데이터 소유권, 운영 자동화, 장애 대응 체계까지 함께 설계해야 효과를 얻을 수 있다.

---

---

## 내부 동작 원리

MSA의 내부 동작은 기본적으로 “클라이언트 → API Gateway → 개별 서비스 → 데이터 저장소 또는 다른 서비스” 흐름으로 구성된다. 각 서비스는 자신의 비즈니스 책임과 데이터를 소유하는 것이 일반적이며, 다른 서비스의 데이터베이스를 직접 조회하지 않고 API나 메시지 브로커를 통해 통신한다.

```text
[Client]
   |
   v
[API Gateway]
   |--------------------|
   v                    v
[User Service]      [Order Service]
   |                    |
[User DB]           [Order DB]
                         |
                         v
                  [Payment Service]
                         |
                    [Payment DB]
```

모놀리식 구조에서는 모든 기능이 하나의 프로세스 안에서 함수 호출로 연결된다.

```text
[Client]
   |
   v
[Monolithic Application]
   |-- User Module
   |-- Order Module
   |-- Payment Module
   |
[Single Database]
```

모놀리식은 내부 호출이 메모리 내 함수 호출이므로 빠르고 단순하지만, 전체 애플리케이션이 하나의 배포 단위가 된다. 반대로 MSA는 서비스 간 호출이 HTTP, gRPC, 메시지 큐 등을 통해 이루어지므로 네트워크 지연, 장애, 타임아웃, 재시도, 중복 처리 문제가 발생할 수 있다.

API Gateway는 클라이언트 요청을 받아 적절한 서비스로 라우팅한다. 예를 들어 `/users/**` 요청은 User Service로, `/orders/**` 요청은 Order Service로 전달한다. 또한 인증 토큰 검증, SSL/TLS 종료, 요청 제한, 응답 캐싱, 로깅, 모니터링, API 버전 관리 등을 수행할 수 있다. 단, Gateway에 비즈니스 로직이 과도하게 들어가면 병목과 단일 장애 지점이 될 수 있다.

Service Discovery는 서비스 인스턴스의 동적 위치를 찾는 과정이다. 컨테이너나 클라우드 환경에서는 인스턴스가 수시로 생성·삭제되고 IP가 바뀔 수 있기 때문에, 고정 IP 기반 호출은 적합하지 않다. Service Discovery 방식은 크게 두 가지로 나눌 수 있다.

1. **Client-side Discovery**  
   클라이언트 또는 호출하는 서비스가 서비스 레지스트리에서 대상 인스턴스 목록을 조회한 뒤 직접 호출한다.

```text
[Order Service] -> [Service Registry] -> 인스턴스 목록 조회
[Order Service] -> [Payment Service Instance A]
```

2. **Server-side Discovery**  
   클라이언트는 로드밸런서나 프록시로 요청하고, 로드밸런서가 서비스 레지스트리를 참고해 적절한 인스턴스로 전달한다.

```text
[Order Service] -> [Load Balancer] -> [Payment Service Instance]
```

SAGA 패턴은 분산 트랜잭션을 하나의 전역 락으로 처리하지 않고, 여러 로컬 트랜잭션과 보상 트랜잭션으로 나누어 처리한다. 예를 들어 주문 생성 과정은 다음과 같다.

```text
1. Order Service: 주문 생성
2. Payment Service: 결제 승인
3. Inventory Service: 재고 차감
4. Delivery Service: 배송 요청
```

만약 3단계 재고 차감이 실패하면 이미 수행된 결제 승인과 주문 생성에 대해 보상 작업을 수행한다.

```text
재고 차감 실패
-> Payment Service: 결제 취소
-> Order Service: 주문 취소
```

SAGA에는 대표적으로 두 방식이 있다.

- **Choreography 방식**: 각 서비스가 이벤트를 발행하고, 다른 서비스가 이를 구독하여 다음 작업을 수행한다.
- **Orchestration 방식**: 중앙의 Orchestrator가 전체 흐름을 제어하고 각 서비스에 명령을 내린다.

Choreography는 중앙 제어자가 없어 느슨한 결합에 유리하지만, 흐름이 복잡해지면 추적이 어렵다. Orchestration은 전체 흐름을 이해하기 쉽지만, Orchestrator가 중요 컴포넌트가 된다.

---

---

## 실제 시스템 연결

실제 시스템에서 MSA는 대규모 트래픽, 팀 단위 개발, 빠른 배포가 필요한 환경에서 자주 사용된다. 예를 들어 전자상거래 시스템은 회원, 상품, 주문, 결제, 배송, 쿠폰, 알림 등의 도메인을 별도 서비스로 분리할 수 있다. 주문 트래픽은 많지만 회원 정보 변경은 상대적으로 적다면, Order Service만 별도로 확장할 수 있다.

Linux 환경에서는 각 마이크로서비스가 독립 프로세스로 실행되거나 컨테이너로 격리되어 실행된다. 서비스는 보통 TCP 포트를 열고 HTTP REST API, gRPC, 메시지 큐 프로토콜 등을 사용해 통신한다. 운영자는 `systemd`, Docker, Kubernetes 등을 통해 서비스 프로세스를 관리할 수 있다. 로그는 각 서비스에서 개별적으로 발생하므로 중앙 로그 수집 시스템이 필요하다. 예를 들어 Fluent Bit, Logstash, OpenSearch, Elasticsearch, Grafana Loki 등이 사용될 수 있다.

Nginx는 API Gateway 또는 Reverse Proxy 역할로 사용될 수 있다. 예를 들어 `/api/users` 요청은 User Service로, `/api/orders` 요청은 Order Service로 프록시할 수 있다.

```nginx
location /api/users/ {
    proxy_pass http://user-service;
}

location /api/orders/ {
    proxy_pass http://order-service;
}
```

다만 Nginx만으로 복잡한 인증 정책, 서비스 디스커버리, 동적 라우팅, 관측성 기능을 모두 처리하기에는 한계가 있을 수 있어, Kong, Envoy, Traefik, Spring Cloud Gateway 같은 API Gateway 제품이나 프레임워크가 함께 사용되기도 한다.

AWS 환경에서는 다음과 같은 구성이 가능하다.

```text
[Amazon CloudFront]
        |
[Application Load Balancer]
        |
[API Gateway 또는 Ingress Controller]
        |
[ECS/EKS 기반 Microservices]
        |
[RDS, DynamoDB, SQS, SNS, ElastiCache]
```

Service Discovery는 AWS Cloud Map, ECS Service Discovery, Kubernetes DNS 등을 통해 구현할 수 있다. 메시지 기반 비동기 통신에는 Amazon SQS, SNS, EventBridge, MSK 등이 사용될 수 있다. 예를 들어 주문 생성 이벤트를 EventBridge 또는 Kafka 토픽에 발행하고, 결제 서비스와 알림 서비스가 이를 구독하는 구조를 만들 수 있다.

GCP에서는 Cloud Run, Google Kubernetes Engine, Cloud Load Balancing, Pub/Sub, Cloud SQL, Firestore 등을 조합해 MSA를 구성할 수 있다. Cloud Run은 컨테이너 기반 서비스를 서버리스 형태로 실행할 수 있으며, GKE는 Kubernetes 기반의 세밀한 제어가 필요한 경우에 적합하다.

실제 시스템에서 중요한 점은 서비스 분리 자체보다 운영 복잡성을 감당할 수 있는지다. MSA에서는 장애가 완전히 사라지는 것이 아니라, 장애가 네트워크 경계와 서비스 경계로 이동한다. 따라서 타임아웃, 재시도, 서킷 브레이커, 분산 추적, 중앙 로그, 메트릭, 알림 체계가 필수에 가깝다.

---

---

## 클라우드 연결

MSA는 클라우드 네이티브 환경과 강하게 연결된다. Docker는 각 마이크로서비스를 독립 실행 가능한 컨테이너 이미지로 패키징할 수 있게 해준다. 서비스별로 런타임, 라이브러리, 환경 변수를 분리할 수 있으며, 동일한 이미지를 개발·스테이징·운영 환경에 배포할 수 있다.

```text
[Order Service Image] -> Container
[Payment Service Image] -> Container
[User Service Image] -> Container
```

Kubernetes는 MSA 운영에서 핵심적인 역할을 한다. 각 서비스는 Deployment로 배포되고, Pod 단위로 실행된다. Kubernetes Service는 Pod의 동적 IP 변경을 추상화하여 안정적인 네트워크 엔드포인트를 제공한다. 내부 DNS를 통해 `payment-service.default.svc.cluster.local` 같은 이름으로 서비스에 접근할 수 있다.

```text
[Order Pod] -> [Kubernetes Service: payment-service] -> [Payment Pods]
```

Kubernetes의 주요 MSA 관련 기능은 다음과 같다.

- **Deployment**: 서비스 배포와 롤링 업데이트 관리
- **Service**: Pod 집합에 대한 안정적인 접근 지점 제공
- **Ingress**: 외부 HTTP/HTTPS 요청을 내부 서비스로 라우팅
- **ConfigMap/Secret**: 설정과 민감 정보 분리
- **Horizontal Pod Autoscaler**: 부하에 따른 Pod 수 자동 조정
- **Liveness/Readiness Probe**: 장애 감지와 트래픽 투입 제어

API Gateway는 클라우드에서 관리형 서비스로도 제공된다. AWS API Gateway는 REST API, HTTP API, WebSocket API를 제공하며, Lambda, ECS, EKS, ALB 등과 연동할 수 있다. AWS Application Load Balancer도 경로 기반 라우팅을 지원하므로 간단한 API 라우팅에 활용할 수 있다.

Service Discovery는 Kubernetes에서는 기본적으로 Service와 CoreDNS를 통해 제공된다. AWS ECS에서는 Cloud Map과 통합하여 서비스 이름 기반 검색을 지원할 수 있다. 서비스 메시(Service Mesh)를 사용하는 경우 Envoy 기반의 Istio, Linkerd, AWS App Mesh 등이 서비스 간 통신을 프록시 계층에서 제어한다. 서비스 메시를 사용하면 mTLS, 트래픽 분할, 재시도, 타임아웃, 관측성 등을 애플리케이션 코드와 분리해 관리할 수 있다.

SAGA 패턴은 클라우드의 메시징 서비스와 잘 어울린다. AWS SQS, SNS, EventBridge, Kafka, Google Pub/Sub 같은 이벤트 기반 인프라를 사용하면 서비스 간 결합도를 낮출 수 있다. 예를 들어 주문 서비스가 `OrderCreated` 이벤트를 발행하면 결제 서비스가 결제를 수행하고 `PaymentCompleted` 이벤트를 발행한다. 이후 재고 서비스가 재고 차감을 수행하는 식이다.

AWS Step Functions는 Orchestration 방식의 SAGA 구현에 활용될 수 있다. 각 단계를 상태 머신으로 정의하고, 실패 시 보상 작업으로 전환하는 흐름을 구성할 수 있다. 다만 모든 워크플로우를 중앙 오케스트레이션으로 처리하면 복잡도와 비용, 상태 관리 방식에 대한 검토가 필요하다.

---

---

## 보안 연결

MSA에서는 서비스 수가 증가하면서 공격 표면도 함께 증가한다. 모놀리식에서는 외부 진입점이 비교적 제한적인 경우가 많지만, MSA에서는 API Gateway, 내부 서비스 API, 메시지 브로커, 서비스 레지스트리, 관리 콘솔, 컨테이너 이미지 저장소 등 보호해야 할 지점이 많다.

API Gateway는 보안의 1차 방어선 역할을 한다. 일반적으로 인증, 인가, 요청 제한, IP 제한, WAF 연동, TLS 종료, 요청 크기 제한, CORS 정책 등을 담당한다. JWT를 사용하는 경우 서명 검증, 만료 시간 확인, issuer와 audience 검증이 필요하다. 단순히 토큰 존재 여부만 확인하는 것은 안전하지 않다.

서비스 간 통신 보안도 중요하다. 내부 네트워크라고 해서 신뢰하면 안 되며, Zero Trust 관점에서 서비스 간 인증과 암호화를 적용하는 것이 좋다. Kubernetes나 서비스 메시 환경에서는 mTLS를 통해 서비스 간 통신을 암호화하고 상호 인증할 수 있다. 또한 각 서비스는 필요한 권한만 가져야 하며, 데이터베이스 계정도 서비스별로 분리하는 것이 바람직하다.

Service Discovery와 관련해서는 서비스 레지스트리 오염 문제가 있다. 공격자가 악성 인스턴스를 레지스트리에 등록하면 정상 서비스가 해당 인스턴스로 트래픽을 보낼 수 있다. 따라서 서비스 등록 권한을 제한하고, 헬스 체크와 인증된 등록 절차를 사용해야 한다.

SAGA 패턴에서는 중복 메시지 처리와 보상 트랜잭션의 안전성이 중요하다. 메시지 브로커는 장애 상황에서 동일 이벤트를 여러 번 전달할 수 있으므로, 각 서비스는 멱등성(idempotency)을 보장해야 한다. 예를 들어 동일한 결제 요청이 두 번 도착해도 결제가 한 번만 처리되도록 idempotency key를 사용할 수 있다. 보상 트랜잭션도 실패할 수 있으므로 재시도 정책, 데드레터 큐, 수동 복구 절차가 필요하다.

컨테이너 보안도 MSA에서 중요하다. 이미지에 민감 정보를 포함하지 않고, 최소 권한 사용자로 실행하며, 불필요한 패키지를 제거하고, 취약점 스캔을 수행해야 한다. Kubernetes에서는 RBAC, NetworkPolicy, Secret 관리, Pod Security 설정, 이미지 서명 및 검증 등을 검토할 수 있다.

대표적인 보안 모범 사례는 다음과 같다.

- API Gateway에서 인증·인가·Rate Limiting 적용
- 서비스 간 mTLS 또는 안전한 네트워크 통신 사용
- 서비스별 최소 권한 원칙 적용
- Secret을 환경 변수나 코드에 하드코딩하지 않기
- 메시지 처리 시 멱등성 보장
- 내부 API도 인증과 접근 제어 적용
- 중앙 로그와 감사 로그 수집
- 컨테이너 이미지 취약점 스캔
- Kubernetes NetworkPolicy로 서비스 간 통신 범위 제한

---

---

## 면접 질문

**Q1. 모놀리식 아키텍처와 마이크로서비스 아키텍처의 차이는 무엇인가요?**  
> 핵심 답변: 모놀리식은 하나의 코드베이스와 배포 단위로 전체 기능을 제공하며 개발 초기에는 단순하지만 규모가 커질수록 결합도와 배포 부담이 커진다. MSA는 기능을 독립 서비스로 분리해 개별 배포와 확장이 가능하지만, 네트워크 통신, 분산 트랜잭션, 관측성, 운영 복잡도가 증가한다.

**Q2. API Gateway의 역할은 무엇인가요?**  
> 핵심 답변: 클라이언트의 단일 진입점으로서 요청 라우팅, 인증·인가, Rate Limiting, 로깅, 모니터링, SSL/TLS 종료, 응답 집계, API 버전 관리 등을 수행한다. 단, 비즈니스 로직을 과도하게 넣으면 병목과 단일 장애 지점이 될 수 있다.

**Q3. Service Discovery가 필요한 이유는 무엇인가요?**  
> 핵심 답변: 클라우드와 컨테이너 환경에서는 서비스 인스턴스가 동적으로 생성·삭제되고 IP가 자주 바뀔 수 있다. Service Discovery는 서비스 이름을 기반으로 현재 사용 가능한 인스턴스를 찾게 해주며, Kubernetes Service/CoreDNS, AWS Cloud Map 등이 대표적인 구현 방식이다.

**Q4. SAGA 패턴이란 무엇이며 왜 사용하나요?**  
> 핵심 답변: 여러 서비스에 걸친 분산 트랜잭션을 각 서비스의 로컬 트랜잭션과 보상 트랜잭션으로 나누어 처리하는 패턴이다. 2PC 같은 강한 일관성 방식 대신 최종 일관성을 목표로 하며, 주문-결제-재고 같은 비즈니스 흐름에서 사용된다.

**Q5. Choreography SAGA와 Orchestration SAGA의 차이는 무엇인가요?**  
> 핵심 답변: Choreography는 각 서비스가 이벤트를 발행·구독하며 자율적으로 다음 단계를 수행한다. 결합도는 낮지만 전체 흐름 추적이 어려울 수 있다. Orchestration은 중앙 Orchestrator가 흐름을 제어하므로 가시성이 좋지만, Orchestrator에 의존성이 생긴다.

---

---

## 관련 개념

- [[모놀리식 아키텍처]] - MSA와 비교되는 단일 배포 단위 아키텍처이다.
- [[API Gateway]] - MSA에서 클라이언트 요청의 단일 진입점 역할을 한다.
- [[Service Discovery]] - 동적으로 변하는 서비스 인스턴스를 찾기 위한 핵심 메커니즘이다.
- [[SAGA 패턴]] - MSA 환경에서 분산 트랜잭션을 관리하기 위한 대표 패턴이다.
- [[분산 트랜잭션]] - 여러 서비스와 데이터 저장소에 걸친 일관성 문제와 연결된다.
- [[최종 일관성]] - SAGA와 이벤트 기반 아키텍처에서 자주 사용되는 데이터 일관성 모델이다.
- [[이벤트 기반 아키텍처]] - 서비스 간 결합도를 낮추고 비동기 처리를 가능하게 한다.
- [[서비스 메시]] - 서비스 간 통신, 보안, 관측성을 인프라 계층에서 제어한다.
- [[Kubernetes Service]] - Kubernetes에서 Service Discovery와 로드밸런싱을 제공한다.
- [[Circuit Breaker]] - 서비스 장애 전파를 막기 위한 회복성 패턴이다.
- [[Idempotency]] - 중복 요청이나 중복 이벤트 처리 시 안전성을 보장하는 개념이다.
- [[CQRS]] - 읽기와 쓰기 모델을 분리해 복잡한 도메인과 이벤트 기반 시스템에서 활용된다.
