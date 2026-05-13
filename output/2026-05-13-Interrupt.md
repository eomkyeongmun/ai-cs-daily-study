---
date: 2026-05-13
category: Computer Architecture
topic: Interrupt
subtopic: Interrupt Handling
tags: [CS, Computer-Architecture, study]
---

# Interrupt - Interrupt Handling

## 핵심 개념

## Interrupt Handling 핵심 개념

**인터럽트 처리(Interrupt Handling)** 는 CPU가 현재 실행 중인 명령 흐름을 잠시 중단하고, 외부 장치나 내부 예외 상황에서 발생한 사건을 처리한 뒤 원래 실행 흐름으로 복귀하는 메커니즘이다. 인터럽트는 키보드 입력, 네트워크 패킷 수신, 디스크 I/O 완료, 타이머 만료, 시스템 콜, 페이지 폴트와 같은 사건을 CPU에 알리는 역할을 한다.

인터럽트의 목적은 **CPU가 모든 장치 상태를 계속 확인하는 폴링 방식의 비효율을 줄이고**, 사건이 발생했을 때만 필요한 처리를 수행하게 만드는 것이다. 예를 들어 네트워크 카드가 패킷을 수신했을 때 CPU가 계속 네트워크 카드를 확인하는 대신, 장치가 인터럽트를 발생시켜 운영체제에게 “처리할 데이터가 있다”고 알릴 수 있다.

인터럽트 처리는 컴퓨터 구조와 운영체제에서 매우 중요하다. 현대 시스템은 CPU, 메모리, 디스크, 네트워크, GPU 등 다양한 하드웨어가 병렬적으로 동작한다. 이때 인터럽트는 **비동기 이벤트를 안전하고 빠르게 처리하는 핵심 수단**이다. 또한 선점형 멀티태스킹, I/O 완료 통지, 타이머 기반 스케줄링, 예외 처리, 시스템 콜 진입 등 운영체제의 핵심 기능 대부분이 인터럽트 또는 트랩 메커니즘과 밀접하게 연결되어 있다.

인터럽트 처리가 느리거나 잘못 설계되면 시스템 전체 성능이 급격히 저하될 수 있다. 예를 들어 네트워크 인터럽트가 과도하게 발생하면 CPU가 애플리케이션 실행보다 인터럽트 처리에 더 많은 시간을 소비하는 **인터럽트 폭주(interrupt storm)** 상태가 될 수 있다. 반대로 인터럽트 처리가 너무 늦으면 I/O 지연, 패킷 손실, 실시간 시스템의 deadline miss 같은 문제가 발생할 수 있다.

---

---

## 내부 동작 원리

## 내부 동작 원리

인터럽트 처리는 하드웨어와 운영체제가 협력하여 수행한다. 일반적인 흐름은 다음과 같다.

```text
[Device]
   |
   | 1. 인터럽트 요청 IRQ 발생
   v
[Interrupt Controller]
   |
   | 2. 우선순위 판단 및 CPU에 전달
   v
[CPU]
   |
   | 3. 현재 실행 상태 저장
   | 4. 인터럽트 벡터 확인
   v
[Interrupt Handler / ISR]
   |
   | 5. 장치 상태 확인 및 최소 처리
   | 6. 필요 시 deferred work 예약
   v
[Return from Interrupt]
   |
   | 7. 저장된 문맥 복원
   v
[Original Program]
```

### 1. 인터럽트 발생

인터럽트는 크게 다음과 같이 나눌 수 있다.

- **하드웨어 인터럽트**
  - 키보드 입력
  - 네트워크 패킷 수신
  - 디스크 I/O 완료
  - 타이머 만료
- **소프트웨어 인터럽트 / 트랩**
  - 시스템 콜
  - 디버그 브레이크포인트
- **예외(Exception)**
  - 페이지 폴트
  - 0으로 나누기
  - 잘못된 명령어 실행
  - 보호 위반

하드웨어 장치는 보통 IRQ, 즉 Interrupt Request를 통해 CPU에게 처리가 필요하다는 신호를 보낸다.

### 2. 인터럽트 컨트롤러 처리

CPU가 모든 장치의 인터럽트 신호를 직접 관리하면 복잡성이 커진다. 그래서 시스템에는 보통 **인터럽트 컨트롤러**가 존재한다.

대표적인 예시는 다음과 같다.

- x86 계열의 PIC, APIC, I/O APIC
- ARM 계열의 GIC(Generic Interrupt Controller)

인터럽트 컨트롤러는 여러 장치에서 온 인터럽트를 모아 다음 작업을 수행한다.

