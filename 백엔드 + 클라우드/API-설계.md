---
date: 2026-05-15
category: 백엔드 - 아키텍처
topic: API 설계
subtopic: RESTful API 성숙도 모델, GraphQL, gRPC 특징 비교
tags: [CS, 백엔드---아키텍처, study]
---

# API 설계 - RESTful API 성숙도 모델, GraphQL, gRPC 특징 비교

## 핵심 개념

API 설계는 클라이언트와 서버가 어떤 방식으로 데이터를 요청하고 응답할지 정의하는 백엔드 아키텍처의 핵심 영역이다. 좋은 API는 단순히 “동작하는 엔드포인트”를 만드는 것이 아니라, 자원의 표현 방식, 통신 규약, 버전 관리, 오류 처리, 인증/인가, 성능 최적화, 확장성까지 고려한다. 대표적인 API 설계 방식으로는 RESTful API, GraphQL, gRPC가 있다.

RESTful API는 HTTP의 자원 중심 모델을 활용하여 URI로 리소스를 표현하고, GET, POST, PUT, PATCH, DELETE 같은 HTTP 메서드로 행위를 나타내는 방식이다. RESTful API의 성숙도를 설명할 때는 흔히 Richardson Maturity Model을 사용한다. 이 모델은 API가 단순히 HTTP를 전송 수단으로만 쓰는 수준에서, 리소스, HTTP 메서드, 하이퍼미디어까지 활용하는 수준으로 발전하는 단계를 설명한다.

GraphQL은 클라이언트가 필요한 데이터 구조를 쿼리로 명시하면 서버가 그에 맞는 응답을 반환하는 API 쿼리 언어이자 런타임이다. REST에서 흔히 발생하는 over-fetching, under-fetching 문제를 줄이는 데 유리하다. 반면 서버 쪽 스키마 설계, 쿼리 복잡도 제어, 캐싱 전략이 중요해진다.

gRPC는 Google에서 공개한 고성능 RPC 프레임워크로, Protocol Buffers를 인터페이스 정의 언어와 직렬화 포맷으로 주로 사용하며 HTTP/2 위에서 동작한다. REST나 GraphQL이 주로 자원 또는 데이터 질의 중심이라면, gRPC는 원격 함수 호출에 가깝다. 낮은 지연 시간, 양방향 스트리밍, 명확한 계약 기반 통신이 필요한 마이크로서비스 간 통신에 자주 사용된다.

이 세 가지 방식은 서로 대체 관계라기보다 사용 목적이 다르다. 외부 공개 API에는 REST가 여전히 널리 쓰이고, 복잡한 화면 데이터 조합이 많은 프론트엔드 중심 서비스에는 GraphQL이 적합할 수 있으며, 내부 서비스 간 고성능 통신에는 gRPC가 강점을 가진다. API 설계에서 중요한 것은 특정 기술을 무조건 선택하는 것이 아니라, 클라이언트 특성, 네트워크 환경, 운영 복잡도, 보안 요구사항, 팀의 유지보수 능력을 함께 고려하는 것이다.

---

## 내부 동작 원리

## 1. RESTful API 성숙도 모델

RESTful API 성숙도 모델은 API가 REST의 제약 조건을 얼마나 잘 활용하는지 단계적으로 설명한다. 일반적으로 다음과 같이 구분한다.

### Level 0: HTTP를 단순 터널로 사용

HTTP를 단순 전송 수단으로만 사용하고, 모든 요청을 하나의 엔드포인트로 보내는 방식이다.

```http
POST /api
{
  "action": "getUser",
  "userId": 1
}
```

이 방식은 RPC 스타일에 가깝고, URI나 HTTP 메서드의 의미를 충분히 활용하지 않는다.

### Level 1: 리소스 도입

URI를 통해 자원을 구분한다.

```http
POST /users/1/get
POST /orders/10/cancel
```

자원은 분리되지만, 여전히 HTTP 메서드를 의미적으로 활용하지 못할 수 있다.

### Level 2: HTTP 메서드 활용

HTTP 메서드와 상태 코드를 의미에 맞게 사용한다.

