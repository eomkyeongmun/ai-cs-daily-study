---
date: 2026-05-30
category: 백엔드 - 인프라
topic: Kubernetes
subtopic: K8s 아키텍처(Master/Worker), Pod, Deployment, Service, Ingress
tags: [CS, 백엔드---인프라, study]
---

# Kubernetes - K8s 아키텍처(Master/Worker), Pod, Deployment, Service, Ingress

## 핵심 개념

Kubernetes(K8s)는 컨테이너화된 애플리케이션을 여러 서버에 걸쳐 배포, 확장, 복구, 네트워킹, 설정 관리까지 자동화하는 컨테이너 오케스트레이션 플랫폼이다. K8s 아키텍처는 크게 **Control Plane(Master로 불리던 영역)** 과 **Worker Node** 로 나뉜다. Control Plane은 클러스터의 “두뇌” 역할을 하며, 사용자가 선언한 원하는 상태(Desired State)를 저장하고 실제 상태(Current State)가 그에 맞도록 조정한다. Worker Node는 실제 애플리케이션 컨테이너가 실행되는 서버이다.

Kubernetes에서 가장 작은 배포 단위는 **Pod** 이다. Pod는 하나 이상의 컨테이너를 감싸는 논리적 실행 단위이며, 같은 Pod 안의 컨테이너들은 네트워크 네임스페이스와 스토리지 볼륨을 공유할 수 있다. 일반적으로 애플리케이션 컨테이너 하나를 하나의 Pod에 배치하지만, 사이드카 패턴처럼 보조 컨테이너를 함께 배치하기도 한다.

**Deployment** 는 Pod를 직접 관리하기보다, 원하는 개수의 Pod가 항상 실행되도록 선언하고 롤링 업데이트, 롤백, ReplicaSet 관리를 제공하는 상위 리소스다. **Service** 는 Pod의 IP가 변경되어도 안정적인 접근 지점을 제공하는 네트워크 추상화다. **Ingress** 는 HTTP/HTTPS 트래픽을 클러스터 내부 Service로 라우팅하기 위한 규칙 객체이며, 실제 동작을 위해서는 Nginx Ingress Controller, AWS Load Balancer Controller 같은 Ingress Controller가 필요하다.

K8s가 중요한 이유는 단순히 컨테이너를 실행하는 수준을 넘어, 장애 복구, 무중단 배포, 자동 확장, 서비스 디스커버리, 선언형 인프라 관리를 표준화하기 때문이다. 현대 백엔드 인프라에서는 수십 개 이상의 마이크로서비스, 여러 환경, 복잡한 네트워크와 보안 요구사항을 다뤄야 하므로 Kubernetes는 클라우드 네이티브 시스템의 핵심 기반으로 사용된다.

---

---

## 내부 동작 원리

## 1. Kubernetes 전체 아키텍처

Kubernetes 클러스터는 다음과 같은 구조로 이해할 수 있다.

```text
사용자 / CI-CD
   |
   | kubectl apply / API 요청
   v
+------------------------------+
|        Control Plane         |
|------------------------------|
| kube-apiserver               |
| etcd                         |
| kube-scheduler               |
| kube-controller-manager      |
| cloud-controller-manager     |
+------------------------------+
              |
              | 노드 상태 감시 및 명령 전달
              v
+------------------------------+
|         Worker Node          |
|------------------------------|
| kubelet                      |
| kube-proxy                   |
| container runtime            |
| Pod / Container              |
+------------------------------+
```

### Control Plane 구성 요소

- **kube-apiserver**
  - Kubernetes API의 진입점이다.
  - `kubectl`, CI/CD 시스템, Controller, Scheduler 등이 모두 API Server를 통해 클러스터 상태를 조회하거나 변경한다.
  - 인증, 인가, Admission Control도 API Server 요청 흐름에서 수행된다.

- **etcd**
  - 클러스터의 상태 정보를 저장하는 분산 키-값 저장소다.
  - Pod, Service, Deployment, ConfigMap, Secret 등 Kubernetes 리소스의 상태가 저장된다.
  - etcd 데이터 손상이나 손실은 클러스터 운영에 치명적이므로 백업과 접근 제어가 중요하다.

