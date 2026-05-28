---
date: 2026-05-29
category: 백엔드 - 인프라
topic: Docker
subtopic: VM vs 컨테이너, 이미지/컨테이너 아키텍처, 볼륨 및 네트워크
tags: [CS, 백엔드---인프라, study]
---

# Docker - VM vs 컨테이너, 이미지/컨테이너 아키텍처, 볼륨 및 네트워크

## 핵심 개념

Docker는 애플리케이션과 그 실행에 필요한 런타임, 라이브러리, 설정 파일 등을 **이미지(Image)** 라는 불변 패키지로 묶고, 이를 **컨테이너(Container)** 라는 격리된 프로세스 환경에서 실행하게 해주는 컨테이너 플랫폼이다. Docker의 핵심 목적은 “내 PC에서는 되는데 서버에서는 안 된다”는 환경 불일치 문제를 줄이고, 애플리케이션 배포 단위를 표준화하는 것이다.

전통적인 **가상 머신(VM)** 은 하이퍼바이저 위에 게스트 OS 전체를 실행한다. 반면 Docker 컨테이너는 호스트 OS의 커널을 공유하면서, Linux namespace와 cgroup 같은 커널 기능을 이용해 프로세스, 파일시스템, 네트워크, 리소스를 격리한다. 따라서 컨테이너는 VM보다 일반적으로 가볍고 시작 속도가 빠르며, 같은 서버에서 더 많은 인스턴스를 실행하기 쉽다. 다만 컨테이너는 커널을 공유하므로 VM만큼 강한 격리 경계로 보기는 어렵고, 보안 설정이 중요하다.

Docker 아키텍처에서 이미지는 읽기 전용 레이어들의 집합이고, 컨테이너는 이미지 위에 쓰기 가능한 얇은 레이어를 추가한 실행 단위다. 데이터 영속성을 위해서는 컨테이너 내부 파일시스템에만 의존하지 않고 **볼륨(Volume)** 또는 바인드 마운트를 사용한다. 또한 컨테이너는 기본적으로 격리된 네트워크 네임스페이스를 가지며, Docker bridge network, host network, overlay network 등을 통해 외부 또는 다른 컨테이너와 통신한다.

백엔드 인프라 관점에서 Docker는 로컬 개발 환경, CI/CD 파이프라인, 마이크로서비스 배포, 테스트 환경 구성, 클라우드 컨테이너 서비스의 기반 기술로 널리 사용된다. 특히 Kubernetes, ECS, GKE 같은 컨테이너 오케스트레이션 환경을 이해하기 위해서는 Docker의 이미지, 컨테이너, 볼륨, 네트워크 개념을 정확히 이해하는 것이 중요하다.

---

---

## 내부 동작 원리

Docker는 크게 **Docker Client**, **Docker Daemon**, **Image Registry**, **Container Runtime** 으로 구성된다.

```text
사용자
  |
  | docker build / docker run / docker pull
  v
Docker CLI
  |
  v
Docker Daemon
  |
  +--> Image 관리
  |      +--> Registry에서 pull
  |      +--> Dockerfile 기반 build
  |
  +--> Container 생성
         +--> namespace 설정
         +--> cgroup 설정
         +--> filesystem layer 연결
         +--> network namespace 생성
         +--> process 실행
```

## 1. VM vs 컨테이너 구조

```text
[가상 머신 구조]

App A        App B
Libs         Libs
Guest OS     Guest OS
VM           VM
Hypervisor
Host OS
Hardware
```

VM은 각 인스턴스마다 게스트 OS를 포함한다. 이 때문에 격리 수준이 높고 서로 다른 OS 환경을 실행할 수 있지만, OS 부팅과 리소스 사용량 측면에서 무겁다.

```text
[컨테이너 구조]

App A        App B
Libs         Libs
Container    Container
Container Runtime
Host OS Kernel
Hardware
```

컨테이너는 호스트 OS 커널을 공유한다. 컨테이너 안에서 독립된 OS처럼 보이는 것은 실제로는 Linux namespace를 통해 프로세스 ID, 네트워크 인터페이스, 마운트 포인트, 사용자 등을 격리했기 때문이다.

## 2. 이미지와 컨테이너 아키텍처

Docker 이미지는 여러 개의 읽기 전용 레이어로 구성된다. Dockerfile의 각 명령어는 일반적으로 이미지 레이어를 생성하거나 메타데이터를 변경한다.

