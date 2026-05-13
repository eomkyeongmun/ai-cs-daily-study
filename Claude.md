# AI CS Daily Study System

## 목표
매일 자동으로 CS 학습 노트를 생성하여 Obsidian Vault에 저장하고,
장기적으로 개인 CS 지식 베이스를 구축한다.

---

# 전체 구조

GitHub Actions
    ↓
Python Script
    ↓
OpenAI API
    ↓
Markdown 생성
    ↓
Obsidian Vault 저장

---

# 주요 기능

- 매일 자동 실행
- CS 주제 순차 학습
- Markdown 자동 생성
- Obsidian 연동
- Git 기반 버전 관리
- 면접 질문 자동 생성
- 관련 개념 자동 연결
- 클라우드/보안 관점 포함

---

# 학습 범위

## 1. Computer Architecture
- CPU
- Cache
- Memory
- Interrupt
- Pipeline

## 2. Operating System
- Process
- Thread
- Scheduling
- Synchronization
- Deadlock
- Virtual Memory

## 3. Network
- TCP/IP
- HTTP
- TLS
- DNS
- Load Balancer

## 4. Cloud / Infrastructure
- Docker
- Kubernetes
- IAM
- VPC
- CDN
- CI/CD

## 5. Database
- Index
- Transaction
- Isolation Level
- Join
- Sharding

## 6. Security
- Authentication
- OAuth
- JWT
- Zero Trust
- Encryption

---

# 생성되는 노트 예시

## 파일명
2026-05-13-Process-vs-Thread.md

## 포함 내용
- 핵심 개념
- 내부 동작 원리
- 실제 시스템 연결
- 클라우드 연결
- 보안 연결
- 면접 질문
- 관련 개념 링크

---

# 프로젝트 구조

project/
├─ topics.json
├─ generate.py
├─ templates/
├─ output/
├─ .github/workflows/
│  └─ cs-daily.yml
└─ README.md

---

# 사용 기술

- Python
- GitHub Actions
- OpenAI API
- Obsidian
- Markdown

---

# 향후 확장 예정

- 복습 자동화
- 난이도 조절
- 개인 약점 분석
- AI 면접 모드
- RAG 기반 검색
- 벡터 DB 연동
- 그림 자동 생성

---

# 최종 목표

"매일 자동으로 성장하는 개인 CS 위키 구축"