- **kube-scheduler**
  - 새로 생성된 Pod 중 아직 Node가 배정되지 않은 Pod를 감지한다.
  - CPU, 메모리 요청량, Node 상태, taint/toleration, affinity/anti-affinity 등의 조건을 고려해 적절한 Worker Node를 선택한다.

- **kube-controller-manager**
  - 여러 Controller를 실행하는 컴포넌트다.
  - Deployment Controller, ReplicaSet Controller, Node Controller 등이 원하는 상태와 실제 상태를 지속적으로 비교하고 조정한다.

- **cloud-controller-manager**
  - 클라우드 제공자와 연동되는 컨트롤러를 실행한다.
  - 예를 들어 AWS, GCP, Azure 환경에서 LoadBalancer 타입 Service를 만들면 클라우드 로드밸런서 생성을 연동할 수 있다.

### Worker Node 구성 요소

- **kubelet**
  - 각 Worker Node에서 동작하는 에이전트다.
  - API Server로부터 자신에게 할당된 Pod 정보를 받아 컨테이너 런타임을 통해 컨테이너를 실행한다.
  - Pod 상태를 주기적으로 보고한다.

- **container runtime**
  - 실제 컨테이너를 생성하고 실행한다.
  - containerd, CRI-O 등이 대표적으로 사용된다.
  - Kubernetes는 CRI(Container Runtime Interface)를 통해 런타임과 통신한다.

- **kube-proxy**
  - Service의 가상 IP와 트래픽 전달 규칙을 노드에 설정한다.
  - 일반적으로 iptables 또는 IPVS 기반으로 Service 트래픽을 적절한 Pod로 전달한다.

---

## 2. Pod 동작 원리

Pod는 Kubernetes에서 스케줄링 가능한 최소 단위다. Pod 안의 컨테이너들은 다음을 공유할 수 있다.

```text
Pod
├── Container A
├── Container B
├── Shared Network Namespace
│   └── 같은 Pod 내 컨테이너는 localhost로 통신 가능
└── Shared Volumes
    └── 컨테이너 간 파일 공유 가능
```

Pod가 생성되는 과정은 다음과 같다.

```text
1. 사용자가 Pod 또는 Deployment YAML 작성
2. kubectl apply 실행
3. kube-apiserver가 요청 검증 후 etcd에 저장
4. scheduler가 Pod를 실행할 Node 선택
5. kubelet이 해당 Node에서 Pod 생성 요청 수신
6. container runtime이 이미지 pull 후 컨테이너 실행
7. kubelet이 Pod 상태를 API Server에 보고
```

Pod는 자체적으로 영속적이지 않다. 장애나 업데이트로 재생성될 수 있고, 이때 Pod 이름과 IP가 바뀔 수 있다. 따라서 운영 환경에서는 Pod를 직접 노출하기보다 Deployment와 Service를 함께 사용한다.

---

## 3. Deployment 동작 원리

Deployment는 원하는 Pod 상태를 선언하는 리소스다. Deployment를 생성하면 내부적으로 ReplicaSet이 생성되고, ReplicaSet이 Pod 개수를 유지한다.

```text
Deployment
   |
   v
ReplicaSet
   |
   +--> Pod 1
   +--> Pod 2
   +--> Pod 3
```

예를 들어 `replicas: 3`으로 설정하면 Kubernetes는 항상 3개의 Pod가 실행되도록 유지한다. Pod 하나가 장애로 종료되면 ReplicaSet Controller가 이를 감지하고 새 Pod를 생성한다.

롤링 업데이트 과정은 다음과 같이 동작한다.

```text
기존 상태:
ReplicaSet v1 -> Pod v1, Pod v1, Pod v1

업데이트 시작:
ReplicaSet v2 생성
Pod v2를 일부 생성
Pod v1을 일부 종료

업데이트 완료:
ReplicaSet v2 -> Pod v2, Pod v2, Pod v2
ReplicaSet v1은 롤백을 위해 일정 기간 남을 수 있음
```

Deployment는 다음 기능을 제공한다.

- 지정한 Pod 개수 유지
- 무중단에 가까운 롤링 업데이트
- 이전 버전으로 롤백
- 업데이트 진행 상태 확인
- 선언형 배포 관리