예시:

```dockerfile
FROM ubuntu
RUN apt-get update
COPY app.jar /app/app.jar
CMD ["java", "-jar", "/app/app.jar"]
```

개념적으로는 다음과 같다.

```text
Container Writable Layer
-------------------------
CMD metadata
COPY app.jar layer
RUN apt-get update layer
Base ubuntu image layer
```

컨테이너가 실행되면 이미지 레이어 위에 **쓰기 가능한 컨테이너 레이어** 가 추가된다. 컨테이너 내부에서 파일을 생성하거나 수정하면 이 writable layer에 반영된다. 컨테이너가 삭제되면 이 레이어도 함께 제거되므로, 데이터베이스 데이터나 업로드 파일처럼 유지되어야 하는 데이터는 볼륨에 저장해야 한다.

Docker는 Linux 환경에서 OverlayFS 같은 union filesystem을 사용해 여러 이미지 레이어를 하나의 파일시스템처럼 보이게 할 수 있다. 이를 통해 이미지 레이어를 재사용하고, 같은 베이스 이미지를 사용하는 여러 컨테이너가 저장 공간을 효율적으로 공유할 수 있다.

## 3. 컨테이너 실행 과정

`docker run nginx` 명령을 실행하면 일반적으로 다음 과정이 일어난다.

1. Docker CLI가 Docker Daemon에 요청을 보낸다.
2. Daemon이 로컬에 `nginx` 이미지가 있는지 확인한다.
3. 없으면 Docker Hub 같은 Registry에서 이미지를 pull 한다.
4. 이미지 레이어를 로컬 스토리지에 저장한다.
5. 컨테이너의 writable layer를 생성한다.
6. 컨테이너 전용 namespace를 설정한다.
   - PID namespace: 프로세스 격리
   - Network namespace: 네트워크 인터페이스 격리
   - Mount namespace: 파일시스템 마운트 격리
   - UTS namespace: hostname 격리
   - IPC namespace: 프로세스 간 통신 격리
   - User namespace: 사용자/그룹 ID 격리
7. cgroup으로 CPU, 메모리, I/O 등의 리소스 제한을 적용할 수 있다.
8. 컨테이너 네트워크를 설정한다.
9. 지정된 ENTRYPOINT 또는 CMD 프로세스를 실행한다.

중요한 점은 컨테이너는 “작은 VM”이 아니라 **격리된 프로세스** 라는 것이다. 컨테이너의 메인 프로세스가 종료되면 컨테이너도 종료된다.

## 4. 볼륨 동작 원리

Docker에서 데이터 저장 방식은 크게 다음과 같다.

```text
[컨테이너 내부 writable layer]
- 컨테이너 삭제 시 데이터 손실
- 임시 파일에 적합

[Volume]
- Docker가 관리하는 호스트 영역에 저장
- 컨테이너 삭제 후에도 유지 가능
- DB 데이터 저장에 적합

[Bind Mount]
- 호스트의 특정 경로를 컨테이너에 직접 연결
- 개발 환경에서 소스코드 마운트에 자주 사용
```

예시:

```bash
docker volume create mysql-data

docker run -d \
  --name mysql \
  -v mysql-data:/var/lib/mysql \
  mysql
```

이 경우 MySQL 컨테이너가 삭제되어도 `mysql-data` 볼륨은 남아 있을 수 있다. 새 MySQL 컨테이너에 같은 볼륨을 연결하면 데이터를 재사용할 수 있다.

개념도:

```text
Host
 ├─ Docker managed volume: mysql-data
 │    └─ DB files
 │
 └─ Container
      └─ /var/lib/mysql -> mysql-data에 연결
```

## 5. 네트워크 동작 원리

Docker 컨테이너는 기본적으로 독립된 network namespace를 가진다. Docker의 대표적인 네트워크 드라이버는 다음과 같다.

- `bridge`: 단일 호스트 내 컨테이너 간 통신에 사용되는 기본 네트워크 방식
- `host`: 컨테이너가 호스트 네트워크 namespace를 공유
- `none`: 네트워크 비활성화
- `overlay`: 여러 Docker 호스트 간 컨테이너 네트워크 연결에 사용
- `macvlan`: 컨테이너에 물리 네트워크와 유사한 MAC 주소 기반 연결 제공

기본 bridge 구조는 다음과 같이 이해할 수 있다.