```http
GET /users/1
POST /users
PUT /users/1
PATCH /users/1
DELETE /users/1
```

예를 들어 `GET`은 조회, `POST`는 생성, `PUT`은 전체 교체, `PATCH`는 부분 수정, `DELETE`는 삭제에 사용한다. 응답에는 `200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found` 같은 HTTP 상태 코드를 활용한다.

### Level 3: HATEOAS

HATEOAS는 Hypermedia As The Engine Of Application State의 약자로, 응답 안에 클라이언트가 다음에 수행할 수 있는 행위의 링크를 포함하는 방식이다.

```json
{
  "id": 1,
  "name": "Alice",
  "_links": {
    "self": { "href": "/users/1" },
    "orders": { "href": "/users/1/orders" },
    "update": { "href": "/users/1" }
  }
}
```

클라이언트는 하드코딩된 URI에 덜 의존하고, 서버가 제공하는 링크를 따라 다음 상태로 이동할 수 있다. 다만 실제 산업 현장에서는 Level 2 수준의 REST API가 많이 사용되며, HATEOAS까지 엄격하게 적용하는 경우는 상대적으로 제한적이다.

## 2. REST 요청 흐름

```text
Client
  |
  | HTTP GET /users/1
  v
API Gateway / Load Balancer
  |
  v
Backend Controller
  |
  v
Service Layer
  |
  v
Repository / Database
  |
  v
JSON Response
```

1. 클라이언트가 URI와 HTTP 메서드로 요청한다.
2. API Gateway나 Load Balancer가 요청을 적절한 서버로 전달한다.
3. 백엔드 컨트롤러가 라우팅한다.
4. 서비스 계층에서 비즈니스 로직을 수행한다.
5. 데이터베이스나 외부 시스템을 호출한다.
6. JSON, XML 등 표현 형식으로 응답한다.

## 3. GraphQL 동작 원리

GraphQL은 하나의 엔드포인트를 두고, 클라이언트가 필요한 필드 구조를 쿼리로 요청한다.

```graphql
query {
  user(id: "1") {
    id
    name
    orders {
      id
      totalPrice
    }
  }
}
```

응답은 요청한 구조와 유사한 형태로 반환된다.

```json
{
  "data": {
    "user": {
      "id": "1",
      "name": "Alice",
      "orders": [
        {
          "id": "100",
          "totalPrice": 30000
        }
      ]
    }
  }
}
```

GraphQL 서버 내부에서는 일반적으로 다음 흐름으로 동작한다.

```text
Client
  |
  | GraphQL Query
  v
GraphQL Endpoint
  |
  v
Parser
  |
  v
Validation against Schema
  |
  v
Resolver Execution
  |
  v
Data Sources
  |
  v
Response Assembly
```

1. 클라이언트가 GraphQL 쿼리 또는 뮤테이션을 전송한다.
2. 서버는 쿼리를 파싱한다.
3. 쿼리가 스키마에 맞는지 검증한다.
4. 각 필드에 연결된 resolver를 실행한다.
5. resolver는 데이터베이스, REST API, gRPC 서비스 등에서 데이터를 가져온다.
6. 요청한 필드 구조에 맞게 응답을 조립한다.

GraphQL의 핵심은 스키마와 resolver이다. 스키마는 가능한 타입, 필드, 쿼리, 뮤테이션을 정의한다. resolver는 해당 필드를 실제 데이터로 채우는 함수다.

## 4. gRPC 동작 원리

gRPC는 `.proto` 파일에 서비스와 메시지를 정의한다.

```proto
service UserService {
  rpc GetUser (GetUserRequest) returns (UserResponse);
}

message GetUserRequest {
  string id = 1;
}

message UserResponse {
  string id = 1;
  string name = 2;
}
```

이 정의 파일을 기반으로 서버와 클라이언트 코드를 생성한다. 클라이언트는 로컬 메서드를 호출하는 것처럼 `GetUser`를 호출하지만, 실제로는 네트워크를 통해 서버의 RPC 메서드가 실행된다.

