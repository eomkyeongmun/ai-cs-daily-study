---
date: 2026-05-16
category: CS 기초 - 운영체제
topic: CPU 스케줄링
subtopic: FCFS, SJF, Round Robin, Priority Scheduling, 멀티 레벨 큐
tags: [CS, CS-기초---운영체제, study]
---

# CPU 스케줄링 - FCFS, SJF, Round Robin, Priority Scheduling, 멀티 레벨 큐

## 핵심 개념

# CPU 스케줄링 핵심 개념

CPU 스케줄링은 운영체제가 **준비 상태(Ready State)** 에 있는 여러 프로세스 또는 스레드 중에서 다음에 CPU를 사용할 대상을 선택하는 정책과 메커니즘을 의미한다. CPU는 한 순간에 제한된 수의 실행 흐름만 처리할 수 있기 때문에, 운영체제는 어떤 작업을 먼저 실행할지 결정해야 한다. 이 결정은 시스템의 **응답 시간(Response Time)**, **대기 시간(Waiting Time)**, **반환 시간(Turnaround Time)**, **처리량(Throughput)**, **공정성(Fairness)** 에 직접적인 영향을 준다.

CPU 스케줄링이 중요한 이유는 시스템의 성격에 따라 최적의 기준이 달라지기 때문이다. 예를 들어 배치 처리 시스템에서는 전체 작업 완료 시간이 중요하고, 대화형 시스템에서는 사용자의 입력에 빠르게 반응하는 것이 중요하다. 실시간 시스템에서는 정해진 시간 안에 작업을 완료하는 것이 핵심이다. 따라서 운영체제는 단순히 “빨리 끝나는 작업”만 선택하는 것이 아니라, 시스템 목표에 맞게 다양한 스케줄링 알고리즘을 조합하거나 변형해서 사용한다.

대표적인 CPU 스케줄링 알고리즘에는 **FCFS**, **SJF**, **Round Robin**, **Priority Scheduling**, **멀티 레벨 큐**가 있다.

## 주요 알고리즘 개요

| 알고리즘 | 핵심 아이디어 | 장점 | 단점 |
|---|---|---|---|
| FCFS | 먼저 도착한 작업을 먼저 실행 | 단순하고 구현 쉬움 | Convoy Effect 발생 가능 |
| SJF | 실행 시간이 짧은 작업 먼저 실행 | 평균 대기 시간 감소 | 실행 시간 예측 어려움, 긴 작업 기아 가능 |
| Round Robin | 정해진 시간 할당량만큼 번갈아 실행 | 응답성 좋음, 시분할 시스템에 적합 | 시간 할당량 설정이 중요 |
| Priority Scheduling | 우선순위가 높은 작업 먼저 실행 | 중요 작업 우선 처리 가능 | 낮은 우선순위 작업 기아 가능 |
| 멀티 레벨 큐 | 작업 유형별로 큐를 분리 | 작업 성격별 정책 적용 가능 | 큐 간 공정성 문제 가능 |

## 선점형과 비선점형

CPU 스케줄링은 크게 **선점형(Preemptive)** 과 **비선점형(Non-preemptive)** 으로 나뉜다.

- **비선점형 스케줄링**
  - 한 프로세스가 CPU를 받으면 자발적으로 종료하거나 I/O 대기 상태가 될 때까지 CPU를 계속 사용한다.
  - FCFS, 비선점형 SJF 등이 대표적이다.
  - 문맥 교환 오버헤드는 적지만, 응답성이 떨어질 수 있다.

- **선점형 스케줄링**
  - 운영체제가 실행 중인 프로세스를 중단시키고 다른 프로세스에 CPU를 줄 수 있다.
  - Round Robin, 선점형 Priority Scheduling 등이 대표적이다.
  - 응답성은 좋지만 문맥 교환 비용이 발생한다.

CPU 스케줄링은 단순한 알고리즘 문제가 아니라, 실제 운영체제의 성능, 클라우드 환경의 자원 격리, 컨테이너의 CPU 제한, 보안적 서비스 거부 공격 대응과도 연결되는 핵심 개념이다.

---

---

## 내부 동작 원리

# CPU 스케줄링 내부 동작 원리

CPU 스케줄링은 보통 다음과 같은 흐름으로 동작한다.

```text
프로세스 생성
   ↓
Ready Queue 진입
   ↓
Scheduler가 실행 대상 선택
   ↓
Dispatcher가 CPU 할당
   ↓
프로세스 실행
   ↓
 ┌───────────────┬───────────────┬───────────────┐
 │ 종료          │ I/O 대기       │ 선점 발생      │
 └───────────────┴───────────────┴───────────────┘
                 ↓
           Ready Queue 재진입
```