- 어떤 인터럽트가 더 높은 우선순위를 가지는지 판단
- 현재 CPU가 인터럽트를 받을 수 있는 상태인지 확인
- 멀티코어 시스템에서 어떤 CPU 코어에 인터럽트를 전달할지 결정
- 인터럽트 번호 또는 벡터를 CPU에 전달

### 3. CPU의 현재 상태 저장

CPU는 인터럽트를 처리하기 전에 현재 실행 중이던 프로그램의 상태를 저장해야 한다. 그래야 인터럽트 처리가 끝난 후 원래 위치로 돌아올 수 있다.

일반적으로 저장되는 정보는 다음과 같다.

- Program Counter 또는 Instruction Pointer
- 상태 레지스터
- 일부 범용 레지스터
- 스택 포인터
- 권한 레벨 관련 정보

구체적으로 어떤 레지스터가 하드웨어에 의해 자동 저장되고, 어떤 레지스터가 운영체제의 인터럽트 핸들러 진입 코드에서 저장되는지는 CPU 아키텍처와 ABI에 따라 다르다.

### 4. 인터럽트 벡터 테이블 조회

CPU는 발생한 인터럽트 번호를 이용해 해당 인터럽트를 처리할 코드의 주소를 찾는다.

```text
Interrupt Vector Number
          |
          v
+---------------------------+
| Interrupt Vector Table    |
| 또는 IDT / Vector Table   |
+---------------------------+
| 0  -> Divide Error Handler|
| 1  -> Debug Handler       |
| ...                       |
| n  -> Device IRQ Handler  |
+---------------------------+
          |
          v
 Interrupt Service Routine
```

아키텍처에 따라 명칭은 다르다.

- x86: IDT, Interrupt Descriptor Table
- ARM: Vector Table

이 테이블은 운영체제가 초기화하며, 각 벡터는 특정 예외나 인터럽트 처리 루틴으로 연결된다.

### 5. ISR 실행

인터럽트 서비스 루틴, 즉 ISR(Interrupt Service Routine)은 인터럽트를 실제로 처리하는 코드다. ISR은 일반적으로 매우 짧고 빠르게 실행되어야 한다.

ISR에서 수행하는 대표 작업은 다음과 같다.

- 어떤 장치가 인터럽트를 발생시켰는지 확인
- 장치 상태 레지스터 읽기
- 인터럽트 발생 원인 확인
- 장치에게 인터럽트 처리 완료 알림
- 필요한 데이터를 커널 버퍼로 이동
- 시간이 오래 걸리는 작업은 나중에 실행되도록 예약

ISR이 짧아야 하는 이유는 인터럽트 처리 중에는 다른 인터럽트가 지연되거나, 특정 CPU에서 일반 프로세스 실행이 멈출 수 있기 때문이다.

### 6. Top Half와 Bottom Half

운영체제는 인터럽트 처리를 두 단계로 나누는 경우가 많다.

```text
Interrupt 발생
    |
    v
Top Half: 즉시 처리해야 하는 최소 작업
    |
    v
Bottom Half: 나중에 처리 가능한 작업
```

#### Top Half

Top Half는 실제 인터럽트 컨텍스트에서 실행된다. 빠르게 끝나야 하며, 일반적으로 블로킹 작업을 수행하면 안 된다.

예:

- 장치 상태 확인
- 인터럽트 acknowledge
- 데이터 수신 여부 확인
- 후속 작업 예약

#### Bottom Half

Bottom Half는 시간이 더 오래 걸릴 수 있는 작업을 나중에 처리한다.

Linux에서는 다음과 같은 메커니즘이 사용된다.

- softirq
- tasklet  
  ⚠️ 확인 필요: tasklet은 Linux 커널에서 오랫동안 사용되었지만, 커널 버전에 따라 사용 권장 여부와 내부 구현 방향이 달라질 수 있다.
- workqueue
- threaded interrupt handler

예를 들어 네트워크 패킷 수신의 경우, NIC가 인터럽트를 발생시키면 Top Half는 최소한의 확인만 수행하고, 실제 패킷 처리 대부분은 softirq 또는 NAPI polling 과정에서 처리될 수 있다.

### 7. 인터럽트 반환

인터럽트 핸들러가 끝나면 CPU는 저장했던 실행 상태를 복원하고 원래 프로그램으로 돌아간다. 이때 사용되는 명령은 아키텍처별로 다르다.

예:

- x86: `iret`, `iretq`
- ARM: 예외 반환 메커니즘 사용

인터럽트 반환 시 CPU는 다음을 복원한다.

- 이전 명령 실행 위치
- 이전 권한 레벨
- 플래그 또는 상태 레지스터
- 스택 상태