```text
Client Stub
  |
  | Protobuf Binary Message over HTTP/2
  v
gRPC Server
  |
  v
Service Implementation
  |
  v
Business Logic / Database
  |
  v
Protobuf Response
```

gRPC는 네 가지 통신 방식을 지원한다.

| 방식 | 설명 |
|---|---|
| Unary RPC | 요청 1개, 응답 1개 |
| Server Streaming RPC | 요청 1개, 응답 스트림 |
| Client Streaming RPC | 요청 스트림, 응답 1개 |
| Bidirectional Streaming RPC | 요청과 응답 모두 스트림 |

HTTP/2의 멀티플렉싱, 헤더 압축, 스트림 기능을 활용할 수 있어 다수의 서비스 간 통신이나 실시간성이 필요한 내부 통신에 적합하다.

## 5. REST, GraphQL, gRPC 비교

| 항목 | REST | GraphQL | gRPC |
|---|---|---|---|
| 설계 중심 | 리소스 | 클라이언트가 요청하는 데이터 그래프 | 원격 프로시저 호출 |
| 일반 포맷 | JSON | JSON | Protocol Buffers |
| 전송 | 주로 HTTP | 주로 HTTP | HTTP/2 |
| 계약 | OpenAPI 등으로 정의 가능 | 스키마 중심 | `.proto` 중심 |
| 브라우저 친화성 | 높음 | 높음 | 직접 사용은 제한적일 수 있음 |
| 캐싱 | HTTP 캐싱과 잘 맞음 | 별도 전략 필요 | HTTP 캐싱과는 덜 직접적 |
| 성능 | 보편적이고 충분히 효율적 | 쿼리 설계에 따라 달라짐 | 바이너리 직렬화와 HTTP/2로 고성능에 유리 |
| 적합한 영역 | 공개 API, CRUD API | 복잡한 화면 데이터 조합 | 내부 마이크로서비스 통신 |

---

---

## 실제 시스템 연결

## 1. Linux 환경에서의 API 서버

Linux 서버에서는 REST, GraphQL, gRPC 서버가 모두 일반적인 프로세스로 실행된다. 예를 들어 Node.js, Java Spring Boot, Go, Python FastAPI, Rust 기반 서버 등이 Linux 위에서 포트를 열고 요청을 수신한다.

```text
Linux Host
 ├─ Nginx : 80/443 포트 수신
 ├─ REST API Server : 8080
 ├─ GraphQL Server : 4000
 └─ gRPC Server : 50051
```

Nginx는 외부 HTTP/HTTPS 요청을 받아 내부 API 서버로 프록시할 수 있다. REST와 GraphQL은 일반적인 HTTP reverse proxy 구성이 쉽다. gRPC는 HTTP/2 기반이므로 Nginx에서 gRPC 프록시 설정을 별도로 구성해야 한다.

## 2. Nginx와 API 라우팅

REST API의 경우 경로 기반 라우팅이 직관적이다.

```text
/api/users     -> user-service
/api/orders    -> order-service
/api/payments  -> payment-service
```

GraphQL은 보통 `/graphql` 같은 단일 엔드포인트를 사용한다.

```text
/graphql -> graphql-gateway
```

이 경우 Nginx는 쿼리 내부 필드까지 이해하지 못하고, 대부분 요청을 GraphQL 서버로 전달한다. 세부적인 권한 제어, 필드별 제한, 쿼리 복잡도 제어는 GraphQL 애플리케이션 레이어에서 수행해야 한다.

gRPC의 경우 서비스 메서드 단위로 호출된다.

```text
/UserService/GetUser
/OrderService/CreateOrder
```

gRPC 서버와 프록시 간에는 HTTP/2와 TLS 설정이 중요하다.

## 3. AWS에서의 실제 연결

AWS에서는 다음과 같은 조합이 흔히 사용된다.

- REST API: Amazon API Gateway, Application Load Balancer, AWS Lambda, ECS, EKS, EC2
- GraphQL: AWS AppSync, Lambda, DynamoDB, RDS, OpenSearch
- gRPC: Application Load Balancer, Network Load Balancer, ECS, EKS, EC2 기반 서비스