---

## 4. Service 동작 원리

Pod는 재생성될 때 IP가 변경될 수 있으므로, 클라이언트가 Pod IP에 직접 의존하면 안정적인 통신이 어렵다. Service는 Pod 집합에 대해 고정된 접근 지점을 제공한다.

Service는 보통 label selector를 사용해 대상 Pod를 선택한다.

```yaml
selector:
  app: my-api
```

```text
Client
  |
  v
Service: my-api-service
  |
  +--> Pod A: app=my-api
  +--> Pod B: app=my-api
  +--> Pod C: app=my-api
```

Service의 주요 타입은 다음과 같다.

- **ClusterIP**
  - 클러스터 내부에서만 접근 가능한 기본 Service 타입이다.
  - 내부 마이크로서비스 간 통신에 사용된다.

- **NodePort**
  - 각 Worker Node의 특정 포트를 통해 Service에 접근할 수 있게 한다.
  - 외부 접근이 가능하지만 운영 환경에서는 보통 LoadBalancer나 Ingress와 함께 사용한다.

- **LoadBalancer**
  - 클라우드 환경에서 외부 로드밸런서를 생성해 Service와 연결한다.
  - AWS ELB/NLB, GCP Cloud Load Balancing 등과 연동될 수 있다.

- **ExternalName**
  - Service 이름을 외부 DNS 이름에 매핑한다.
  - 내부 서비스처럼 외부 서비스를 참조할 때 사용할 수 있다.

---

## 5. Ingress 동작 원리

Ingress는 HTTP/HTTPS 요청을 어떤 Service로 보낼지 정의하는 라우팅 규칙이다. Ingress 자체는 규칙 객체이며, 실제 트래픽 처리는 Ingress Controller가 수행한다.

```text
Internet
   |
   v
External Load Balancer
   |
   v
Ingress Controller
   |
   +-- host: api.example.com /api -> api-service
   |
   +-- host: web.example.com /    -> web-service
```

Ingress는 다음과 같은 기능을 제공할 수 있다.

- 도메인 기반 라우팅
- 경로 기반 라우팅
- TLS 인증서 적용
- 단일 진입점에서 여러 Service로 분기
- HTTP 레벨 로드밸런싱

예를 들어 `api.example.com`으로 들어온 요청은 API Service로, `web.example.com`으로 들어온 요청은 Web Service로 라우팅할 수 있다.

---

---

## 실제 시스템 연결

## 1. Linux와 Kubernetes

Kubernetes는 Linux 커널 기능을 적극적으로 활용한다. 컨테이너는 기본적으로 다음 Linux 기능을 기반으로 격리된다.

- **Namespace**
  - 프로세스, 네트워크, 마운트, IPC, UTS, 사용자 공간 등을 격리한다.
- **cgroups**
  - CPU, 메모리 등 리소스 사용량을 제한하고 측정한다.
- **iptables / IPVS**
  - Service 트래픽 전달 및 로드밸런싱 규칙에 사용된다.
- **overlay filesystem**
  - 컨테이너 이미지 레이어를 효율적으로 관리하는 데 사용된다.

Pod의 네트워크는 CNI(Container Network Interface) 플러그인을 통해 구성된다. 대표적인 CNI로는 Calico, Cilium, Flannel 등이 있다. CNI는 Pod마다 IP를 부여하고, 노드 간 Pod 통신이 가능하도록 네트워크를 설정한다.

## 2. Nginx와 Ingress

실제 운영 환경에서 Ingress Controller로 Nginx Ingress Controller를 사용하는 경우가 많다. 이 경우 흐름은 다음과 같다.

```text
사용자 브라우저
   |
   v
클라우드 Load Balancer
   |
   v
Nginx Ingress Controller Pod
   |
   v
Kubernetes Service
   |
   v
Application Pod
```

Nginx Ingress Controller는 Kubernetes API를 감시하다가 Ingress 리소스가 생성되거나 변경되면 Nginx 설정을 동적으로 갱신한다. 이를 통해 애플리케이션별로 별도의 외부 로드밸런서를 만들지 않고도 여러 서비스를 하나의 진입점으로 노출할 수 있다.

