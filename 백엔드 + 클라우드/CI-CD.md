---
date: 2026-05-31
category: 백엔드 - 인프라
topic: CI/CD
subtopic: 빌드, 테스트, 배포 자동화 파이프라인 (GitHub Actions, Jenkins)
tags: [CS, 백엔드---인프라, study]
---

# CI/CD - 빌드, 테스트, 배포 자동화 파이프라인 (GitHub Actions, Jenkins)

## 핵심 개념

CI/CD는 애플리케이션 변경 사항을 더 자주, 더 안전하게 사용자에게 전달하기 위한 자동화된 소프트웨어 전달 방식이다. CI는 Continuous Integration, 즉 지속적 통합을 의미하며, 개발자가 작성한 코드를 자주 중앙 저장소에 병합하고 자동으로 빌드와 테스트를 수행하는 과정이다. CD는 문맥에 따라 Continuous Delivery 또는 Continuous Deployment를 의미한다. Continuous Delivery는 언제든 배포 가능한 상태까지 자동화하는 것이고, Continuous Deployment는 검증을 통과한 변경 사항을 운영 환경까지 자동 배포하는 것을 의미한다.

CI/CD의 핵심 목적은 수작업으로 인한 실수 감소, 빠른 피드백, 배포 리드타임 단축, 장애 발생 가능성 감소, 변경 사항의 추적성 확보에 있다. 백엔드 인프라 관점에서 CI/CD는 단순히 코드를 빌드하는 도구가 아니라, 소스 코드 저장소, 빌드 서버, 테스트 환경, 컨테이너 레지스트리, 배포 대상 서버 또는 Kubernetes 클러스터, 모니터링 시스템을 연결하는 자동화 파이프라인이다.

예를 들어 개발자가 GitHub에 코드를 push하면 GitHub Actions 또는 Jenkins가 이벤트를 감지하고, 의존성 설치, 정적 분석, 단위 테스트, 통합 테스트, Docker 이미지 빌드, 이미지 레지스트리 푸시, 스테이징 배포, 운영 배포를 순차적으로 수행할 수 있다. 이 과정에서 실패한 단계가 있으면 이후 단계는 중단되고 개발자에게 알림이 전달된다. 따라서 CI/CD는 개발 속도뿐 아니라 품질, 보안, 운영 안정성까지 연결되는 백엔드 인프라의 핵심 구성 요소이다.

---

---

## 내부 동작 원리

CI/CD 파이프라인은 일반적으로 “이벤트 트리거 → 작업 실행 환경 준비 → 빌드 → 테스트 → 패키징 → 배포 → 검증/알림”의 흐름으로 동작한다.

```text
[Developer]
    |
    | git push / pull request / tag 생성
    v
[Git Repository: GitHub, GitLab 등]
    |
    | Webhook 또는 내장 이벤트
    v
[CI/CD Orchestrator: GitHub Actions, Jenkins]
    |
    | Job 실행
    v
[Runner / Agent]
    |
    +--> 의존성 설치
    +--> 코드 빌드
    +--> 테스트 실행
    +--> 정적 분석 / 보안 스캔
    +--> Artifact 생성
    +--> Docker Image 빌드
    +--> Registry Push
    +--> 서버 또는 Kubernetes 배포
    v
[Target Environment: Dev / Staging / Production]
```

GitHub Actions는 저장소 내부의 `.github/workflows/*.yml` 파일에 정의된 workflow를 기반으로 동작한다. workflow는 `on`, `jobs`, `steps`로 구성된다. `on`은 어떤 이벤트에서 실행할지 정의한다. 예를 들어 `push`, `pull_request`, `workflow_dispatch` 등이 있다. `jobs`는 병렬 또는 순차적으로 실행되는 작업 단위이고, 각 job은 runner 위에서 실행된다. runner는 GitHub가 제공하는 호스팅 runner를 사용할 수도 있고, 사용자가 직접 구성한 self-hosted runner를 사용할 수도 있다. 각 step은 shell command 또는 재사용 가능한 action을 실행한다.

예시 구조는 다음과 같다.

```yaml
name: backend-ci

on:
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout source code
        uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'

      - name: Run tests
        run: ./gradlew test
```