```text
Container A eth0
      |
      v
Docker bridge network docker0
      |
      v
Host network interface
      |
      v
External Network
```

컨테이너 포트를 외부에 노출하려면 포트 매핑을 사용한다.

```bash
docker run -d -p 8080:80 nginx
```

이 명령은 호스트의 `8080` 포트로 들어온 요청을 컨테이너의 `80` 포트로 전달한다.

```text
Client
  |
  | http://host:8080
  v
Host:8080
  |
  v
Container nginx:80
```

Docker Compose에서는 같은 사용자 정의 bridge network에 있는 서비스들이 서비스 이름으로 서로를 찾을 수 있다.

```yaml
services:
  web:
    image: nginx
    ports:
      - "8080:80"
  app:
    image: my-app
```

같은 Compose 프로젝트의 네트워크 안에서 `app` 컨테이너는 `web`이라는 DNS 이름으로 접근할 수 있다.

---

---

## 실제 시스템 연결

## 1. Linux 서버에서 Docker 실행

Linux 서버에서 Docker는 호스트 커널의 기능을 직접 사용한다. 예를 들어 Ubuntu나 Amazon Linux 같은 서버에 Docker Engine을 설치하면, 컨테이너는 해당 Linux 커널 위에서 namespace와 cgroup을 통해 격리된다.

실제 백엔드 서버에서는 다음과 같은 방식으로 Docker가 사용된다.

```bash
docker build -t my-api:1.0 .
docker run -d \
  --name my-api \
  -p 8080:8080 \
  -e SPRING_PROFILES_ACTIVE=prod \
  my-api:1.0
```

이 구성은 Spring Boot, Node.js, Go API 서버 등을 이미지로 패키징해 동일한 방식으로 실행할 수 있게 해준다.

## 2. Nginx 리버스 프록시와 Docker

실무에서는 Nginx를 컨테이너로 실행하고, 내부 API 컨테이너로 요청을 전달하는 구조를 많이 사용한다.

```text
Client
  |
  v
Nginx Container :80/:443
  |
  v
Backend API Container :8080
```

Docker Compose 예시:

```yaml
services:
  nginx:
    image: nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api

  api:
    image: my-api:1.0
```

여기서 Nginx 설정 파일은 bind mount로 주입하고, 같은 Docker network 안에서 `api`라는 서비스 이름으로 백엔드에 접근할 수 있다.

## 3. MySQL, PostgreSQL 같은 DB 컨테이너

개발 환경에서는 데이터베이스를 Docker 컨테이너로 실행하는 경우가 많다.

```bash
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=secret \
  -v pg-data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres
```

다만 운영 환경에서 DB를 컨테이너로 직접 운영할 경우에는 백업, 볼륨 스토리지, 장애 복구, 성능, 업그레이드 전략을 신중히 설계해야 한다. 단순히 컨테이너만 사용한다고 데이터 안정성이 자동으로 보장되는 것은 아니다.

## 4. Docker Desktop과 macOS/Windows

Linux가 아닌 macOS나 Windows에서 Docker Desktop을 사용할 경우, 컨테이너는 일반적으로 Linux VM 위에서 실행된다. 이는 Linux 컨테이너가 Linux 커널 기능에 의존하기 때문이다. 사용자는 Docker CLI로 동일하게 조작하지만, 내부적으로는 Linux 환경을 제공하는 가상화 계층이 존재한다.

```text
macOS/Windows
  |
  v
Docker Desktop VM
  |
  v
Linux Kernel
  |
  v
Containers
```

따라서 로컬 개발 중 파일 공유 성능, 네트워크 접근 방식, 볼륨 마운트 동작이 Linux 서버와 다르게 느껴질 수 있다.

## 5. CI/CD 파이프라인

Docker는 CI/CD에서 빌드 산출물을 표준화하는 데 자주 사용된다.

```text
Git Push
  |
  v
CI Server
  |
  +--> docker build
  +--> docker test
  +--> docker push
  |
  v
Registry
  |
  v
Production Server or Kubernetes
```

예를 들어 GitHub Actions, GitLab CI, Jenkins 등에서 Docker 이미지를 빌드한 후 Registry에 push하고, 운영 환경에서는 해당 이미지를 pull하여 배포한다. 이를 통해 배포 대상 서버에 애플리케이션 런타임을 직접 설치하지 않고도 동일한 실행 환경을 유지할 수 있다.

---

---

## 클라우드 연결