Amazon API Gateway는 REST API와 HTTP API 구성에 사용될 수 있고, 인증, 사용량 제한, 로깅, CORS 설정을 제공한다. AWS AppSync는 관리형 GraphQL 서비스로, GraphQL 스키마를 기반으로 DynamoDB, Lambda, HTTP 데이터 소스 등을 연결할 수 있다.

마이크로서비스 내부 통신에서는 gRPC를 사용하고, 외부 클라이언트에는 REST 또는 GraphQL을 제공하는 구조도 자주 사용된다.

```text
Mobile/Web Client
      |
      v
REST or GraphQL API
      |
      v
Backend For Frontend
      |
      v
gRPC Internal Services
      |
      v
Database / Cache / Message Queue
```

## 4. GCP에서의 실제 연결

GCP 환경에서는 Cloud Run, GKE, Compute Engine에서 REST, GraphQL, gRPC 서비스를 실행할 수 있다. gRPC는 Google 생태계에서 널리 사용되는 통신 방식이며, Protocol Buffers와 함께 서비스 간 계약을 명확히 정의하는 데 적합하다.

```text
Client
  |
  v
Cloud Load Balancing
  |
  v
Cloud Run / GKE Service
  |
  v
REST, GraphQL, or gRPC Server
```

Cloud Load Balancing, API Gateway, Cloud Endpoints 등을 활용하여 인증, 라우팅, 관측성을 구성할 수 있다.

## 5. 실제 선택 예시

### REST가 적합한 경우

- 외부 파트너에게 공개하는 API
- CRUD 중심 서비스
- HTTP 캐싱, CDN 연동이 중요한 API
- 다양한 클라이언트가 쉽게 사용할 수 있어야 하는 경우

### GraphQL이 적합한 경우

- 모바일 앱처럼 네트워크 비용이 중요한 환경
- 한 화면에서 여러 리소스의 일부 필드만 필요한 경우
- 프론트엔드 요구사항 변경이 잦은 경우
- 여러 백엔드 API를 하나의 데이터 그래프로 통합하고 싶은 경우

### gRPC가 적합한 경우

- 내부 마이크로서비스 간 고성능 통신
- 명확한 인터페이스 계약이 필요한 경우
- 스트리밍 통신이 필요한 경우
- 다국어 서비스 간 통신이 필요한 경우

---

---

## 클라우드 연결

## 1. Docker와 API 설계

REST, GraphQL, gRPC 서버는 모두 컨테이너로 패키징할 수 있다. Dockerfile을 통해 런타임과 의존성을 고정하고, 동일한 이미지를 개발, 테스트, 운영 환경에서 실행할 수 있다.

```text
Docker Image
 ├─ Application Code
 ├─ Runtime
 ├─ Dependency
 └─ API Server
```

REST와 GraphQL은 보통 HTTP 포트를 노출한다.

```yaml
ports:
  - "8080:8080"
```

gRPC 서버는 일반적으로 별도 포트를 사용한다.

```yaml
ports:
  - "50051:50051"
```

중요한 점은 컨테이너화가 API 설계 자체를 바꾸지는 않지만, 서비스 배포 단위와 네트워크 경계를 명확히 만든다는 것이다. 컨테이너 간 통신에서는 서비스 이름 기반 DNS, 로드밸런싱, 헬스체크가 중요하다.

## 2. Kubernetes와 API

Kubernetes에서는 API 서버를 Pod로 실행하고 Service로 노출한다.

```text
Client
  |
  v
Ingress
  |
  v
Kubernetes Service
  |
  v
Pods
```

REST와 GraphQL은 Ingress Controller를 통해 HTTP 라우팅하기 쉽다.

```text
/api     -> rest-service
/graphql -> graphql-service
```

gRPC도 Kubernetes에서 사용할 수 있지만, Ingress Controller와 Load Balancer가 HTTP/2 및 gRPC 프록시를 지원해야 한다. Envoy, Istio, Linkerd 같은 서비스 메시 도구는 gRPC 트래픽 관측, mTLS, 로드밸런싱에 활용될 수 있다.