Jenkins는 Jenkins controller와 agent 구조로 동작한다. Jenkins controller는 job 설정, pipeline 정의, 실행 스케줄링, 플러그인 관리, UI 제공을 담당한다. 실제 빌드 작업은 controller에서 직접 실행할 수도 있지만, 보통 agent 노드에서 실행한다. Jenkins Pipeline은 `Jenkinsfile`에 선언형 또는 스크립트형 문법으로 작성한다.

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/example/repo.git'
            }
        }

        stage('Build') {
            steps {
                sh './gradlew build'
            }
        }

        stage('Test') {
            steps {
                sh './gradlew test'
            }
        }

        stage('Deploy') {
            steps {
                sh './deploy.sh'
            }
        }
    }
}
```

빌드 단계에서는 소스 코드를 실행 가능한 형태로 변환한다. Java 백엔드라면 Gradle 또는 Maven을 통해 `.jar` 파일을 만들고, Node.js라면 npm 또는 pnpm을 이용해 의존성을 설치하고 번들링할 수 있다. 테스트 단계에서는 단위 테스트, 통합 테스트, API 테스트, E2E 테스트가 수행될 수 있다. 배포 단계에서는 빌드 결과물을 서버에 복사하거나 Docker 이미지를 생성해 컨테이너 레지스트리에 push한 뒤, Kubernetes Deployment를 갱신하거나 AWS ECS 서비스에 새 태스크 정의를 반영하는 방식으로 진행된다.

CI/CD 내부에서 중요한 개념은 artifact와 immutable build이다. artifact는 빌드 결과물이다. 예를 들어 `.jar`, `.war`, Docker image, Helm chart 등이 artifact가 될 수 있다. 이상적인 파이프라인에서는 같은 commit으로 생성된 artifact를 테스트 환경과 운영 환경에 동일하게 배포한다. 즉, 테스트한 결과물과 운영 배포 결과물이 달라지지 않도록 관리하는 것이 중요하다.

배포 자동화는 보통 다음과 같은 전략과 연결된다.

```text
[Rolling Deployment]
기존 인스턴스를 일부씩 새 버전으로 교체

[Blue-Green Deployment]
Blue: 현재 운영 버전
Green: 새 버전
트래픽 전환으로 배포

[Canary Deployment]
일부 사용자 또는 일부 트래픽만 새 버전으로 전달 후 점진 확대
```

파이프라인은 각 단계의 성공/실패 상태를 저장하고, 실패 시 로그를 제공한다. 또한 Slack, 이메일, GitHub PR status check, Jira 등과 연동해 개발자에게 결과를 알릴 수 있다. 이 피드백 루프가 빠를수록 개발자는 문제를 조기에 발견하고 수정할 수 있다.

---

---

## 실제 시스템 연결

실제 백엔드 시스템에서 CI/CD는 Linux 서버, Git 저장소, 빌드 도구, 웹 서버, 애플리케이션 서버, 클라우드 인프라와 긴밀하게 연결된다.

가장 단순한 예는 GitHub Actions를 이용해 Spring Boot 애플리케이션을 빌드하고, Linux EC2 서버에 배포하는 구조이다.

```text
[GitHub Repository]
    |
    | push to main
    v
[GitHub Actions Runner]
    |
    +--> ./gradlew test
    +--> ./gradlew bootJar
    +--> scp app.jar to EC2
    +--> ssh EC2 "systemctl restart app"
    v
[AWS EC2 Linux Server]
    |
    +--> systemd로 Java 애플리케이션 실행
    +--> Nginx가 Reverse Proxy 역할 수행
```

Linux 서버에서는 `systemd`를 이용해 백엔드 애플리케이션을 서비스로 등록할 수 있다. CI/CD 파이프라인은 SSH로 서버에 접속해 새 artifact를 업로드하고 `systemctl restart` 또는 무중단 배포 스크립트를 실행할 수 있다. Nginx는 외부 요청을 받아 내부 애플리케이션 포트로 전달하는 reverse proxy 역할을 한다. 예를 들어 사용자는 `https://api.example.com`으로 접근하지만, Nginx는 내부적으로 `localhost:8080`의 백엔드 서버로 요청을 전달할 수 있다.

```text
[Client]
   |
   v
[Nginx: 80/443]
   |
   v
[Backend App: 8080]
```

Jenkins를 사용하는 실제 시스템에서는 사내 네트워크에 Jenkins controller를 설치하고, 여러 agent를 연결하는 방식이 흔하다. 예를 들어 Linux agent는 Java 빌드에 사용하고, Docker가 설치된 agent는 컨테이너 이미지 빌드에 사용할 수 있다.

```text
[Jenkins Controller]
    |
    +--> [Agent 1: Java Build]
    |
    +--> [Agent 2: Docker Build]
    |
    +--> [Agent 3: Deployment Job]
```