## 주요 구성 요소

### 1. Ready Queue

Ready Queue는 CPU를 사용할 준비가 되었지만 아직 실행되지 못한 프로세스들이 대기하는 큐다. 스케줄링 알고리즘에 따라 큐의 구조가 달라진다.

- FCFS: FIFO 큐
- SJF: 실행 시간이 짧은 순서의 우선순위 큐
- Round Robin: 순환 큐
- Priority Scheduling: 우선순위 큐
- 멀티 레벨 큐: 여러 개의 큐

### 2. Scheduler

Scheduler는 Ready Queue에서 다음 실행 대상을 고른다. 이때 알고리즘에 따라 선택 기준이 달라진다.

### 3. Dispatcher

Dispatcher는 선택된 프로세스에 CPU를 실제로 넘긴다. 이 과정에서 다음 작업이 일어난다.

- 현재 프로세스의 레지스터 상태 저장
- 다음 프로세스의 레지스터 상태 복원
- 메모리 관리 정보 전환
- 사용자 모드로 전환
- 프로그램 카운터 갱신

이 과정을 **문맥 교환(Context Switching)** 이라고 한다.

---

## 1. FCFS: First-Come, First-Served

FCFS는 **먼저 도착한 프로세스가 먼저 CPU를 사용하는 방식**이다. 일반적인 FIFO 큐와 같다.

### 동작 과정

```text
Ready Queue

[P1] → [P2] → [P3] → [P4]

CPU는 P1부터 실행
```

P1이 끝나야 P2가 실행되고, P2가 끝나야 P3가 실행된다.

### 예시

| 프로세스 | 도착 시간 | CPU Burst |
|---|---:|---:|
| P1 | 0 | 10 |
| P2 | 1 | 2 |
| P3 | 2 | 1 |

실행 순서:

```text
0          10     12   13
|---- P1 ----|--P2--|P3|
```

이 경우 P2와 P3는 짧은 작업임에도 P1이 끝날 때까지 오래 기다려야 한다. 이를 **Convoy Effect**라고 한다. 긴 CPU 중심 작업이 앞에 있으면 뒤의 짧은 작업들이 줄줄이 대기하면서 평균 대기 시간이 증가한다.

### 특징

- 구현이 매우 단순하다.
- 비선점형 방식이다.
- 평균 대기 시간이 길어질 수 있다.
- 대화형 시스템에는 적합하지 않다.

---

## 2. SJF: Shortest Job First

SJF는 **CPU Burst 시간이 가장 짧은 작업을 먼저 실행하는 방식**이다. 이론적으로 모든 프로세스가 동시에 도착하고 CPU Burst를 정확히 알고 있다면 평균 대기 시간을 최소화하는 알고리즘으로 알려져 있다.

### 동작 과정

```text
Ready Queue

[P1: 8ms] [P2: 4ms] [P3: 2ms] [P4: 1ms]

정렬 후 실행

[P4] → [P3] → [P2] → [P1]
```

### 비선점형 SJF

한 번 CPU를 받은 프로세스는 끝날 때까지 실행된다.

```text
0   1     3       7             15
|P4|--P3--|---P2---|-----P1------|
```

### 선점형 SJF: SRTF

선점형 SJF는 보통 **SRTF(Shortest Remaining Time First)** 라고 부른다. 새로 도착한 프로세스의 남은 실행 시간이 현재 실행 중인 프로세스의 남은 시간보다 짧으면 CPU를 선점한다.

```text
현재 실행 중: P1, 남은 시간 8ms
새로 도착: P2, 예상 실행 시간 3ms

P2가 P1을 선점
```

### 한계

SJF의 핵심 문제는 **미래의 CPU Burst 시간을 정확히 알기 어렵다**는 점이다. 실제 운영체제는 과거 실행 기록을 바탕으로 다음 CPU Burst를 추정할 수 있다.

대표적인 추정 방식은 지수 평균이다.

```text
예상값_new = α × 실제값_previous + (1 - α) × 예상값_previous
```

여기서 α는 최근 실행 기록을 얼마나 강하게 반영할지 결정하는 값이다.

### 특징

- 평균 대기 시간을 줄이는 데 효과적이다.
- 짧은 작업에 유리하다.
- 긴 작업은 계속 밀려 **기아(Starvation)** 상태가 될 수 있다.
- CPU Burst 예측이 어렵다.

