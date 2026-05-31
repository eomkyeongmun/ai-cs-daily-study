---
date: 2026-06-01
category: 백엔드 - 인프라
topic: 인프라 자동화 (IaC)
subtopic: 인프라를 코드로 관리 (Terraform, Ansible)
tags: [CS, 백엔드---인프라, study]
---

# 인프라 자동화 (IaC) - 인프라를 코드로 관리 (Terraform, Ansible)

## 핵심 개념

## 인프라 자동화(IaC, Infrastructure as Code) 핵심 개념

인프라 자동화, 특히 IaC는 서버, 네트워크, 보안 그룹, 로드 밸런서, 데이터베이스, Kubernetes 리소스 같은 인프라 구성 요소를 수동 콘솔 작업이 아니라 코드로 정의하고 관리하는 방식이다. 즉, “어떤 인프라가 존재해야 하는가” 또는 “서버가 어떤 상태여야 하는가”를 코드 파일에 선언하고, 도구가 이를 실제 환경에 적용한다.

대표적인 IaC 도구로는 **Terraform**과 **Ansible**이 있다. Terraform은 주로 클라우드 리소스 프로비저닝에 사용되며, AWS EC2, VPC, RDS, GCP Compute Engine, Kubernetes 리소스 등을 선언적으로 생성·수정·삭제한다. Ansible은 서버 설정 관리, 패키지 설치, 설정 파일 배포, 서비스 재시작 같은 작업에 강하며, SSH 기반으로 원격 서버에 명령을 실행한다.

IaC가 중요한 이유는 인프라 운영의 **재현성**, **일관성**, **버전 관리**, **자동화**, **감사 가능성**을 높이기 때문이다. 과거에는 운영자가 콘솔에서 직접 서버를 만들고 방화벽 규칙을 수정했기 때문에 누가 무엇을 변경했는지 추적하기 어렵고, 환경마다 설정 차이가 발생하기 쉬웠다. IaC를 사용하면 인프라 변경 이력이 Git에 남고, 코드 리뷰를 통해 변경을 검증할 수 있으며, 개발·스테이징·운영 환경을 동일한 방식으로 구성할 수 있다.

Terraform은 “목표 상태”를 코드로 정의하고 현재 상태와 비교하여 필요한 변경만 적용하는 방식에 가깝다. 반면 Ansible은 “작업 절차”를 플레이북으로 작성해 서버를 원하는 상태로 구성하는 데 적합하다. 실무에서는 Terraform으로 클라우드 인프라를 만들고, Ansible로 생성된 서버 내부를 설정하는 식으로 함께 사용하기도 한다.

---

---

## 내부 동작 원리

## 내부 동작 원리

### 1. Terraform의 동작 방식

Terraform은 선언형 IaC 도구다. 사용자는 HCL(HashiCorp Configuration Language) 형식으로 원하는 인프라 상태를 정의한다.

예시:

```hcl
resource "aws_instance" "web" {
  ami           = "ami-xxxxxxxx"
  instance_type = "t3.micro"

  tags = {
    Name = "web-server"
  }
}
```

Terraform의 주요 동작 과정은 다음과 같다.

```text
[Terraform 코드]
      |
      v
terraform init
      |
      v
Provider 플러그인 다운로드
      |
      v
terraform plan
      |
      v
현재 상태(State)와 목표 코드 비교
      |
      v
변경 계획 생성
      |
      v
terraform apply
      |
      v
클라우드 API 호출
      |
      v
실제 인프라 생성/수정/삭제
      |
      v
State 파일 갱신
```

### Terraform 주요 구성 요소

#### 1) Provider

Provider는 Terraform이 외부 시스템과 통신하기 위한 플러그인이다. AWS, GCP, Azure, Kubernetes, GitHub 등 다양한 Provider가 존재한다.

예:

```hcl
provider "aws" {
  region = "ap-northeast-2"
}
```

Terraform은 Provider를 통해 실제 클라우드 API를 호출한다. 예를 들어 AWS EC2 인스턴스를 만들 때 Terraform이 직접 서버를 생성하는 것이 아니라 AWS API에 요청을 보내는 방식이다.

#### 2) Resource