## 3. API Gateway와 서비스 메시

클라우드 아키텍처에서는 외부 트래픽과 내부 트래픽을 구분하는 것이 중요하다.

```text
External Client
      |
      v
API Gateway
      |
      v
REST / GraphQL Edge API
      |
      v
Service Mesh
      |
      v
gRPC Internal Services
```

API Gateway는 주로 다음 역할을 수행한다.

- 인증 및 인가 연동
- 요청 제한
- CORS 처리
- 라우팅
- 로깅
- 요청/응답 변환
- API 버전 관리

서비스 메시의 주요 역할은 다음과 같다.

- 서비스 간 mTLS
- 트래픽 라우팅
- 재시도, 타임아웃, 서킷 브레이커
- 분산 추적
- 서비스 간 정책 적용

REST나 GraphQL은 외부 API 경계에 배치하고, gRPC는 내부 서비스 간 통신에 배치하는 구조가 클라우드 네이티브 아키텍처에서 자주 사용된다.

## 4. AWS 서비스와의 연결

### REST

- Amazon API Gateway로 REST API 또는 HTTP API 제공
- AWS Lambda와 연결하여 서버리스 API 구성
- ECS/EKS/EC2의 백엔드 서비스 앞단에 ALB 배치
- CloudFront와 결합하여 정적 콘텐츠 및 API 응답 캐싱 가능

### GraphQL

- AWS AppSync로 관리형 GraphQL API 제공
- DynamoDB, Lambda, HTTP 엔드포인트 등과 연결 가능
- Cognito, IAM 등과 연동하여 인증/인가 구성 가능

### gRPC

- ECS, EKS, EC2에서 gRPC 서버 실행
- Application Load Balancer 또는 Network Load Balancer를 통해 트래픽 전달 가능
- 서비스 간 통신에서는 AWS Cloud Map, App Mesh 등을 함께 사용할 수 있음

## 5. 운영 관점

클라우드에서 API를 운영할 때는 단순히 요청을 처리하는 것보다 다음 항목이 중요하다.

| 운영 항목 | REST | GraphQL | gRPC |
|---|---|---|---|
| 헬스체크 | HTTP endpoint | HTTP endpoint | gRPC health checking 또는 별도 endpoint |
| 로깅 | 경로/메서드 기반 | 쿼리/operation 기반 | 서비스/메서드 기반 |
| 모니터링 | status code, latency | resolver latency, query complexity | RPC latency, status code |
| 배포 | API 버전 관리 중요 | 스키마 호환성 중요 | proto 호환성 중요 |
| 장애 분석 | URI 단위 추적 | resolver 단위 추적 필요 | method 단위 추적 필요 |

---

---

## 보안 연결

## 1. REST 보안 이슈와 모범 사례

REST API는 HTTP 기반이므로 일반적인 웹 보안 위협에 노출된다.

주요 보안 이슈:

- 인증 없는 엔드포인트 노출
- IDOR, 즉 Insecure Direct Object Reference
- 과도한 데이터 노출
- 잘못된 HTTP 메서드 허용
- CORS 오설정
- 입력값 검증 부족
- Rate limiting 부재
- 민감 정보가 URL 쿼리 파라미터에 포함되는 문제

모범 사례:

- 모든 민감 API는 HTTPS 사용
- 인증과 인가를 분리하여 설계
- 리소스 접근 권한을 서버에서 검증
- 최소한의 필드만 응답
- HTTP 메서드별 권한 제어
- API Gateway 또는 애플리케이션에서 rate limit 적용
- 요청 본문과 파라미터 검증
- 에러 메시지에 내부 구현 정보 노출 금지
- 보안 헤더와 CORS 정책을 명확히 설정

REST에서 특히 중요한 것은 “사용자가 해당 리소스에 접근할 권한이 있는가”를 매 요청마다 확인하는 것이다.

```http
GET /users/123/orders
Authorization: Bearer <token>
```

토큰이 유효하더라도, 요청자가 `user 123`의 주문을 볼 권한이 있는지 별도로 확인해야 한다.