---

## 3. Round Robin

Round Robin은 각 프로세스에 **동일한 시간 할당량(Time Quantum)** 을 부여하고, 시간이 끝나면 다음 프로세스로 CPU를 넘기는 방식이다. 시분할 시스템에서 널리 설명되는 대표적 스케줄링 알고리즘이다.

### 동작 과정

```text
Ready Queue

[P1] → [P2] → [P3] → [P4]
 ↑                      ↓
 └──────── 순환 ────────┘
```

각 프로세스는 최대 q만큼 실행된다.

```text
Time Quantum = 4ms

0    4    8    12   16   20
| P1 | P2 | P3 | P1 | P4 |
```

P1이 4ms 안에 끝나지 않으면 다시 Ready Queue의 뒤로 들어간다.

### 시간 할당량의 영향

| Time Quantum | 결과 |
|---|---|
| 너무 작음 | 문맥 교환이 자주 발생하여 오버헤드 증가 |
| 너무 큼 | FCFS와 유사해져 응답성 저하 |
| 적절함 | 대화형 작업의 응답성 확보 |

### 특징

- 선점형 알고리즘이다.
- 모든 프로세스가 공정하게 CPU를 나눠 받는다.
- 응답 시간이 중요한 대화형 시스템에 적합하다.
- 시간 할당량 설정이 성능에 큰 영향을 준다.

---

## 4. Priority Scheduling

Priority Scheduling은 각 프로세스에 부여된 **우선순위(Priority)** 를 기준으로 CPU를 할당하는 방식이다. 우선순위가 높은 프로세스가 먼저 실행된다.

### 동작 과정

```text
Ready Queue

[P1: priority 3]
[P2: priority 1]
[P3: priority 5]

우선순위 기준 선택
```

주의할 점은 시스템마다 숫자가 작을수록 높은 우선순위인지, 숫자가 클수록 높은 우선순위인지 다를 수 있다는 것이다.

### 선점형 Priority Scheduling

새로 도착한 프로세스의 우선순위가 현재 실행 중인 프로세스보다 높으면 CPU를 빼앗는다.

```text
현재 실행: P1(priority 5)
새로 도착: P2(priority 1, 더 높은 우선순위)

P2가 P1을 선점
```

### 비선점형 Priority Scheduling

현재 실행 중인 프로세스는 끝날 때까지 실행되고, 다음 선택 시점에 우선순위가 높은 프로세스가 선택된다.

### 기아와 Aging

Priority Scheduling의 대표적인 문제는 낮은 우선순위 프로세스가 계속 실행되지 못하는 **기아(Starvation)** 이다. 이를 완화하기 위해 **Aging** 기법을 사용한다.

Aging은 오래 기다린 프로세스의 우선순위를 점진적으로 높이는 방식이다.

```text
대기 시간 증가
   ↓
우선순위 상승
   ↓
언젠가 CPU를 할당받음
```

### 특징

- 중요 작업을 먼저 처리할 수 있다.
- 실시간 작업이나 시스템 작업에 유용하다.
- 우선순위 설정이 부적절하면 공정성이 떨어진다.
- Priority Inversion 문제가 발생할 수 있다.

---

## 5. 멀티 레벨 큐: Multilevel Queue

멀티 레벨 큐 스케줄링은 Ready Queue를 하나만 두지 않고, 프로세스 유형에 따라 여러 큐로 나누는 방식이다.

예를 들면 다음과 같이 나눌 수 있다.

```text
Queue 0: 시스템 프로세스
Queue 1: 대화형 프로세스
Queue 2: 배치 프로세스
Queue 3: 백그라운드 프로세스
```

### 구조 다이어그램

```text
높은 우선순위
┌────────────────────────┐
│ Q0: System Processes   │  ← Priority Scheduling
└────────────────────────┘
┌────────────────────────┐
│ Q1: Interactive Tasks  │  ← Round Robin
└────────────────────────┘
┌────────────────────────┐
│ Q2: Batch Jobs         │  ← FCFS
└────────────────────────┘
┌────────────────────────┐
│ Q3: Background Jobs    │  ← FCFS
└────────────────────────┘
낮은 우선순위
```

큐마다 다른 스케줄링 알고리즘을 적용할 수 있다. 예를 들어 대화형 작업 큐는 Round Robin을 사용하고, 배치 작업 큐는 FCFS를 사용할 수 있다.

### 큐 간 스케줄링