Resource는 생성하거나 관리할 인프라 단위다.

예:

```hcl
resource "aws_security_group" "web_sg" {
  name = "web-sg"
}
```

EC2, VPC, Subnet, IAM Role, RDS, S3 Bucket 등이 모두 Resource가 될 수 있다.

#### 3) State

Terraform의 핵심은 **State 파일**이다. State는 Terraform이 관리하는 리소스의 현재 상태를 저장한다.

예:

```text
terraform.tfstate
```

State에는 Terraform 코드와 실제 클라우드 리소스를 매핑하는 정보가 들어 있다. 예를 들어 코드상 `aws_instance.web`이 실제 AWS의 어떤 EC2 인스턴스 ID와 연결되는지 저장한다.

```text
Terraform 코드: aws_instance.web
        |
        v
State 파일: i-xxxxxxxxxxxx
        |
        v
AWS 실제 리소스: EC2 Instance
```

State가 없으면 Terraform은 어떤 리소스를 자신이 관리하고 있는지 알기 어렵다. 따라서 팀 환경에서는 로컬 State 파일 대신 S3, Terraform Cloud, GCS 같은 원격 백엔드를 사용하고, 동시에 여러 사람이 변경하지 못하도록 Locking을 적용하는 것이 일반적이다.

#### 4) Plan

`terraform plan`은 실제 변경을 적용하기 전에 어떤 작업이 수행될지 미리 보여준다.

예:

```text
+ create aws_instance.web
~ update aws_security_group.web_sg
- destroy aws_instance.old
```

기호 의미는 보통 다음과 같다.

```text
+ 생성
~ 수정
- 삭제
-/+ 재생성
```

이를 통해 운영자는 의도하지 않은 삭제나 변경을 사전에 확인할 수 있다.

#### 5) Apply

`terraform apply`는 Plan에서 계산된 변경 사항을 실제 인프라에 적용한다. 이 과정에서 Terraform은 Provider를 통해 클라우드 API를 호출한다.

---

### 2. Ansible의 동작 방식

Ansible은 구성 관리 및 자동화 도구다. Terraform이 인프라 리소스를 생성하는 데 강하다면, Ansible은 서버 내부 설정을 자동화하는 데 강하다.

Ansible의 기본 구조는 다음과 같다.

```text
[Control Node]
Ansible 실행 머신
      |
      | SSH
      v
[Managed Node 1]
[Managed Node 2]
[Managed Node 3]
```

Ansible은 일반적으로 Agent를 설치하지 않고 SSH를 통해 원격 서버에 접속한다. Windows 대상의 경우 WinRM을 사용할 수 있다.

### Ansible 주요 구성 요소

#### 1) Inventory

Inventory는 관리 대상 서버 목록이다.

예:

```ini
[web]
web1.example.com
web2.example.com

[db]
db1.example.com
```

#### 2) Playbook

Playbook은 YAML 형식으로 작성된 자동화 작업 정의 파일이다.

예:

```yaml
- name: Configure web servers
  hosts: web
  become: yes
  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present

    - name: Start nginx
      service:
        name: nginx
        state: started
        enabled: yes
```

위 Playbook은 web 그룹 서버에 접속해 Nginx를 설치하고 서비스를 시작한다.

#### 3) Module

Module은 실제 작업을 수행하는 단위다. 예를 들어 `apt`, `yum`, `dnf`, `copy`, `template`, `service`, `user`, `file` 등이 있다.

```yaml
- name: Copy nginx config
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
```

#### 4) Idempotency, 멱등성

Ansible의 중요한 특징 중 하나는 멱등성이다. 같은 Playbook을 여러 번 실행해도 결과 상태가 동일해야 한다는 의미다.

예를 들어 다음 작업은 Nginx가 이미 설치되어 있으면 다시 설치하지 않는다.

```yaml
- name: Install nginx
  apt:
    name: nginx
    state: present
```

단, 모든 Ansible 작업이 자동으로 멱등적인 것은 아니다. `shell`, `command` 모듈을 사용할 때는 멱등성을 직접 고려해야 한다.

예:

```yaml
- name: Create file only if not exists
  command: touch /tmp/example
  args:
    creates: /tmp/example
```