## 3. AWS EKS 사례

AWS에서는 관리형 Kubernetes 서비스인 Amazon EKS를 사용할 수 있다. EKS에서는 Control Plane을 AWS가 관리하고, 사용자는 Worker Node 또는 Fargate 기반 실행 환경을 구성해 애플리케이션을 배포한다.

실제 구성 예시는 다음과 같다.

```text
Route 53
   |
   v
AWS Load Balancer
   |
   v
Ingress Controller
   |
   v
Service
   |
   v
Deployment / Pod
```

- Route 53: 도메인 DNS 관리
- AWS Load Balancer: 외부 트래픽 수신
- Ingress Controller: HTTP/HTTPS 라우팅
- Service: 내부 Pod 접근 지점
- Deployment: Pod 복제본 및 배포 전략 관리

## 4. GCP GKE 사례

Google Cloud에서는 Google Kubernetes Engine(GKE)을 사용할 수 있다. GKE에서도 Kubernetes 리소스 모델은 동일하다. LoadBalancer 타입 Service나 Ingress를 사용하면 Google Cloud Load Balancing과 연동할 수 있다.

```text
Client
  |
  v
Google Cloud Load Balancer
  |
  v
GKE Ingress / Service
  |
  v
Pod
```

GKE는 클러스터 운영, 노드 풀 관리, 오토스케일링, 로깅/모니터링 연동을 클라우드 서비스와 함께 제공한다.

---

---

## 클라우드 연결

## 1. Docker와 Kubernetes의 관계

Docker는 컨테이너 이미지 빌드와 실행 생태계에서 널리 사용되는 도구이고, Kubernetes는 컨테이너를 여러 서버에 걸쳐 운영하는 오케스트레이션 플랫폼이다. 개발자는 Dockerfile로 이미지를 만들고, 이를 이미지 레지스트리에 업로드한 뒤 Kubernetes Deployment에서 해당 이미지를 참조해 배포한다.

```text
Dockerfile
   |
   v
docker build
   |
   v
Container Image
   |
   v
Container Registry
   |
   v
Kubernetes Deployment
   |
   v
Pod 실행
```

Kubernetes는 Docker 이미지 형식을 사용할 수 있지만, 실제 노드에서 컨테이너를 실행할 때는 CRI를 지원하는 런타임(containerd, CRI-O 등)을 사용한다.

## 2. Kubernetes와 AWS 서비스

AWS에서 Kubernetes를 운영할 때 자주 연결되는 서비스는 다음과 같다.

- **Amazon EKS**
  - AWS 관리형 Kubernetes 서비스
- **Amazon ECR**
  - 컨테이너 이미지 저장소
- **Elastic Load Balancing**
  - LoadBalancer Service 또는 Ingress Controller와 연동
- **Amazon VPC**
  - Kubernetes Node와 Pod 네트워크 기반
- **IAM**
  - 클러스터 접근 제어 및 AWS 리소스 권한 관리
- **Amazon CloudWatch**
  - 로그와 메트릭 수집
- **AWS Secrets Manager / SSM Parameter Store**
  - 애플리케이션 비밀값 관리에 활용 가능

## 3. Kubernetes와 CI/CD

Kubernetes는 선언형 YAML 리소스를 기반으로 하므로 CI/CD와 잘 맞는다. 일반적인 배포 흐름은 다음과 같다.

```text
1. 개발자가 코드 push
2. CI가 테스트 수행
3. Docker 이미지 빌드
4. 이미지 레지스트리에 push
5. Deployment YAML의 이미지 태그 변경
6. kubectl apply 또는 GitOps 도구로 배포
7. Kubernetes가 Rolling Update 수행
```

Argo CD, Flux 같은 GitOps 도구는 Git 저장소의 선언형 매니페스트를 실제 클러스터 상태와 동기화한다.

## 4. Service와 클라우드 로드밸런서

Kubernetes의 `Service type: LoadBalancer`는 클라우드 환경에서 외부 로드밸런서를 생성하는 방식으로 동작한다. 예를 들어 AWS EKS에서 LoadBalancer Service를 만들면 클라우드 컨트롤러 또는 관련 컨트롤러가 AWS 로드밸런서 생성을 처리한다.