멀티 레벨 큐에서는 두 가지 결정이 필요하다.

1. 각 큐 내부에서 어떤 프로세스를 실행할 것인가?
2. 여러 큐 중 어떤 큐를 먼저 실행할 것인가?

큐 간 스케줄링 방식은 다음과 같다.

### 고정 우선순위 방식

상위 큐가 비어 있을 때만 하위 큐가 실행된다.

```text
Q0에 작업 있음 → Q0 실행
Q0 비어 있음, Q1에 작업 있음 → Q1 실행
Q0, Q1 비어 있음, Q2 실행
```

단점은 하위 큐의 기아 가능성이다.

### 시간 분할 방식

각 큐에 CPU 비율을 배정한다.

```text
Q0: CPU 50%
Q1: CPU 30%
Q2: CPU 20%
```

이 방식은 하위 큐도 일정 비율의 CPU를 받을 수 있어 기아를 완화할 수 있다.

---

## 멀티 레벨 피드백 큐와의 차이

멀티 레벨 큐는 일반적으로 프로세스가 한 큐에 고정된다. 반면 **멀티 레벨 피드백 큐(MLFQ)** 는 프로세스의 동작에 따라 큐 사이를 이동할 수 있다.

```text
짧게 CPU 사용 후 I/O 대기 → 높은 우선순위 유지
CPU를 오래 사용 → 낮은 우선순위 큐로 강등
오래 대기 → 높은 우선순위 큐로 승격 가능
```

MLFQ는 대화형 작업을 우대하면서도 CPU 중심 작업을 처리하기 위한 현실적인 스케줄링 모델로 자주 설명된다.

---

---

## 실제 시스템 연결

# 실제 시스템에서의 CPU 스케줄링 연결

현대 범용 운영체제는 교과서의 FCFS, SJF, Round Robin, Priority Scheduling을 그대로 단독 적용하기보다는, 다양한 정책을 조합하고 현실적인 제약을 반영한 스케줄러를 사용한다.

## Linux

Linux는 일반 작업에 대해 오랫동안 발전해 온 스케줄링 정책을 사용한다. 현재 일반적인 Linux 시스템에서 기본 일반 태스크 스케줄링은 **CFS(Completely Fair Scheduler)** 계열로 설명된다. CFS는 전통적인 Round Robin처럼 고정된 큐를 단순 순환하는 방식이 아니라, 각 태스크가 공정하게 CPU 시간을 받도록 **가상 실행 시간(vruntime)** 을 기준으로 실행 대상을 고른다.

### Linux와 관련된 스케줄링 개념

| Linux 개념 | 관련 스케줄링 개념 |
|---|---|
| nice 값 | 우선순위 조정 |
| CFS | 공정성 기반 스케줄링 |
| SCHED_FIFO | 실시간 FIFO 방식 |
| SCHED_RR | 실시간 Round Robin 방식 |
| SCHED_DEADLINE | 데드라인 기반 실시간 스케줄링 |
| CPU affinity | 특정 CPU 코어에 태스크 고정 |
| cgroups CPU controller | 프로세스 그룹별 CPU 사용량 제어 |

Linux의 `nice` 값은 일반 프로세스의 상대적 우선순위에 영향을 준다. `nice` 값이 낮을수록 더 높은 우선순위를 갖는 방향으로 동작한다. 단, 실제 CPU 배분은 스케줄링 클래스와 정책, 시스템 부하, cgroup 설정 등에 의해 함께 결정된다.

예시 명령어:

```bash
nice -n 10 ./batch_job
renice -n 5 -p <PID>
taskset -c 0,1 ./app
```

- `nice`: 프로세스 우선순위 조정
- `renice`: 실행 중인 프로세스의 nice 값 조정
- `taskset`: CPU affinity 설정

## Linux 실시간 스케줄링

Linux는 일반 작업 외에도 실시간 스케줄링 정책을 제공한다.

### SCHED_FIFO

- 같은 우선순위에서는 FIFO 방식으로 실행된다.
- 더 높은 우선순위 태스크가 나타나면 선점될 수 있다.
- 실행 중인 태스크가 스스로 양보하거나 블록되기 전까지 계속 실행될 수 있다.

### SCHED_RR

- 실시간 우선순위 기반이다.
- 같은 우선순위의 태스크들 사이에서 Round Robin 방식으로 시간 할당량을 나눠 가진다.

이 구조는 교과서의 Priority Scheduling, FCFS, Round Robin 개념과 직접적으로 연결된다.