---

### 3. Terraform과 Ansible 비교

| 항목 | Terraform | Ansible |
|---|---|---|
| 주요 목적 | 인프라 프로비저닝 | 서버 설정 관리, 배포 자동화 |
| 방식 | 선언형 | 절차형에 가까운 선언적 작업 조합 |
| 상태 관리 | State 파일 사용 | 기본적으로 중앙 State 없음 |
| 통신 방식 | Provider를 통한 API 호출 | 주로 SSH/WinRM |
| 대표 사용처 | VPC, EC2, RDS, IAM, Kubernetes 리소스 생성 | 패키지 설치, 설정 파일 배포, 서비스 제어 |
| 언어 | HCL | YAML |
| 멱등성 | 목표 상태와 State 비교 | 모듈 단위 멱등성 지원 |

### 4. 함께 사용하는 흐름

```text
1. Terraform 코드 작성
   - VPC
   - Subnet
   - Security Group
   - EC2
   - Load Balancer

2. terraform apply
   - AWS 인프라 생성

3. Terraform Output으로 EC2 IP 출력

4. Ansible Inventory 생성

5. Ansible Playbook 실행
   - Nginx 설치
   - 애플리케이션 설정 배포
   - systemd 서비스 등록
```

다이어그램으로 표현하면 다음과 같다.

```text
[Git Repository]
   | 
   | Terraform 코드
   v
[Terraform]
   |
   | Cloud API
   v
[AWS/GCP/Azure 인프라 생성]
   |
   | 생성된 서버 IP/호스트 정보
   v
[Ansible Inventory]
   |
   | SSH 접속
   v
[서버 내부 설정]
   - 패키지 설치
   - 설정 파일 배포
   - 서비스 실행
```

---

---

## 실제 시스템 연결

## 실제 시스템 연결

### 1. Linux 서버 구성 자동화

Linux 서버를 수동으로 구성할 경우 다음 작업을 직접 수행해야 한다.

```bash
sudo apt update
sudo apt install nginx
sudo systemctl enable nginx
sudo systemctl start nginx
sudo vi /etc/nginx/nginx.conf
```

Ansible을 사용하면 위 작업을 Playbook으로 관리할 수 있다.

```yaml
- name: Configure nginx server
  hosts: web
  become: yes
  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present
        update_cache: yes

    - name: Deploy nginx config
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      notify:
        - Restart nginx

    - name: Ensure nginx is running
      service:
        name: nginx
        state: started
        enabled: yes

  handlers:
    - name: Restart nginx
      service:
        name: nginx
        state: restarted
```

여기서 `notify`와 `handlers`를 사용하면 설정 파일이 변경되었을 때만 Nginx를 재시작할 수 있다. 이는 불필요한 서비스 재시작을 줄이는 데 유용하다.

---

### 2. AWS 인프라 자동화 예시

Terraform으로 AWS에 기본적인 웹 서버 인프라를 구성할 수 있다.

구성 예:

```text
VPC
 ├── Public Subnet
 ├── Internet Gateway
 ├── Route Table
 ├── Security Group
 └── EC2 Instance
```

Terraform 코드 구조 예:

```text
infra/
 ├── main.tf
 ├── variables.tf
 ├── outputs.tf
 ├── provider.tf
 └── terraform.tfvars
```

예시 코드:

```hcl
provider "aws" {
  region = var.aws_region
}

resource "aws_instance" "web" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.web.id]

  tags = {
    Name = "terraform-web"
  }
}

resource "aws_security_group" "web" {
  name = "web-sg"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.admin_ip_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

위 구성은 HTTP 80 포트는 전체 공개하고, SSH 22 포트는 관리자 IP 대역으로 제한하는 구조다.

---

### 3. Nginx 배포 자동화

Terraform으로 EC2를 만든 뒤 Ansible로 Nginx를 설치하는 구조는 실무에서 자주 사용된다.

```text
Terraform:
  - EC2 생성
  - Security Group 생성
  - Public IP 출력

Ansible:
  - EC2에 SSH 접속
  - Nginx 설치
  - 설정 파일 배포
  - 서비스 시작