Jenkins는 플러그인 생태계가 크기 때문에 GitHub Webhook, GitLab, Slack, Docker, Kubernetes, AWS 관련 플러그인과 연결할 수 있다. 다만 플러그인이 많아질수록 버전 호환성, 보안 업데이트, 권한 관리가 복잡해질 수 있다. GitHub Actions는 GitHub 저장소와 자연스럽게 통합되어 pull request 기반 검증, branch protection rule, status check와 연결하기 쉽다. 반면 Jenkins는 자체 호스팅 환경에서 네트워크, 실행 환경, 플러그인, 권한 모델을 더 세밀하게 제어할 수 있다는 장점이 있다.

실제 운영 환경에서는 CI/CD가 모니터링 시스템과도 연결된다. 배포 후 애플리케이션 헬스 체크 API를 호출하고, 실패하면 배포를 중단하거나 롤백할 수 있다. 예를 들어 `/health` 또는 `/actuator/health` 같은 엔드포인트를 호출해 애플리케이션이 정상 상태인지 확인한다. 또한 Prometheus, Grafana, CloudWatch 같은 모니터링 도구를 통해 에러율, 응답 시간, CPU 사용률, 메모리 사용량을 확인하고 배포 성공 여부를 판단할 수 있다.

---

---

## 클라우드 연결

CI/CD는 클라우드 네이티브 환경에서 Docker, Kubernetes, AWS, GCP 같은 서비스와 강하게 연결된다. 현대적인 백엔드 배포에서는 애플리케이션을 서버에 직접 복사하기보다 Docker 이미지로 패키징한 뒤, 컨테이너 레지스트리에 저장하고, 실행 환경에서 해당 이미지를 pull해 실행하는 방식이 자주 사용된다.

일반적인 Docker 기반 CI/CD 흐름은 다음과 같다.

```text
[Source Code]
    |
    v
[CI: Build & Test]
    |
    v
[Docker Build]
    |
    v
[Container Registry]
    |
    v
[Deployment Target]
    |
    +--> Docker Host
    +--> Kubernetes
    +--> AWS ECS
    +--> GCP Cloud Run
```

Docker를 사용하면 애플리케이션 실행 환경을 이미지로 고정할 수 있다. 예를 들어 Java 버전, OS 패키지, 애플리케이션 파일, 실행 명령을 Dockerfile에 정의한다. CI/CD 파이프라인은 Dockerfile을 기반으로 이미지를 빌드하고, 이미지 태그를 commit SHA나 release tag로 지정한다. 이렇게 하면 어떤 코드가 어떤 이미지로 배포되었는지 추적하기 쉽다.

Kubernetes 환경에서는 CI/CD가 Deployment, Service, Ingress, ConfigMap, Secret, Helm chart, Kustomize와 연결된다. 예를 들어 GitHub Actions가 Docker 이미지를 빌드해 Amazon ECR 또는 Google Artifact Registry에 push한 뒤, `kubectl set image` 또는 Helm upgrade를 통해 Kubernetes 클러스터에 새 버전을 배포할 수 있다.

```text
[GitHub Actions]
    |
    +--> docker build
    +--> docker push
    +--> helm upgrade
    v
[Kubernetes Cluster]
    |
    +--> Deployment
    +--> ReplicaSet
    +--> Pod
    +--> Service
    +--> Ingress
```

AWS에서는 다음 서비스들과 연결되는 경우가 많다.

- Amazon EC2: 가상 서버에 직접 배포
- Amazon ECR: Docker 이미지 저장소
- Amazon ECS: 컨테이너 오케스트레이션 서비스
- Amazon EKS: 관리형 Kubernetes 서비스
- AWS CodeDeploy: 배포 자동화 서비스
- AWS IAM: CI/CD 권한 제어
- Amazon S3: 정적 파일 또는 artifact 저장소
- Amazon CloudWatch: 로그와 메트릭 모니터링

GitHub Actions에서 AWS에 접근할 때는 장기 액세스 키를 저장하는 방식보다 OIDC 기반 federation을 사용하는 방식이 보안상 권장된다. 이 방식은 GitHub Actions가 AWS IAM Role을 임시 자격 증명으로 AssumeRole하도록 구성하는 방식이다. 단, 정확한 설정은 GitHub 저장소, 조직 정책, AWS IAM trust policy에 따라 달라진다.

GCP에서는 Cloud Run, Google Kubernetes Engine, Artifact Registry, Cloud Build, IAM 등과 연결할 수 있다. 예를 들어 GitHub Actions에서 Docker 이미지를 Artifact Registry에 push하고, Cloud Run 서비스를 새 이미지로 갱신하는 파이프라인을 구성할 수 있다.