## Windows

Windows도 우선순위 기반의 선점형 스케줄링을 사용한다. 스레드 우선순위, 동적 우선순위 조정, 양자 기반 실행 등의 개념이 존재한다. 대화형 응답성을 위해 포그라운드 작업을 우대하는 정책도 사용된다.

## Nginx

Nginx는 일반적으로 이벤트 기반 아키텍처와 worker process 모델을 사용한다. Nginx 자체는 운영체제의 CPU 스케줄러가 아니지만, 여러 worker process가 CPU를 사용하는 방식은 OS 스케줄러의 영향을 받는다.

예를 들어 CPU 코어 수에 맞춰 worker process를 설정하고, CPU affinity를 지정하면 특정 worker가 특정 CPU 코어에서 주로 실행되도록 유도할 수 있다.

```nginx
worker_processes auto;
```

`worker_processes auto`는 시스템의 CPU 자원을 고려해 worker process 수를 자동 설정하는 데 사용된다.

CPU 부하가 높은 TLS 처리, 압축, 동적 upstream 처리 등이 많아지면 Nginx worker들이 CPU 경쟁을 하게 되고, 이때 Linux 스케줄러가 worker들에게 CPU 시간을 배분한다.

## 데이터베이스 시스템

MySQL, PostgreSQL 같은 데이터베이스는 내부적으로 작업자 스레드 또는 프로세스를 사용한다. 쿼리 실행, 정렬, 인덱스 생성, 체크포인트, VACUUM 같은 백그라운드 작업은 CPU를 소비한다. 운영체제 스케줄러는 이러한 작업과 애플리케이션 프로세스 사이에서 CPU를 배분한다.

실무에서는 다음과 같은 조정이 필요할 수 있다.

- DB 프로세스의 CPU affinity 설정
- 배치 작업의 nice 값 증가
- 컨테이너 CPU limit 설정
- 백그라운드 작업 시간대 조정
- CPU steal time 모니터링

## 클라우드 VM

AWS EC2, Google Compute Engine, Azure VM 같은 클라우드 가상 머신에서는 게스트 OS 내부의 스케줄러와 호스트 하이퍼바이저의 스케줄러가 함께 관여한다.

```text
애플리케이션 스레드
   ↓
게스트 OS 스케줄러
   ↓
가상 CPU(vCPU)
   ↓
하이퍼바이저 스케줄러
   ↓
물리 CPU
```

사용자는 VM 내부에서 프로세스 스케줄링을 볼 수 있지만, 물리 호스트에서 vCPU가 실제 CPU에 어떻게 배치되는지는 클라우드 제공자의 관리 영역이다. 이 때문에 VM에서 CPU가 충분해 보이더라도, 호스트 자원 경합이 있으면 성능 변동이 발생할 수 있다.

---

---

## 클라우드 연결

# 클라우드 환경과 CPU 스케줄링

클라우드에서는 CPU 스케줄링이 단순히 운영체제 내부 문제가 아니라, **컨테이너**, **오케스트레이션**, **가상화**, **멀티 테넌시**, **비용 최적화**와 연결된다.

## Docker와 CPU 스케줄링

Docker 컨테이너는 별도의 커널을 갖는 것이 아니라 일반적으로 호스트 Linux 커널을 공유한다. 따라서 컨테이너 내부 프로세스도 결국 호스트의 Linux CPU 스케줄러에 의해 실행된다. Docker는 cgroups를 이용해 컨테이너별 CPU 사용량을 제한하거나 가중치를 줄 수 있다.

### 주요 Docker CPU 옵션

```bash
docker run --cpus="1.5" nginx
docker run --cpu-shares=512 myapp
docker run --cpuset-cpus="0,1" myapp
```

| 옵션 | 의미 |
|---|---|
| `--cpus` | 컨테이너가 사용할 수 있는 CPU 시간 제한 |
| `--cpu-shares` | CPU 경쟁 상황에서 상대적 가중치 |
| `--cpuset-cpus` | 사용할 CPU 코어 지정 |

예를 들어 `--cpus="1.5"`는 컨테이너가 CPU 시간 기준으로 약 1.5개 CPU에 해당하는 양을 사용하도록 제한하는 방식으로 이해할 수 있다. 실제 동작은 Linux cgroups CPU quota/period 설정과 연결된다.

## Kubernetes와 CPU 스케줄링

Kubernetes에서 “스케줄링”이라는 말은 두 가지 층위에서 사용된다.