## 2. GraphQL 보안 이슈와 모범 사례

GraphQL은 단일 엔드포인트를 사용하기 때문에 전통적인 URL 기반 보안 정책만으로는 충분하지 않다. 쿼리 내부의 필드와 resolver 단위 권한 제어가 중요하다.

주요 보안 이슈:

- 과도하게 깊은 중첩 쿼리로 인한 서버 부하
- 복잡한 쿼리를 이용한 DoS
- introspection을 통한 스키마 정보 노출
- 필드 단위 권한 검증 누락
- resolver에서 발생하는 N+1 쿼리 문제로 인한 성능 저하
- 에러 메시지를 통한 내부 구조 노출

예시:

```graphql
query {
  user(id: "1") {
    orders {
      items {
        product {
          reviews {
            author {
              orders {
                items {
                  product {
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

이런 깊은 쿼리는 서버에 큰 부하를 줄 수 있다.

모범 사례:

- 쿼리 depth 제한
- 쿼리 complexity 계산 및 제한
- rate limiting
- persisted query 사용
- 필드 및 resolver 단위 인가
- 운영 환경에서 introspection 허용 여부 검토
- 민감 필드 마스킹
- DataLoader 같은 배치 로딩 패턴 활용
- 에러 메시지 표준화

GraphQL에서는 “스키마에 보이는 필드가 모두 모든 사용자에게 허용되는 것은 아니다”라는 점을 명확히 해야 한다.

## 3. gRPC 보안 이슈와 모범 사례

gRPC는 HTTP/2 위에서 동작하며, 내부 서비스 간 통신에 자주 쓰인다. 내부망이라고 해서 안전하다고 가정하면 안 된다.

주요 보안 이슈:

- TLS 미사용으로 인한 트래픽 노출
- 서비스 간 인증 부재
- proto 파일에 정의된 메서드의 과도한 노출
- 메타데이터를 통한 민감 정보 노출
- 메시지 크기 제한 미설정으로 인한 리소스 고갈
- deadline/timeout 미설정으로 인한 장애 전파

모범 사례:

- TLS 또는 mTLS 사용
- 서비스 간 인증 및 인가 적용
- gRPC interceptor로 인증, 로깅, 정책 검증 공통화
- 메시지 크기 제한 설정
- deadline과 timeout 설정
- 에러 응답에 내부 정보 노출 금지
- proto 필드 변경 시 하위 호환성 고려
- 서비스 메시를 통한 mTLS와 정책 관리

gRPC에서는 HTTP 상태 코드 대신 gRPC status code를 사용한다. 인증 실패, 권한 부족, 잘못된 요청, 타임아웃 등을 명확히 구분해야 운영과 보안 분석에 도움이 된다.

## 4. 인증과 인가 비교

| 항목 | REST | GraphQL | gRPC |
|---|---|---|---|
| 인증 전달 | Authorization 헤더 | Authorization 헤더 | Metadata |
| 인가 단위 | 리소스/메서드 | 필드/resolver | 서비스/메서드 |
| 주요 위험 | IDOR, CORS, 과다 노출 | 쿼리 복잡도, 필드 권한 누락 | 내부망 신뢰, mTLS 부재 |
| 방어 전략 | RBAC/ABAC, rate limit | complexity limit, field auth | mTLS, interceptor |

## 5. API 보안 설계 원칙

API 유형과 관계없이 공통적으로 적용해야 할 원칙은 다음과 같다.

- 기본적으로 모든 요청은 신뢰하지 않는다.
- 인증된 사용자라도 모든 리소스 접근 권한이 있는 것은 아니다.
- 클라이언트 입력은 반드시 검증한다.
- 민감 정보는 응답에서 제외하거나 마스킹한다.
- 장애 상황에서도 내부 구현 정보를 노출하지 않는다.
- 로그에는 토큰, 비밀번호, 개인정보 등 민감 정보를 남기지 않는다.
- 타임아웃, 재시도, rate limit을 설정하여 장애 전파를 줄인다.
- API 계약 변경은 하위 호환성을 고려한다.

---

---

## 면접 질문

**Q1. RESTful API 성숙도 모델의 각 단계는 무엇인가요?**  
> 핵심 답변: Level 0은 HTTP를 단순 전송 수단으로 사용하는 단계, Level 1은 URI로 리소스를 구분하는 단계, Level 2는 HTTP 메서드와 상태 코드를 의미 있게 사용하는 단계, Level 3은 HATEOAS를 통해 응답에 다음 가능한 상태 전이 링크를 포함하는 단계다. 실무에서는 Level 2 수준이 많이 사용된다.

**Q2. REST와 GraphQL의 가장 큰 차이는 무엇인가요?**  
> 핵심 답변: REST는 서버가 정의한 리소스 엔드포인트를 클라이언트가 호출하는 방식이고, GraphQL은 클라이언트가 필요한 데이터 구조를 쿼리로 명시하는 방식이다. REST는 HTTP 캐싱과 리소스 모델에 강점이 있고, GraphQL은 over-fetching과 under-fetching을 줄이는 데 유리하다.

**Q3. GraphQL에서 보안상 주의해야 할 점은 무엇인가요?**  
> 핵심 답변: 단일 엔드포인트이므로 URL 기반 접근 제어만으로는 부족하다. 쿼리 깊이 제한, complexity 제한, rate limiting, resolver 및 필드 단위 인가가 필요하다. 또한 introspection 허용 여부, 에러 메시지 노출, N+1 쿼리 문제도 관리해야 한다.

**Q4. gRPC가 마이크로서비스 내부 통신에 적합한 이유는 무엇인가요?**  
> 핵심 답변: Protocol Buffers 기반의 명확한 계약, 바이너리 직렬화, HTTP/2의 멀티플렉싱과 스트리밍 지원, 다양한 언어 코드 생성이 장점이다. 서비스 간 통신에서 낮은 지연 시간과 강한 인터페이스 계약이 필요한 경우 적합하다.

**Q5. REST, GraphQL, gRPC 중 어떤 것을 선택할지 판단하는 기준은 무엇인가요?**  
> 핵심 답변: 외부 공개 API와 CRUD 중심 서비스에는 REST가 적합하다. 복잡한 화면 데이터 조합과 클라이언트 주도 데이터 조회가 중요하면 GraphQL이 유리하다. 내부 서비스 간 고성능 통신, 스트리밍, 명확한 계약이 필요하면 gRPC가 적합하다. 보안, 캐싱, 운영 복잡도, 팀 역량도 함께 고려해야 한다.

---

---

## 관련 개념

- [[REST]] - 리소스 중심 API 설계 방식이며 RESTful API 성숙도 모델의 기반이다.
- [[Richardson Maturity Model]] - REST API가 HTTP와 하이퍼미디어를 얼마나 활용하는지 설명하는 성숙도 모델이다.
- [[HATEOAS]] - REST 성숙도 Level 3의 핵심 개념으로, 응답에 상태 전이 링크를 포함한다.
- [[GraphQL]] - 클라이언트가 필요한 데이터 구조를 직접 질의하는 API 쿼리 언어다.
- [[gRPC]] - Protocol Buffers와 HTTP/2를 활용하는 고성능 RPC 프레임워크다.
- [[Protocol Buffers]] - gRPC에서 주로 사용하는 인터페이스 정의 및 직렬화 방식이다.
- [[HTTP/2]] - gRPC의 기반 전송 프로토콜로 멀티플렉싱과 스트리밍을 지원한다.
- [[API Gateway]] - 인증, 라우팅, rate limiting, 로깅 등 API 경계 기능을 제공한다.
- [[Backend for Frontend]] - 클라이언트별 요구사항에 맞춘 API 계층으로 REST나 GraphQL과 함께 사용된다.
- [[Service Mesh]] - 마이크로서비스 간 통신에서 mTLS, 라우팅, 관측성을 제공한다.
- [[OpenAPI]] - REST API 명세를 문서화하고 계약으로 관리하는 데 사용된다.
- [[Schema Design]] - GraphQL과 gRPC에서 API 계약과 호환성을 결정하는 핵심 설계 활동이다.