```

Terraform Output 예:

```hcl
output "web_public_ip" {
  value = aws_instance.web.public_ip
}
```

Ansible Inventory 예:

```ini
[web]
13.xxx.xxx.xxx ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/my-key.pem
```

Ansible 실행:

```bash
ansible-playbook -i inventory.ini nginx.yml
```

---

### 4. GCP 환경에서의 예시

Terraform은 GCP Provider를 사용해 Compute Engine, VPC Network, Firewall Rule 등을 관리할 수 있다.

예시 개념 구조:

```text
google_compute_network
google_compute_subnetwork
google_compute_firewall
google_compute_instance
```

GCP에서도 Terraform이 직접 리소스를 생성하는 것이 아니라 Google Cloud API를 호출한다. 인증은 일반적으로 Google Cloud 서비스 계정 키, Application Default Credentials, Workload Identity Federation 등의 방식을 사용할 수 있다.

⚠️ 확인 필요: 조직의 보안 정책에 따라 서비스 계정 키 파일 사용이 금지되거나 제한될 수 있으므로, 실제 환경에서는 해당 조직의 클라우드 인증 정책을 확인해야 한다.

---

### 5. 운영 환경에서의 GitOps/IaC 흐름

실제 운영에서는 Terraform 코드와 Ansible Playbook을 Git 저장소에 두고 Pull Request 기반으로 변경한다.

```text
개발자/운영자
   |
   | Pull Request
   v
Git Repository
   |
   | CI Pipeline
   v
terraform fmt
terraform validate
terraform plan
   |
   | 리뷰 및 승인
   v
terraform apply
   |
   v
Ansible Playbook 실행
```

이 방식은 다음 장점을 가진다.

- 변경 이력 추적 가능
- 코드 리뷰 가능
- 자동 검증 가능
- 승인 기반 운영 가능
- 롤백 전략 수립 가능
- 환경별 코드 재사용 가능

---

---

## 클라우드 연결

## 클라우드 연결

### 1. AWS와 Terraform

Terraform은 AWS 리소스 관리에 널리 사용된다. 관리 가능한 대표 리소스는 다음과 같다.

- VPC
- Subnet
- Route Table
- Internet Gateway
- NAT Gateway
- Security Group
- EC2
- Auto Scaling Group
- Elastic Load Balancer
- RDS
- S3
- IAM Role / Policy
- EKS

예를 들어 EKS 클러스터를 Terraform으로 생성하고, 이후 Kubernetes Provider나 Helm Provider를 사용해 클러스터 내부 리소스를 관리할 수 있다.

```text
Terraform AWS Provider
   |
   v
EKS Cluster 생성
   |
   v
Terraform Kubernetes Provider / Helm Provider
   |
   v
Deployment, Service, Ingress, Helm Chart 배포
```

---

### 2. Docker와의 연관성

Docker 자체는 애플리케이션 실행 환경을 컨테이너 이미지로 패키징하는 기술이다. IaC와 직접적으로 같은 범주의 도구는 아니지만, 배포 자동화 측면에서 함께 사용된다.

예:

```text
Terraform:
  - VM 또는 Kubernetes 클러스터 생성

Ansible:
  - Docker Engine 설치
  - Docker Compose 파일 배포
  - 컨테이너 실행

Docker:
  - 애플리케이션 컨테이너 실행
```

Ansible Playbook 예:

```yaml
- name: Install Docker and run app
  hosts: app
  become: yes
  tasks:
    - name: Install docker package
      apt:
        name: docker.io
        state: present
        update_cache: yes

    - name: Start docker
      service:
        name: docker
        state: started
        enabled: yes
```

⚠️ 확인 필요: Linux 배포판과 설치 방식에 따라 Docker 패키지 이름, 저장소 설정, 권장 설치 절차가 다를 수 있다.

---

### 3. Kubernetes와의 연관성

Kubernetes 환경에서도 IaC는 중요하다. 클러스터 자체와 클러스터 내부 리소스를 모두 코드로 관리할 수 있다.

```text
클러스터 외부 인프라:
  - VPC
  - Subnet
  - Load Balancer
  - IAM
  - Node Group