1. **Kubernetes Scheduler**
   - Pod를 어느 Node에 배치할지 결정한다.
2. **Linux CPU Scheduler**
   - Node 안에서 실제 컨테이너 프로세스에 CPU 시간을 배분한다.

```text
Kubernetes Scheduler
   ↓
Pod를 Node에 배치
   ↓
컨테이너 런타임 실행
   ↓
Linux cgroups 설정
   ↓
Linux CPU Scheduler가 실제 CPU 시간 배분
```

### CPU requests와 limits

Kubernetes에서 CPU 자원은 주로 `requests`와 `limits`로 관리한다.

```yaml
resources:
  requests:
    cpu: "500m"
  limits:
    cpu: "1"
```

- `requests.cpu`
  - Pod 배치 시 필요한 최소 CPU 자원으로 사용된다.
  - 스케줄러가 Node 용량과 비교해 배치 가능 여부를 판단한다.

- `limits.cpu`
  - 컨테이너가 사용할 수 있는 CPU 상한을 설정한다.
  - Linux cgroups의 CPU 제한과 연결된다.

CPU limit이 낮게 설정된 컨테이너는 부하가 많을 때 CPU throttling을 경험할 수 있다. 이 경우 애플리케이션 응답 시간이 증가할 수 있다.

## QoS Class

Kubernetes는 Pod의 requests와 limits 설정에 따라 QoS Class를 부여한다.

- Guaranteed
- Burstable
- BestEffort

이는 CPU뿐 아니라 메모리 관리와도 연결되며, 특히 자원 경합 상황에서 어떤 Pod가 더 안정적으로 자원을 확보할 가능성이 있는지와 관련된다.

## AWS ECS와 EKS

AWS ECS와 EKS에서도 컨테이너의 CPU 설정은 중요하다.

- ECS Task Definition의 CPU 설정
- EKS Pod의 CPU requests/limits
- EC2 기반 실행 환경의 vCPU 용량
- Fargate의 CPU/Memory 조합

컨테이너가 CPU를 과도하게 사용하면 같은 노드의 다른 워크로드에 영향을 줄 수 있다. 따라서 CPU limit, autoscaling, node sizing을 함께 고려해야 한다.

## AWS Lambda

AWS Lambda는 사용자가 직접 CPU 스케줄링 정책을 설정하지 않는다. 다만 Lambda에서는 메모리 설정에 따라 CPU 등 실행 자원이 함께 조정되는 모델을 사용한다. 따라서 CPU 집약적인 함수는 메모리 설정을 늘렸을 때 실행 시간이 줄어드는 경우가 있다.

## GCP Cloud Run

Cloud Run은 컨테이너 기반 서버리스 실행 환경이다. 사용자는 컨테이너의 CPU와 메모리 할당을 설정할 수 있으며, 요청 처리 중 CPU가 얼마나 할당되는지에 따라 응답 성능이 달라질 수 있다. CPU 집약적인 작업을 처리할 때는 동시성 설정과 CPU 할당량을 함께 고려해야 한다.

## 클라우드에서 자주 발생하는 CPU 스케줄링 문제

### 1. CPU Throttling

컨테이너가 CPU limit을 초과하려고 할 때 제한되어 실행이 지연되는 현상이다.

증상:

- 응답 시간 증가
- 처리량 감소
- p99 latency 증가
- CPU 사용률은 낮아 보이는데 애플리케이션은 느림

확인 지표:

- cgroup CPU throttling metrics
- Kubernetes `container_cpu_cfs_throttled_periods_total`
- Kubernetes `container_cpu_cfs_throttled_seconds_total`

### 2. Noisy Neighbor

같은 물리 호스트나 같은 노드의 다른 워크로드가 CPU를 많이 사용하여 성능에 영향을 주는 현상이다. 클라우드 제공자는 격리와 스케줄링을 통해 이를 완화하지만, 멀티 테넌트 환경에서는 성능 변동성을 완전히 제거하기 어렵다.

### 3. Overcommit

물리 CPU보다 많은 vCPU 또는 컨테이너 CPU 요청을 배치하는 방식이다. 자원 활용률을 높일 수 있지만, 피크 시점에는 경합이 심해질 수 있다.

### 4. Autoscaling과 CPU

Horizontal Pod Autoscaler는 CPU 사용률을 기준으로 Pod 수를 늘릴 수 있다. 하지만 CPU limit이나 throttling 때문에 실제 병목이 CPU인지, I/O인지, lock contention인지 구분해야 한다.

---

---

## 보안 연결