```text
외부 사용자
   |
   v
AWS/GCP Load Balancer
   |
   v
Kubernetes Service
   |
   v
Pod
```

## 5. Ingress와 클라우드 네이티브 아키텍처

Ingress는 여러 서비스를 하나의 HTTP/HTTPS 진입점으로 통합하는 데 유용하다. 클라우드에서는 보통 다음 구성을 사용한다.

```text
DNS
 |
 v
Cloud Load Balancer
 |
 v
Ingress Controller
 |
 v
Service A / Service B / Service C
```

이 구조는 마이크로서비스 아키텍처에서 서비스가 많아져도 외부 진입점을 효율적으로 관리할 수 있게 해준다.

---

---

## 보안 연결

## 1. API Server 보안

Kubernetes의 모든 제어 요청은 API Server를 통해 이루어진다. 따라서 API Server 보안은 클러스터 보안의 핵심이다.

모범 사례:

- TLS 기반 통신 사용
- 인증(Authentication)과 인가(Authorization) 적용
- RBAC(Role-Based Access Control) 최소 권한 원칙 적용
- 불필요한 사용자나 ServiceAccount 권한 제거
- Audit Log 활성화
- API Server 공개 범위 제한

## 2. etcd 보안

etcd에는 클러스터의 핵심 상태 정보가 저장된다. Secret 리소스도 etcd에 저장되므로 etcd 접근 권한이 탈취되면 민감 정보가 노출될 수 있다.

모범 사례:

- etcd 접근을 Control Plane 내부로 제한
- etcd 통신에 TLS 사용
- etcd 데이터 백업 암호화
- Kubernetes Secret의 암호화 저장 설정 사용
- 정기적인 백업과 복구 테스트 수행

## 3. Pod 보안

Pod는 컨테이너 실행 단위이므로 컨테이너 권한 설정이 중요하다.

모범 사례:

- root 사용자로 컨테이너 실행하지 않기
- `privileged: true` 사용 최소화
- 필요한 Linux capability만 허용
- read-only root filesystem 사용 검토
- 리소스 requests/limits 설정
- 신뢰할 수 있는 이미지 사용
- 이미지 취약점 스캔 수행

예시 보안 설정:

```yaml
securityContext:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
```

## 4. Network Policy

기본적으로 Kubernetes 클러스터 내부 Pod 간 통신은 CNI 설정에 따라 넓게 허용될 수 있다. NetworkPolicy를 사용하면 Pod 간 네트워크 접근을 제한할 수 있다.

예를 들어 API Pod는 DB Pod에 접근할 수 있지만, Web Pod는 DB Pod에 직접 접근하지 못하게 제한할 수 있다.

```text
Web Pod  ---> API Pod  ---> DB Pod
Web Pod  -X-> DB Pod
```

NetworkPolicy를 적용하려면 이를 지원하는 CNI 플러그인이 필요하다.

## 5. Service와 Ingress 보안

Service와 Ingress는 외부 트래픽이 들어오는 경로가 될 수 있으므로 보안 설정이 중요하다.

모범 사례:

- Ingress에 TLS 적용
- HTTP를 HTTPS로 리다이렉트
- 허용된 도메인만 라우팅
- WAF 적용 검토
- Rate Limiting 적용 검토
- 관리자용 Service는 외부에 노출하지 않기
- LoadBalancer 타입 Service 사용 시 보안 그룹 또는 방화벽 제한
- Ingress Controller 자체의 취약점 패치 유지

## 6. Secret 관리

Kubernetes Secret은 민감 정보를 담기 위한 리소스지만, 기본적으로 Secret 값은 Base64로 인코딩된 형태로 표현된다. Base64는 암호화가 아니다. 따라서 Secret 사용 시 추가적인 보호가 필요하다.

모범 사례:

- etcd 암호화 저장 활성화
- RBAC으로 Secret 조회 권한 제한
- Secret을 컨테이너 이미지에 포함하지 않기
- 환경 변수보다 파일 마운트 방식 검토
- 외부 Secret Manager 연동 검토
- 로그에 Secret이 출력되지 않도록 주의