이 과정을 통해 프로그램은 마치 잠깐 멈췄다가 다시 이어서 실행되는 것처럼 동작한다.

---

---

## 실제 시스템 연결

## 실제 시스템 연결

### Linux의 인터럽트 처리

Linux는 하드웨어 인터럽트를 커널 내부의 IRQ subsystem을 통해 관리한다. 각 장치는 IRQ 번호에 연결될 수 있고, 해당 IRQ에는 하나 이상의 핸들러가 등록될 수 있다.

Linux에서 인터럽트 정보를 확인할 때 자주 사용하는 파일은 다음과 같다.

```bash
cat /proc/interrupts
```

예시 형태:

```text
           CPU0       CPU1
  24:      1000       2000  IO-APIC  eth0
  25:       500        300  IO-APIC  nvme0q1
```

`/proc/interrupts`는 각 IRQ가 어떤 CPU에서 몇 번 처리되었는지 보여준다. 네트워크 카드, 스토리지 컨트롤러, 타이머, 인터프로세서 인터럽트 등이 표시될 수 있다.

### Linux 네트워크 처리와 인터럽트

고속 네트워크 환경에서는 패킷마다 인터럽트를 발생시키면 CPU 부하가 매우 커질 수 있다. 이를 완화하기 위해 Linux 네트워크 스택은 **NAPI(New API)** 방식을 사용한다.

NAPI의 기본 아이디어는 다음과 같다.

```text
패킷 수신
   |
   v
NIC 인터럽트 발생
   |
   v
커널이 인터럽트 일부 비활성화
   |
   v
polling 방식으로 여러 패킷을 한 번에 처리
   |
   v
처리 완료 후 인터럽트 재활성화
```

즉, 낮은 트래픽에서는 인터럽트 기반으로 빠르게 반응하고, 높은 트래픽에서는 polling에 가까운 방식으로 전환하여 인터럽트 폭주를 줄인다.

### SMP 시스템과 IRQ Affinity

멀티코어 시스템에서는 특정 IRQ를 어떤 CPU 코어에서 처리할지 조정할 수 있다. 이를 **IRQ affinity**라고 한다.

Linux에서는 다음 경로를 통해 IRQ affinity를 설정할 수 있다.

```bash
/proc/irq/<IRQ_NUMBER>/smp_affinity
```

예를 들어 네트워크 인터럽트를 특정 CPU에 몰아주거나, 애플리케이션이 실행되는 CPU와 분리하여 성능을 튜닝할 수 있다.

다만 IRQ affinity 설정은 시스템 구조, NUMA 구조, NIC 큐 구성, 애플리케이션 스레드 배치와 함께 고려해야 한다.

### MSI와 MSI-X

전통적인 인터럽트는 별도의 하드웨어 라인을 통해 전달되는 방식이었지만, 현대 PCI Express 장치에서는 **MSI(Message Signaled Interrupts)** 또는 **MSI-X**를 사용할 수 있다.

MSI/MSI-X는 장치가 특정 메모리 주소에 메시지를 쓰는 방식으로 인터럽트를 전달한다. 특히 MSI-X는 여러 인터럽트 벡터를 사용할 수 있어 멀티큐 NIC나 NVMe 장치에서 CPU 병렬 처리를 개선하는 데 유용하다.

### Nginx와 인터럽트

Nginx 자체는 사용자 공간 애플리케이션이므로 하드웨어 인터럽트를 직접 처리하지 않는다. 하지만 Nginx의 네트워크 성능은 NIC 인터럽트 처리, 커널 네트워크 스택, softirq, CPU affinity, epoll 이벤트 처리와 밀접하게 연결된다.

예를 들어 고성능 웹 서버에서는 다음 요소들이 함께 고려된다.

- NIC RX/TX queue 개수
- IRQ affinity
- Receive Packet Steering, Receive Flow Steering
- NAPI
- softirq CPU 사용률
- Nginx worker process CPU pinning

즉, Nginx 요청 처리 성능 저하가 실제로는 애플리케이션 코드가 아니라 커널의 인터럽트 및 네트워크 처리 병목에서 발생할 수 있다.

---

---

## 클라우드 연결

## 클라우드 연결

### 가상화 환경에서의 인터럽트

클라우드 VM에서는 게스트 OS가 실제 물리 장치를 직접 다루지 않는 경우가 많다. 대신 하이퍼바이저가 물리 장치를 관리하고, 게스트에는 가상 장치를 제공한다.

```text
[Physical NIC]
     |
     v
[Host Kernel / Hypervisor]
     |
     v
[Virtual Interrupt]
     |
     v
[Guest OS Interrupt Handler]
     |
     v
[Application]
```