# CPU 스케줄링과 보안

CPU 스케줄링은 성능뿐 아니라 보안과도 연결된다. 공격자가 CPU 자원을 과도하게 사용하면 서비스 가용성을 떨어뜨릴 수 있고, 우선순위 설정 오류나 자원 제한 미비는 특정 작업이 시스템을 독점하는 문제로 이어질 수 있다.

## 1. CPU 기반 서비스 거부 공격

가장 직접적인 보안 이슈는 CPU 고갈을 유도하는 **Denial of Service(DoS)** 공격이다.

예시:

- 복잡한 정규표현식 입력으로 CPU를 오래 점유하는 ReDoS
- 대량의 TLS handshake 요청
- 비싼 해시 계산을 유발하는 요청
- 압축 해제 폭탄 처리
- 이미지, PDF, 동영상 변환 요청 남용
- API 요청 폭주

공격자는 서버의 CPU를 고갈시켜 정상 요청이 스케줄링되지 못하게 만들 수 있다.

### 대응 방안

- 요청당 CPU 비용 제한
- Rate Limiting
- Timeout 설정
- 입력 크기 제한
- 비동기 작업 큐 사용
- WAF 적용
- 복잡한 연산은 별도 worker pool로 격리
- 컨테이너 CPU limit 설정

## 2. 우선순위 남용

Priority Scheduling이 있는 시스템에서는 높은 우선순위 작업이 CPU를 과도하게 점유할 수 있다. 특히 실시간 우선순위로 실행되는 프로세스가 잘못 작성되면 일반 프로세스가 실행 기회를 얻지 못할 수 있다.

예시:

```bash
chrt -f 99 ./cpu_hog
```

이와 같은 실시간 우선순위 작업은 시스템 응답성을 크게 저하시킬 수 있다.

### 모범 사례

- 실시간 우선순위는 필요한 프로세스에만 제한적으로 부여
- CPU 사용량 제한 적용
- systemd slice, cgroups로 서비스별 자원 제한
- 운영 계정 권한 최소화
- 실시간 정책 사용 권한 제한

## 3. Priority Inversion

Priority Inversion은 낮은 우선순위 작업이 락을 보유하고 있고, 높은 우선순위 작업이 그 락을 기다리는 상황에서 발생한다. 중간 우선순위 작업이 CPU를 계속 사용하면 높은 우선순위 작업은 낮은 우선순위 작업이 락을 풀 때까지 지연된다.

```text
High Priority Task: Lock 필요, 대기 중
Low Priority Task : Lock 보유, 실행 필요
Medium Task       : CPU 점유

결과: High Priority Task가 Medium Task보다도 늦게 진행
```

### 대응 방안

- Priority Inheritance
- Priority Ceiling Protocol
- 락 보유 시간 최소화
- 실시간 시스템에서 락 설계 검토

## 4. 컨테이너 간 CPU 자원 격리

컨테이너 환경에서 CPU limit을 설정하지 않으면 하나의 컨테이너가 CPU를 과도하게 사용해 같은 노드의 다른 컨테이너에 영향을 줄 수 있다.

### 모범 사례

Kubernetes 예시:

```yaml
resources:
  requests:
    cpu: "500m"
  limits:
    cpu: "1"
```

권장 사항:

- 모든 운영 워크로드에 CPU requests 설정
- CPU 집약 작업에는 별도 Node Pool 사용
- Batch Job과 latency-sensitive 서비스 분리
- HPA/VPA 사용 전 throttling 지표 확인
- BestEffort Pod 남용 방지

## 5. 사이드 채널 공격

CPU 스케줄링과 캐시, 분기 예측, SMT 같은 하드웨어 특성이 결합되면 사이드 채널 공격 가능성이 생길 수 있다. 대표적으로 CPU 캐시 타이밍 차이를 이용해 다른 작업의 정보를 추론하는 공격 계열이 연구되어 왔다.

운영체제와 클라우드 제공자는 마이크로코드 업데이트, 커널 패치, 격리 강화, SMT 제어 등의 방식으로 위험을 완화한다.

### 모범 사례

- 보안 패치와 커널 업데이트 유지
- 민감 워크로드는 전용 노드 사용 고려
- 멀티 테넌트 환경에서 격리 수준 검토
- 클라우드 제공자의 보안 권고 확인
- 고위험 환경에서는 SMT 비활성화 검토

## 6. CPU Exhaustion 모니터링

보안 관점에서는 CPU 사용률만 보는 것으로 부족하다. 다음 지표를 함께 봐야 한다.