## 1. Docker와 Kubernetes

Kubernetes는 컨테이너 오케스트레이션 플랫폼이다. Kubernetes는 Docker 이미지와 같은 OCI 호환 컨테이너 이미지를 실행할 수 있다. Kubernetes의 Pod는 하나 이상의 컨테이너를 포함하며, 컨테이너는 이미지로부터 생성된다.

```text
Docker Image
  |
  v
Kubernetes Pod
  |
  +--> Container A
  +--> Container B
```

Docker에서 익힌 이미지, 포트, 환경변수, 볼륨, 네트워크 개념은 Kubernetes에서도 다음과 같이 연결된다.

| Docker 개념 | Kubernetes 개념 |
|---|---|
| Image | Container image |
| Container | Pod 내부 container |
| Volume | volume, PersistentVolume, PersistentVolumeClaim |
| Port mapping | Service, Ingress |
| Environment variable | env, ConfigMap, Secret |
| Docker network | Pod network, Service network |

## 2. AWS와 Docker

AWS에서는 Docker 이미지를 다양한 서비스에서 실행할 수 있다.

- **Amazon ECR**: Docker/OCI 이미지를 저장하는 컨테이너 이미지 Registry
- **Amazon ECS**: 컨테이너 오케스트레이션 서비스
- **AWS Fargate**: 서버를 직접 관리하지 않고 컨테이너를 실행하는 컴퓨팅 방식
- **Amazon EKS**: AWS에서 제공하는 관리형 Kubernetes 서비스
- **Elastic Beanstalk**: Docker 기반 애플리케이션 배포를 지원하는 PaaS 성격의 서비스

일반적인 흐름:

```text
Developer
  |
  v
docker build
  |
  v
Amazon ECR push
  |
  v
ECS / EKS / Fargate 배포
  |
  v
Application Load Balancer
  |
  v
Users
```

## 3. GCP와 Docker

GCP에서도 Docker 이미지를 빌드하고 실행하는 구조가 널리 사용된다.

- **Artifact Registry**: 컨테이너 이미지를 저장하는 Registry
- **Google Kubernetes Engine, GKE**: 관리형 Kubernetes
- **Cloud Run**: 컨테이너 이미지를 서버리스 방식으로 실행
- **Cloud Build**: 컨테이너 이미지 빌드 및 CI/CD 자동화

Cloud Run은 컨테이너 이미지를 HTTP 요청 기반 서비스로 실행할 수 있게 해준다. 개발자는 Dockerfile 또는 빌드팩 기반으로 이미지를 만들고, 이를 배포하여 서버 관리 부담을 줄일 수 있다.

## 4. Azure와 Docker

Azure에서는 다음 서비스와 연결된다.

- **Azure Container Registry, ACR**: 컨테이너 이미지 저장소
- **Azure Kubernetes Service, AKS**: 관리형 Kubernetes
- **Azure Container Apps**: 컨테이너 기반 애플리케이션 실행 환경
- **Azure App Service for Containers**: 컨테이너 이미지 기반 웹 앱 실행

## 5. 클라우드 스토리지와 볼륨

Docker 단독 환경의 volume은 보통 단일 호스트에 종속된다. 클라우드 환경에서 상태 저장 애플리케이션을 안정적으로 운영하려면 외부 스토리지를 사용한다.

예시:

```text
Kubernetes Pod
  |
  v
PersistentVolumeClaim
  |
  v
Cloud Disk / EBS / Persistent Disk / Azure Disk
```

AWS에서는 EBS, EFS, S3 등을 목적에 따라 사용하고, GCP에서는 Persistent Disk, Filestore, Cloud Storage 등을 사용할 수 있다. 단, 객체 스토리지인 S3나 Cloud Storage는 일반적인 POSIX 파일시스템 볼륨과 동작 방식이 다르므로 애플리케이션 요구사항에 맞게 선택해야 한다.

## 6. 클라우드 네트워크와 컨테이너 네트워크

Docker의 bridge network는 단일 호스트 중심이다. 클라우드에서 여러 호스트에 걸쳐 컨테이너를 운영하면 서비스 디스커버리, 로드밸런싱, 네트워크 정책이 필요하다.

Kubernetes에서는 다음 구성요소가 이를 담당한다.

```text
Pod IP
  |
  v
Service
  |
  v
Ingress / LoadBalancer
  |
  v
External Client
```