이때 인터럽트는 다음 형태로 처리될 수 있다.

- 물리 장치 인터럽트
- 하이퍼바이저의 이벤트 처리
- 게스트 OS에 전달되는 가상 인터럽트
- virtio 같은 paravirtualized device의 이벤트 알림

가상화 계층이 추가되면 인터럽트 전달 경로가 길어질 수 있으므로, 클라우드 네트워크 성능에서는 인터럽트 처리 비용과 가상 I/O 최적화가 중요하다.

### AWS와 인터럽트

AWS EC2 인스턴스에서는 인스턴스 타입과 가상화 방식에 따라 네트워크 및 스토리지 I/O 경로가 달라진다. AWS의 Nitro 기반 인스턴스는 전용 하드웨어와 경량화된 하이퍼바이저를 사용하여 네트워크와 스토리지 가상화 오버헤드를 줄이는 구조로 설명된다.

⚠️ 확인 필요: 특정 인스턴스 타입에서 인터럽트가 어떤 방식으로 배치되고 몇 개의 MSI-X 벡터를 사용하는지는 인스턴스 세대, ENA 드라이버 버전, 커널 버전에 따라 달라질 수 있다.

AWS에서 네트워크 성능을 분석할 때는 다음 요소를 확인한다.

- ENA 드라이버 사용 여부
- 네트워크 인터페이스 큐 개수
- `/proc/interrupts`
- softirq 사용률
- CPU steal time
- PPS(Packet Per Second) 한계
- 인스턴스 타입별 네트워크 성능 제한

### GCP와 인터럽트

GCP의 Compute Engine VM도 가상 네트워크 장치를 통해 패킷을 처리한다. Linux 게스트에서는 virtio-net 또는 gVNIC 같은 네트워크 인터페이스가 사용될 수 있다.

⚠️ 확인 필요: 특정 GCP VM 머신 타입에서 기본적으로 사용되는 네트워크 드라이버와 인터럽트 큐 구성은 이미지, 머신 타입, OS 버전에 따라 다를 수 있다.

GCP에서도 고성능 네트워크 애플리케이션을 운영할 때는 다음 항목이 중요하다.

- NIC 드라이버
- 멀티큐 활성화 여부
- IRQ affinity
- vCPU 수
- 커널 네트워크 스택 튜닝
- 패킷 처리량과 CPU 사용률의 관계

### Docker와 인터럽트

Docker 컨테이너는 독립된 커널을 가지는 것이 아니라 일반적으로 **호스트 OS 커널을 공유**한다. 따라서 하드웨어 인터럽트 처리는 컨테이너 내부가 아니라 호스트 커널에서 수행된다.

```text
[Physical NIC]
    |
    v
[Host Kernel Interrupt Handler]
    |
    v
[Host Network Stack]
    |
    v
[Container Network Namespace]
    |
    v
[Container Process]
```

컨테이너 내부의 애플리케이션이 네트워크 패킷을 받더라도, 실제 NIC 인터럽트는 호스트 커널이 처리한다. 따라서 컨테이너 네트워크 성능 문제를 분석할 때는 컨테이너 내부뿐 아니라 호스트의 `/proc/interrupts`, softirq, NIC queue, veth, bridge, iptables/nftables 처리도 확인해야 한다.

### Kubernetes와 인터럽트

Kubernetes는 직접 인터럽트를 관리하지 않는다. 하지만 Kubernetes 워크로드의 성능은 노드의 CPU 배치와 커널 인터럽트 처리에 영향을 받을 수 있다.

고성능 또는 저지연 워크로드에서는 다음을 고려한다.

- CPU Manager의 static policy
- Guaranteed QoS Pod
- CPU pinning
- isolcpus 같은 커널 부팅 옵션
- IRQ affinity 조정
- NUMA-aware 배치
- SR-IOV CNI 사용

예를 들어 패킷 처리량이 중요한 NFV(Network Function Virtualization) 워크로드에서는 SR-IOV를 사용해 컨테이너 또는 Pod가 물리 NIC의 Virtual Function에 가깝게 접근하도록 구성할 수 있다. 이 경우에도 인터럽트 처리는 CPU affinity, NUMA locality, NIC queue 구성과 함께 튜닝해야 한다.

---

---

## 보안 연결

## 보안 연결

### 1. 인터럽트 폭주를 이용한 서비스 거부

장치나 외부 입력이 과도한 인터럽트를 발생시키면 CPU가 정상 작업보다 인터럽트 처

---

## 면접 질문



---

## 관련 개념