- CPU usage
- Load average
- Run queue length
- Context switch rate
- CPU throttling
- Steal time
- p95/p99 latency
- 요청당 CPU 시간
- 특정 endpoint별 CPU 비용

이러한 지표를 통해 단순 트래픽 증가인지, 비정상적인 CPU 고갈 공격인지 구분할 수 있다.

---

---

## 면접 질문

# 면접 질문

**Q1. FCFS 스케줄링의 장단점과 Convoy Effect를 설명하세요.**  
> 핵심 답변: FCFS는 먼저 도착한 프로세스를 먼저 실행하는 비선점형 알고리즘이다. 구현이 단순하고 오버헤드가 적지만, 긴 작업이 앞에 있으면 뒤의 짧은 작업들이 오래 기다리는 Convoy Effect가 발생할 수 있다. 이로 인해 평균 대기 시간과 응답 시간이 나빠질 수 있다.

**Q2. SJF가 평균 대기 시간을 줄일 수 있는 이유와 실제 시스템에서 적용하기 어려운 이유는 무엇인가요?**  
> 핵심 답변: SJF는 CPU Burst가 짧은 작업을 먼저 실행하므로 짧은 작업들이 긴 작업 뒤에서 오래 대기하는 상황을 줄인다. 이론적으로 평균 대기 시간을 최소화하는 특성이 있다. 하지만 실제 시스템에서는 각 프로세스의 미래 CPU Burst 시간을 정확히 알기 어렵고, 긴 작업이 계속 밀리는 기아 문제가 발생할 수 있다.

**Q3. Round Robin에서 Time Quantum이 너무 작거나 너무 크면 어떤 문제가 발생하나요?**  
> 핵심 답변: Time Quantum이 너무 작으면 문맥 교환이 지나치게 자주 발생해 오버헤드가 커진다. 반대로 너무 크면 한 프로세스가 CPU를 오래 점유하므로 FCFS와 비슷해져 대화형 응답성이 떨어진다. 따라서 시스템의 문맥 교환 비용과 응답성 요구사항을 고려해 적절한 값을 설정해야 한다.

**Q4. Priority Scheduling에서 Starvation과 Aging을 설명하세요.**  
> 핵심 답변: Priority Scheduling은 우선순위가 높은 프로세스를 먼저 실행한다. 이때 낮은 우선순위 프로세스는 높은 우선순위 작업이 계속 들어오면 CPU를 받지 못하는 기아 상태가 될 수 있다. Aging은 오래 기다린 프로세스의 우선순위를 점진적으로 높여 언젠가 실행될 수 있도록 하는 기법이다.

**Q5. 멀티 레벨 큐와 멀티 레벨 피드백 큐의 차이는 무엇인가요?**  
> 핵심 답변: 멀티 레벨 큐는 프로세스를 유형별로 여러 큐에 나누고, 각 큐마다 다른 스케줄링 알고리즘을 적용할 수 있다. 일반적으로 프로세스는 한 큐에 고정된다. 반면 멀티 레벨 피드백 큐는 프로세스의 CPU 사용 패턴이나 대기 시간에 따라 큐 사이를 이동할 수 있어 더 동적인 스케줄링이 가능하다.

**Q6. 선점형 스케줄링과 비선점형 스케줄링의 차이는 무엇인가요?**  
> 핵심 답변: 비선점형은 프로세스가 CPU를 받으면 종료하거나 I/O 대기 상태가 될 때까지 계속 실행된다. 선점형은 운영체제가 타이머 인터럽트나 높은 우선순위 작업 도착 등의 이유로 실행 중인 프로세스를 중단시키고 다른 프로세스에 CPU를 줄 수 있다. 선점형은 응답성이 좋지만 문맥 교환 오버헤드가 증가한다.

**Q7. Linux의 CFS는 Round Robin과 어떻게 다른가요?**  
> 핵심 답변: Round Robin은 각 프로세스에 고정된 시간 할당량을 주고 순환 실행한다. CFS는 각 태스크의 가상 실행 시간인 vruntime을 기준으로 상대적으로 CPU를 덜 사용한 태스크를 선택하여 공정성을 추구한다. 일반 태스크에서 단순 순환 큐보다는 가중치 기반 공정 분배에 가깝다.

---

---

## 관련 개념

# 관련 개념

- [[프로세스]] - CPU 스케줄링의 기본 대상이며 실행 중인 프로그램 인스턴스를 의미한다.
- [[스레드]] -