AWS ECS에서는 Service Discovery, Load Balancer, VPC networking을 통해 컨테이너 간 통신과 외부 노출을 구성할 수 있다.

---

---

## 보안 연결

## 1. 컨테이너는 보안 경계가 약할 수 있음

컨테이너는 VM과 달리 호스트 커널을 공유한다. 따라서 컨테이너 내부 프로세스가 커널 취약점을 악용하거나, 과도한 권한을 가진 상태로 실행되면 호스트에 영향을 줄 수 있다. 컨테이너를 VM과 동일한 강도의 격리 수단으로 가정하면 안 된다.

모범 사례:

- 컨테이너를 root가 아닌 사용자로 실행
- 불필요한 Linux capability 제거
- `--privileged` 사용 금지 또는 최소화
- 호스트 파일시스템 bind mount 최소화
- 읽기 전용 root filesystem 사용 검토
- seccomp, AppArmor, SELinux 같은 보안 기능 활용

## 2. 이미지 보안

Docker 이미지는 애플리케이션과 OS 패키지를 포함하므로 취약점이 들어갈 수 있다. 오래된 베이스 이미지, 불필요한 패키지, 하드코딩된 secret은 주요 위험 요소다.

모범 사례:

```dockerfile
# 예시: root가 아닌 사용자 사용
FROM node
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev
COPY . .
USER node
CMD ["node", "server.js"]
```

- 공식 이미지 또는 신뢰할 수 있는 이미지 사용
- 이미지 태그를 명확히 관리
- 이미지 취약점 스캔 수행
- secret을 이미지에 포함하지 않기
- `.dockerignore`로 불필요한 파일 제외
- multi-stage build로 빌드 도구를 런타임 이미지에서 제거

## 3. Registry 보안

Registry에 push된 이미지는 운영 배포의 기준이 된다. 공격자가 Registry 이미지를 변조하면 공급망 공격으로 이어질 수 있다.

모범 사례:

- Registry 접근 권한 최소화
- CI/CD 계정 권한 분리
- 이미지 서명 및 검증 도입 검토
- private registry 사용
- 불필요한 public image push 방지
- 배포 가능한 이미지와 개발용 이미지 분리

## 4. 볼륨 보안

볼륨과 bind mount는 컨테이너가 호스트 파일시스템에 접근할 수 있는 통로가 된다. 특히 다음과 같은 설정은 위험할 수 있다.

```bash
docker run -v /:/host ...
```

이 경우 컨테이너가 호스트 루트 파일시스템에 접근할 수 있어 매우 위험하다.

모범 사례:

- 필요한 경로만 mount
- 가능한 경우 read-only mount 사용

```bash
docker run -v ./nginx.conf:/etc/nginx/nginx.conf:ro nginx
```

- DB 볼륨 백업과 접근 권한 관리
- secret 파일을 일반 볼륨에 평문 저장하지 않기
- 컨테이너 간 불필요한 볼륨 공유 제한

## 5. 네트워크 보안

컨테이너 포트를 외부에 노출하면 공격 표면이 증가한다. 모든 컨테이너 포트를 무조건 publish하는 것은 위험하다.

모범 사례:

- 외부 공개가 필요한 포트만 `-p`로 노출
- 내부 서비스는 Docker internal network 안에서만 통신
- DB는 외부 인터넷에 직접 노출하지 않기
- reverse proxy 또는 load balancer를 통해 진입점 제한
- 네트워크를 서비스 단위로 분리
- Kubernetes에서는 NetworkPolicy 사용 검토

예시:

```yaml
services:
  api:
    image: my-api
    networks:
      - backend

  db:
    image: postgres
    networks:
      - backend

networks:
  backend:
```

이 경우 `api`와 `db`는 같은 backend 네트워크에서 통신하지만, `ports`를 지정하지 않으면 호스트 외부로 직접 노출되지 않는다.

## 6. Docker Socket 보안

Docker daemon socket은 매우 강력한 권한을 가진다. 컨테이너에 `/var/run/docker.sock`을 마운트하면 컨테이너 내부에서 호스트 Docker daemon을 제어할 수 있다. 이는 사실상 호스트 장악으로 이어질 수 있으므로 매우 주의해야 한다.

위험한 예:

```bash
docker run -v /var/run/docker.sock:/var/run/docker.sock ...
```

모범 사례:

- Docker socket mount 금지 또는 엄격히 제한
- CI/CD에서 필요한 경우 별도 격리된 runner 사용
- 최소 권한 원칙 적용