클러스터 내부 리소스:
  - Namespace
  - Deployment
  - Service
  - ConfigMap
  - Secret
  - Ingress
```

Terraform은 EKS, GKE, AKS 같은 Managed Kubernetes 클러스터를 만들 수 있다. 또한 Kubernetes Provider를 통해 Kubernetes 리소스를 관리할 수 있다.

Ansible은 Kubernetes 모듈을 통해 리소스를 적용할 수 있으며, Helm Chart 배포 자동화에도 사용될 수 있다.

일반적인 구조:

```text
Terraform:
  - 네트워크 구성
  - Kubernetes 클러스터 생성
  - 노드 그룹 생성
  - IAM 권한 구성

Helm / Argo CD / kubectl / Ansible:
  - 애플리케이션 배포
  - Ingress 구성
  - ConfigMap/Secret 관리
```

---

### 4. CI/CD와 IaC

IaC는 CI/CD 파이프라인과 결합하면 강력해진다.

예시 파이프라인:

```text
Pull Request 생성
   |
   v
terraform fmt 검사
   |
   v
terraform validate
   |
   v
terraform plan
   |
   v
Plan 결과를 PR에 표시
   |
   v
승인
   |
   v
terraform apply
```

Ansible의 경우:

```text
애플리케이션 릴리즈
   |
   v
Ansible Playbook 실행
   |
   v
서버 설정 변경
   |
   v
서비스 재시작 또는 롤링 배포
```

운영 환경에서는 `apply` 같은 실제 변경 작업을 자동으로 실행하기 전에 승인 절차를 두는 것이 안전하다.

---

### 5. 클라우드 네이티브 환경에서의 역할 분리

실무에서는 다음처럼 역할을 나누는 경우가 많다.

```text
Terraform:
  - 클라우드 리소스 생성
  - 네트워크/IAM/DB/클러스터 관리

Ansible:
  - VM 내부 설정
  - 패키지 설치
  - 보안 설정
  - 레거시 서버 관리

Helm:
  - Kubernetes 애플리케이션 패키징

Argo CD / Flux:
  - GitOps 기반 Kubernetes 배포
```

Terraform과 Ansible은 경쟁 관계라기보다 목적이 다르다. Terraform은 인프라의 생명주기 관리에 강하고, Ansible은 서버 내부 상태 구성과 작업 자동화에 강하다.

---

---

## 보안 연결

## 보안 연결

### 1. State 파일 보안

Terraform State 파일은 매우 민감할 수 있다. 리소스 ID, 속성 값, 경우에 따라 민감한 설정 값이 포함될 수 있기 때문이다. 예를 들어 데이터베이스 초기 비밀번호, 액세스 키, 인증 토큰 등이 State에 남을 수 있다.

따라서 다음 보안 원칙을 지켜야 한다.

- State 파일을 Git에 커밋하지 않는다.
- 원격 Backend를 사용한다.
- Backend 저장소 암호화를 활성화한다.
- State 접근 권한을 최소화한다.
- State Locking을 사용해 동시 변경을 방지한다.
- 민감 값은 Secret Manager, Parameter Store, Vault 등으로 분리한다.

AWS 예시:

```text
S3 Backend:
  - S3 버킷에 State 저장
  - 서버 측 암호화 사용
  - IAM으로 접근 제어

DynamoDB:
  - State Locking에 사용 가능