클라우드 환경에서 중요한 점은 CI/CD 도구가 단순히 배포 명령을 실행하는 주체가 아니라, 클라우드 리소스를 변경할 수 있는 권한을 가진 자동화 계정이라는 점이다. 따라서 IAM 권한은 최소 권한 원칙에 따라 설정해야 하며, 운영 배포 권한과 개발/스테이징 배포 권한을 분리하는 것이 좋다.

---

---

## 보안 연결

CI/CD 파이프라인은 소스 코드, 비밀 정보, 빌드 결과물, 운영 인프라 권한을 모두 다루기 때문에 중요한 공격 표면이 된다. CI/CD 보안은 단순히 테스트를 추가하는 수준이 아니라, 공급망 보안, 권한 관리, 비밀 정보 보호, 실행 환경 격리, artifact 무결성 검증까지 포함한다.

대표적인 보안 이슈는 secret 노출이다. API Key, DB 비밀번호, 클라우드 액세스 키, SSH private key를 코드 저장소에 커밋하거나 CI 로그에 출력하면 공격자가 이를 이용해 인프라에 접근할 수 있다. GitHub Actions에서는 repository secrets, organization secrets, environment secrets를 사용할 수 있고, Jenkins에서는 Credentials Plugin 등을 통해 secret을 관리할 수 있다. 그러나 secret을 환경 변수로 주입한 뒤 스크립트에서 출력하면 로그에 노출될 수 있으므로 주의해야 한다.

두 번째 이슈는 과도한 권한이다. CI/CD 파이프라인이 운영 서버, Kubernetes 클러스터, 클라우드 계정에 접근할 수 있다면, 해당 파이프라인이 탈취되었을 때 피해 범위가 매우 커진다. 따라서 최소 권한 원칙을 적용해야 한다. 예를 들어 테스트 job에는 배포 권한이 없어야 하며, pull request 검증 job에는 운영 배포 secret을 제공하지 않는 것이 안전하다. 외부 기여자의 pull request에서 secret이 노출되지 않도록 GitHub Actions 이벤트 사용 방식에도 주의해야 한다.

세 번째 이슈는 dependency 및 supply chain 공격이다. 빌드 중 다운로드하는 오픈소스 패키지, GitHub Action, Jenkins 플러그인, Docker base image에 취약점이나 악성 코드가 포함될 수 있다. 따라서 다음과 같은 모범 사례가 필요하다.

- dependency lock file 사용
- 패키지 취약점 스캔 수행
- Docker image 취약점 스캔 수행
- 신뢰할 수 있는 base image 사용
- GitHub Actions의 third-party action은 가능한 commit SHA로 pinning
- Jenkins 플러그인 업데이트 및 불필요한 플러그인 제거
- 빌드 artifact 서명 및 검증 고려

네 번째 이슈는 self-hosted runner 또는 Jenkins agent의 격리 문제이다. 빌드 작업은 임의의 스크립트를 실행할 수 있으므로, runner에 민감한 파일이나 광범위한 네트워크 접근 권한이 있으면 위험하다. 특히 self-hosted runner가 운영 네트워크에 접근 가능하다면, 악성 PR 또는 잘못된 스크립트가 내부 시스템을 공격하는 경로가 될 수 있다. 따라서 runner는 격리된 환경에서 실행하고, job 종료 후 작업 디렉터리를 정리하며, 필요한 네트워크 접근만 허용하는 것이 좋다.

Jenkins의 경우 controller 보안이 특히 중요하다. Jenkins controller에는 job 설정, credential, 플러그인, 사용자 권한 정보가 모여 있다. 따라서 관리자 계정 보호, CSRF 보호 기능 유지, 플러그인 최신화, 권한 기반 접근 제어, controller에서 직접 빌드 실행 최소화, agent 격리 등이 필요하다.

GitHub Actions 보안 모범 사례는 다음과 같다.

```text
1. GITHUB_TOKEN 권한을 workflow 또는 job 단위로 최소화
2. 운영 배포는 protected environment와 required reviewer 사용
3. secret을 pull_request 검증에 무분별하게 제공하지 않기
4. third-party action 버전 고정
5. OIDC 기반 클라우드 인증 사용
6. dependency 및 container image 스캔 추가
7. branch protection rule과 required status checks 적용
```

CI/CD 보안의 핵심은 “자동화된 배포 권한은 곧 운영 인프라 변경 권한”이라는 관점이다. 따라서 파이프라인은 코드 품질을 높이는 도구인 동시에, 강력한 권한을 가진 자동화 시스템으로 다루어야 한다.

---

---

## 면접 질문