---

---

## 면접 질문

**Q1. Kubernetes의 Control Plane과 Worker Node의 역할 차이는 무엇인가요?**  
> 핵심 답변: Control Plane은 클러스터 상태를 관리하고 스케줄링, API 처리, 컨트롤 루프를 수행한다. Worker Node는 실제 Pod와 컨테이너를 실행한다. Control Plane에는 kube-apiserver, etcd, scheduler, controller-manager 등이 있고 Worker Node에는 kubelet, kube-proxy, container runtime이 있다.

**Q2. Pod와 Container의 차이는 무엇인가요?**  
> 핵심 답변: Container는 실제 애플리케이션 프로세스 실행 단위이고, Pod는 Kubernetes에서 스케줄링되는 최소 단위다. Pod는 하나 이상의 컨테이너를 포함할 수 있으며 같은 Pod 내 컨테이너들은 네트워크 네임스페이스와 볼륨을 공유할 수 있다.

**Q3. Deployment를 사용하는 이유는 무엇인가요?**  
> 핵심 답변: Deployment는 Pod를 직접 관리하지 않고 원하는 복제본 수, 업데이트 전략, 롤백을 선언적으로 관리하기 위해 사용한다. 내부적으로 ReplicaSet을 생성해 Pod 개수를 유지하고, 롤링 업데이트를 통해 새 버전 배포를 안정적으로 수행한다.

**Q4. Service가 필요한 이유는 무엇인가요?**  
> 핵심 답변: Pod는 재생성될 때 IP가 변경될 수 있으므로 안정적인 접근 지점이 필요하다. Service는 label selector로 Pod 집합을 선택하고 고정된 가상 IP 또는 외부 접근 방식을 제공한다. 이를 통해 클라이언트는 개별 Pod IP가 아니라 Service를 통해 통신할 수 있다.

**Q5. Ingress와 Service LoadBalancer의 차이는 무엇인가요?**  
> 핵심 답변: LoadBalancer 타입 Service는 보통 하나의 Service를 외부 로드밸런서에 직접 노출하는 방식이다. Ingress는 HTTP/HTTPS 레벨에서 도메인이나 경로 기반으로 여러 Service에 라우팅하는 규칙이다. Ingress는 반드시 Ingress Controller가 있어야 실제 트래픽 처리가 가능하다.

---

---

## 관련 개념

- [[컨테이너]] - Kubernetes는 컨테이너화된 애플리케이션을 배포하고 운영하는 플랫폼이다.
- [[Docker]] - 컨테이너 이미지 빌드와 로컬 실행에 널리 사용되며 Kubernetes 배포 흐름과 연결된다.
- [[Pod]] - Kubernetes에서 스케줄링 가능한 최소 실행 단위다.
- [[Deployment]] - Pod 복제본, 롤링 업데이트, 롤백을 관리하는 핵심 리소스다.
- [[ReplicaSet]] - Deployment가 내부적으로 사용하는 Pod 복제본 유지 리소스다.
- [[Service]] - Pod의 동적 IP 문제를 해결하고 안정적인 네트워크 접근 지점을 제공한다.
- [[Ingress]] - HTTP/HTTPS 트래픽을 Service로 라우팅하는 Kubernetes 리소스다.
- [[Ingress Controller]] - Ingress 규칙을 실제 네트워크 프록시 설정으로 반영하는 컨트롤러다.
- [[etcd]] - Kubernetes 클러스터 상태를 저장하는 분산 키-값 저장소다.
- [[kube-apiserver]] - Kubernetes API 요청의 진입점이며 인증, 인가, 리소스 처리를 담당한다.
- [[kube-scheduler]] - Pod를 실행할 적절한 Worker Node를 선택하는 컴포넌트다.
- [[kubelet]] - Worker Node에서 Pod 실행과 상태 보고를 담당하는 에이전트다.
- [[CNI]] - Kubernetes Pod 네트워크를 구성하는 플러그인 인터페이스다.
- [[NetworkPolicy]] - Pod 간 네트워크 접근 제어를 정의하는 보안 리소스다.
- [[RBAC]] - Kubernetes API 권한을 역할 기반으로 제어하는 인가 방식이다.