```

⚠️ 확인 필요: Terraform 버전 및 Backend 구성 방식에 따라 Locking 지원 방식이 다를 수 있으므로 사용하는 Backend의 공식 문서를 확인해야 한다.

---

### 2. 클라우드 자격 증명 관리

Terraform과 Ansible은 클라우드 API 또는 원격 서버에 접근하기 위해 자격 증명이 필요하다. 이 자격 증명을 코드에 하드코딩하면 매우 위험하다.

나쁜 예:

```hcl
provider "aws" {
  access_key = "AKIA..."
  secret_key = "..."
}
```

권장 방식:

- 환경 변수 사용
- IAM Role 사용
- Workload Identity 사용
- OIDC 기반 CI/CD 인증 사용
- Secret Manager 사용
- 단기 자격 증명 사용

CI/CD에서 Terraform을 실행할 경우 장기 Access Key를 저장하는 것보다 OIDC 기반으로 클라우드 역할을 위임받는 방식이 더 안전한 경우가 많다.

⚠️ 확인 필요: CI/CD 플랫폼과 클라우드 제공자별 OIDC 연동 방식은 다르므로 실제 설정은 공식 문서를 기준으로 검증해야 한다.

---

### 3. 최소 권한 원칙

IaC 도구는 강력한 권한을 가질 수 있다. 예를 들어 Terraform에 관리자 권한을 부여하면 네트워크, IAM, 데이터베이스, 스토리지를 모두 수정할 수 있다. 이는 실수나 침해 사고 발생 시 피해 범위를 크게 키운다.

모범 사례:

```text
- 환경별 IAM Role 분리
- 작업별 권한 분리
- 읽기 전용 Plan 권한과 Apply 권한 분리
- 운영 환경 Apply 권한 제한
- 관리자 승인 후 변경
- CloudTrail, Audit Log 활성화
```

예:

```text
dev-terraform-role
staging-terraform-role
prod-terraform-role
```

운영 환경의 Terraform 실행 권한은 제한된 사용자 또는 승인된 CI/CD 파이프라인에만 부여하는 것이 좋다.

---

### 4. SSH 키와 Ansible 보안

Ansible은 일반적으로 SSH로 서버에 접근한다. 따라서 SSH 키 관리가 중요하다.

보안 권장 사항:

- 개인 키를 Git에 저장하지 않는다.
- SSH 키 권한을 제한한다.
- 서버별 또는 환경별 키를 분리한다.
- 가능하면 Bastion Host 또는 Session Manager 사용을 고려한다.
- `become` 권한 사용 시 sudo 정책을 명확히 제한한다.
- Inventory에 비밀번호를 평문으로 저장하지 않는다.

Ansible Vault를 사용하면 민감 정보를 암호화할 수 있다.

예:

```bash
ansible-vault encrypt group_vars/prod.yml
```

암호화된 변수 파일을 Playbook에서 사용할 수 있다.

---

### 5. 보안 그룹과 방화벽 자동화의 위험

IaC로 보안 그룹을 관리하면 변경이 추적 가능하다는 장점이 있다. 하지만 잘못 작성된 코드가 그대로 적용되면 보안 사고로 이어질 수 있다.

위험한 예:

```hcl
ingress {
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}
```

SSH를 전 세계에 공개하는 구성은 공격 표면을 넓힌다.

권장:

```hcl
ingress {
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = [var.admin_ip_cidr]
}
```

추가적으로 다음 검사를 자동화할 수 있다.

- `0.0.0.0/0`로 열린 관리 포트 탐지
- 퍼블릭 S3 버킷 탐지
- 과도한 IAM 권한 탐지
- 암호화되지 않은 스토리지 탐지
- 태그 누락 탐지

도구 예:

- tfsec
- Checkov
- Terrascan
- Open Policy Agent
- Sentinel

⚠️ 확인 필요: 각 도구의 지원 범위와 정책 문법은 버전별로 달라질 수 있으므로 도입 전 공식 문서를 확인해야 한다.

---

### 6. Drift 탐지

Drift란 코드상 정의된 인프라 상태와 실제 클라우드 상태가 달라진 것을 의미한다.

예:

```text
Terraform 코드:
  Security Group 80 포트만 허용

실제 AWS 콘솔:
  누군가 22 포트를 0.0.0.0/0으로 추가

결과:
  코드와 실제 상태 불일치