---

---

## 면접 질문

**Q1. VM과 Docker 컨테이너의 차이는 무엇인가요?**  
> 핵심 답변: VM은 하이퍼바이저 위에서 게스트 OS 전체를 실행하고, 컨테이너는 호스트 OS 커널을 공유하면서 namespace와 cgroup으로 프로세스를 격리한다. 컨테이너는 일반적으로 가볍고 빠르지만, 커널 공유로 인해 보안 격리 측면에서는 VM과 차이가 있다.

**Q2. Docker 이미지와 컨테이너의 차이는 무엇인가요?**  
> 핵심 답변: 이미지는 애플리케이션 실행 환경을 담은 읽기 전용 템플릿이고, 컨테이너는 이미지를 기반으로 실행된 프로세스 인스턴스다. 컨테이너는 이미지 위에 writable layer를 추가해 실행되며, 컨테이너 삭제 시 해당 writable layer의 데이터는 사라질 수 있다.

**Q3. Docker Volume을 사용하는 이유는 무엇인가요?**  
> 핵심 답변: 컨테이너 내부 writable layer는 컨테이너 수명에 종속되므로 데이터 영속성에 적합하지 않다. Volume은 컨테이너와 분리된 저장 공간을 제공하여 DB 데이터, 업로드 파일, 설정 데이터 등을 컨테이너 재생성 후에도 유지할 수 있게 한다.

**Q4. Docker bridge network와 port publishing은 어떻게 다른가요?**  
> 핵심 답변: bridge network는 컨테이너 간 통신을 위한 가상 네트워크이고, port publishing은 호스트의 포트를 컨테이너 포트로 매핑해 외부 클라이언트가 접근할 수 있게 하는 기능이다. bridge network 안의 컨테이너끼리는 내부 IP나 서비스 이름으로 통신할 수 있지만, 외부 접근에는 `-p` 옵션이 필요하다.

**Q5. Docker 컨테이너를 운영 환경에서 안전하게 실행하기 위한 보안 모범 사례는 무엇인가요?**  
> 핵심 답변: root가 아닌 사용자로 실행하고, `--privileged` 사용을 피하며, 필요한 capability만 허용한다. 신뢰할 수 있는 이미지와 취약점 스캔을 사용하고, secret을 이미지에 포함하지 않아야 한다. 또한 Docker socket mount를 피하고, 볼륨과 네트워크 노출 범위를 최소화해야 한다.

---

---

## 관련 개념

- [[Linux Namespace]] - 컨테이너가 프로세스, 네트워크, 마운트 등을 격리하는 핵심 커널 기능이다.
- [[cgroup]] - 컨테이너의 CPU, 메모리, I/O 같은 리소스 사용량을 제한하고 관리하는 Linux 기능이다.
- [[OverlayFS]] - Docker 이미지 레이어를 하나의 파일시스템처럼 합쳐 보여주는 union filesystem 계열 기술이다.
- [[OCI Image]] - Docker 이미지와 호환되는 표준 컨테이너 이미지 형식을 이해하는 데 필요하다.
- [[Container Runtime]] - containerd, runc처럼 실제 컨테이너 생성과 실행을 담당하는 계층과 관련된다.
- [[Dockerfile]] - Docker 이미지를 선언적으로 빌드하기 위한 핵심 파일이다.
- [[Docker Compose]] - 여러 컨테이너 서비스를 네트워크, 볼륨과 함께 로컬 또는 단일 호스트 환경에서 정의하고 실행하는 도구다.
- [[Kubernetes Pod]] - Kubernetes에서 컨테이너를 실행하는 최소 배포 단위이며 Docker 컨테이너 개념과 직접 연결된다.
- [[Persistent Volume]] - Kubernetes 환경에서 Docker volume 개념을 클러스터 수준의 영속 스토리지로 확장한 개념이다.
- [[Service Discovery]] - 컨테이너 환경에서 동적으로 생성되고 삭제되는 서비스의 주소를 찾기 위한 핵심 개념이다.
- [[Reverse Proxy]] - Nginx 같은 프록시가 컨테이너 기반 백엔드 서비스 앞단에서 트래픽을 제어하는 방식과 관련된다.
- [[CI/CD Pipeline]] - Docker 이미지를 빌드, 테스트, 배포하는 자동화 흐름과 밀접하게 연결된다.