**Q1. CI와 CD의 차이는 무엇인가요?**  
> 핵심 답변: CI는 코드 변경 사항을 자주 통합하고 자동 빌드/테스트로 문제를 조기에 발견하는 과정이다. CD는 검증된 결과물을 배포 가능한 상태로 만들거나, 운영 환경까지 자동 배포하는 과정이다. Continuous Delivery는 수동 승인 후 배포 가능 상태를 의미하고, Continuous Deployment는 승인 없이 자동 운영 배포까지 수행하는 것을 의미한다.

**Q2. GitHub Actions와 Jenkins의 차이는 무엇인가요?**  
> 핵심 답변: GitHub Actions는 GitHub 저장소 이벤트와 밀접하게 통합된 CI/CD 서비스이며 workflow를 YAML로 정의한다. Jenkins는 자체 호스팅 가능한 범용 자동화 서버로, controller-agent 구조와 풍부한 플러그인 생태계를 가진다. GitHub Actions는 GitHub 기반 프로젝트에 편리하고, Jenkins는 사내망, 복잡한 커스텀 환경, 세밀한 인프라 제어가 필요한 경우 유용하다.

**Q3. CI/CD 파이프라인에서 artifact를 분리해 관리해야 하는 이유는 무엇인가요?**  
> 핵심 답변: artifact는 빌드 결과물이며, 동일한 artifact를 테스트 환경과 운영 환경에 배포해야 환경 간 차이로 인한 문제를 줄일 수 있다. commit과 artifact, 배포 이력을 연결하면 추적성과 롤백 가능성이 좋아진다. Docker image, jar 파일, Helm chart 등이 artifact가 될 수 있다.

**Q4. 무중단 배포를 CI/CD에서 어떻게 구현할 수 있나요?**  
> 핵심 답변: Rolling, Blue-Green, Canary 배포 전략을 사용할 수 있다. Rolling은 인스턴스를 순차 교체하고, Blue-Green은 기존 환경과 새 환경을 분리한 뒤 트래픽을 전환한다. Canary는 일부 트래픽만 새 버전으로 보내고 점진적으로 확대한다. 로드밸런서, 헬스 체크, 모니터링, 자동 롤백이 함께 필요하다.

**Q5. CI/CD 파이프라인에서 주의해야 할 보안 문제는 무엇인가요?**  
> 핵심 답변: secret 노출, 과도한 클라우드 권한, 악성 dependency, 취약한 third-party action 또는 Jenkins plugin, self-hosted runner 침해가 주요 위험이다. 최소 권한 원칙, secret manager 사용, OIDC 기반 임시 자격 증명, action 버전 고정, dependency/image 스캔, runner 격리, branch protection을 적용해야 한다.

---

---

## 관련 개념

- [[Continuous Integration]] - 코드 변경 사항을 자주 병합하고 자동 빌드/테스트를 수행하는 CI/CD의 핵심 단계이다.
- [[Continuous Delivery]] - 검증된 artifact를 언제든 배포 가능한 상태로 유지하는 배포 자동화 개념이다.
- [[Continuous Deployment]] - 테스트를 통과한 변경 사항을 운영 환경까지 자동 배포하는 방식이다.
- [[GitHub Actions]] - GitHub 이벤트 기반으로 workflow를 실행하는 대표적인 CI/CD 도구이다.
- [[Jenkins]] - 자체 호스팅 가능한 자동화 서버로 복잡한 빌드와 배포 파이프라인을 구성할 수 있다.
- [[Docker]] - 애플리케이션과 실행 환경을 이미지로 패키징하여 CI/CD 배포 단위를 표준화한다.
- [[Kubernetes]] - 컨테이너 배포, 롤링 업데이트, 스케일링, 서비스 디스커버리를 제공하는 주요 배포 대상이다.
- [[Artifact Registry]] - 빌드 결과물이나 컨테이너 이미지를 저장하고 배포 단계에서 참조하는 저장소이다.
- [[Blue-Green Deployment]] - 기존 운영 환경과 새 운영 환경을 분리해 트래픽 전환으로 배포 위험을 줄이는 전략이다.
- [[Canary Deployment]] - 일부 트래픽에만 새 버전을 노출하고 점진적으로 확대하는 안전한 배포 전략이다.
- [[Infrastructure as Code]] - Terraform, CloudFormation 등으로 인프라 변경을 코드화해 CI/CD와 함께 자동화할 수 있다.
- [[Secrets Management]] - API Key, DB 비밀번호, 클라우드 자격 증명을 안전하게 저장하고 파이프라인에 주입하는 개념이다.