```

Drift는 수동 콘솔 작업, 긴급 변경, 외부 시스템 변경 등으로 발생할 수 있다.

대응 방법:

- 정기적으로 `terraform plan` 실행
- 클라우드 감사 로그 확인
- 콘솔 직접 변경 제한
- IaC 외 변경 탐지 알림 구성
- 변경은 Pull Request 기반으로 수행

Drift를 방치하면 운영 환경의 재현성과 보안성이 떨어진다.

---

---

## 면접 질문

**Q1. IaC가 무엇이며 왜 필요한가요?**  
> 핵심 답변: IaC는 서버, 네트워크, DB, 보안 설정 등 인프라를 코드로 정의하고 관리하는 방식이다. 수동 작업을 줄이고, 재현성·일관성·버전 관리·감사 가능성을 높인다. Git 기반 변경 관리와 코드 리뷰를 통해 운영 안정성을 향상시킬 수 있다.

**Q2. Terraform과 Ansible의 차이는 무엇인가요?**  
> 핵심 답변: Terraform은 주로 클라우드 리소스 프로비저닝에 사용되며 Provider API와 State 파일을 기반으로 목표 상태를 관리한다. Ansible은 주로 서버 설정 관리와 작업 자동화에 사용되며 SSH/WinRM으로 대상 서버에 접속해 Playbook을 실행한다. Terraform은 인프라 생명주기 관리에 강하고, Ansible은 서버 내부 구성에 강하다.

**Q3. Terraform State 파일이 중요한 이유는 무엇인가요?**  
> 핵심 답변: State 파일은 Terraform 코드의 리소스와 실제 인프라 리소스의 매핑 정보를 저장한다. 이를 통해 Terraform은 어떤 리소스를 생성, 수정, 삭제해야 하는지 판단한다. State에는 민감 정보가 포함될 수 있으므로 Git에 저장하면 안 되며, 원격 Backend, 암호화, 접근 제어, Locking을 적용하는 것이 좋다.

**Q4. Ansible의 멱등성이란 무엇인가요?**  
> 핵심 답변: 멱등성은 같은 작업을 여러 번 실행해도 최종 상태가 동일하게 유지되는 성질이다. 예를 들어 `apt` 모듈로 `state: present`를 지정하면 패키지가 이미 설치된 경우 불필요한 변경을 하지 않는다. 다만 `shell`, `command` 모듈은 멱등성을 직접 보장해야 하므로 `creates`, `removes`, 조건문 등을 활용해야 한다.

**Q5. IaC를 운영 환경에 적용할 때 주의해야 할 보안 사항은 무엇인가요?**  
> 핵심 답변: 클라우드 자격 증명을 코드에 하드코딩하지 않고, State 파일을 안전하게 관리해야 한다. 최소 권한 원칙을 적용하고 운영 환경 Apply 권한을 제한해야 한다. 보안 그룹, IAM 정책, 퍼블릭 접근 설정은 자동 검사 도구로 검증하는 것이 좋다. Ansible 사용 시 SSH 키와 Vault 관리도 중요하다.

---

---

## 관련 개념

- [[Terraform]] - 클라우드 인프라를 선언형 코드로 정의하고 State 기반으로 관리하는 대표 IaC 도구
- [[Ansible]] - SSH 기반으로 서버 설정, 패키지 설치, 서비스 제어를 자동화하는 구성 관리 도구
- [[Infrastructure as Code]] - 인프라를 코드로 관리하는 전체 개념이며 Terraform과 Ansible의 상위 개념
- [[Configuration Management]] - 서버 내부 설정과 패키지, 서비스 상태를 일관되게 관리하는 개념
- [[Provisioning]] - 서버, 네트워크, 스토리지 등 인프라 리소스를 생성하고 준비하는 과정
- [[Terraform State]] - Terraform이 실제 리소스와 코드 리소스를 매핑하기 위해 사용하는 상태 정보
- [[Idempotency]] - 같은 작업을 여러 번 실행해도 동일한 결과를 보장하는 자동화의 핵심 성질
- [[GitOps]] - Git 저장소를 단일 진실 공급원으로 삼아 인프라와 애플리케이션 배포를 관리하는 방식
- [[CI/CD Pipeline]] - IaC 코드를 검증하고 배포하기 위한 자동화 실행 흐름
- [[AWS IAM]] - Terraform이나 Ansible이 클라우드 리소스에 접근할 때 필요한 권한 제어 체계
- [[Kubernetes]] - IaC로 클러스터와 내부 리소스를 관리할 수 있는 컨테이너 오케스트레이션 플랫폼
- [[Secret Management]] - API 키, 비밀번호, 인증 토큰 같은 민감 정보를 안전하게 저장하고 사용하는 방식
