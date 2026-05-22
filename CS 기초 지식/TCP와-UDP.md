---
date: 2026-05-23
category: CS 기초 - 네트워크
topic: TCP와 UDP
subtopic: 특징 비교, 신뢰성 보장 메커니즘, 흐름 제어, 혼잡 제어
tags: [CS, CS-기초---네트워크, study]
---

# TCP와 UDP - 특징 비교, 신뢰성 보장 메커니즘, 흐름 제어, 혼잡 제어

## 핵심 개념

## TCP와 UDP 핵심 개념

TCP와 UDP는 모두 전송 계층(Transport Layer) 프로토콜로, 애플리케이션 간 데이터를 주고받기 위해 사용된다. 둘 다 IP 위에서 동작하지만, 제공하는 기능과 설계 목적은 크게 다르다.

**TCP(Transmission Control Protocol)**는 연결 지향형 프로토콜이다. 데이터를 보내기 전에 송신자와 수신자가 연결을 설정하고, 데이터가 순서대로, 손실 없이, 중복 없이 전달되도록 다양한 메커니즘을 제공한다. 대표적으로 **3-way handshake**, **ACK**, **재전송**, **흐름 제어**, **혼잡 제어**가 있다. HTTP/1.1, HTTP/2, SSH, SMTP, 데이터베이스 연결처럼 데이터의 정확성과 순서가 중요한 서비스에서 주로 사용된다.

반면 **UDP(User Datagram Protocol)**는 비연결형 프로토콜이다. 연결 설정 없이 데이터를 독립적인 데이터그램 단위로 전송하며, 순서 보장, 재전송, 혼잡 제어를 기본적으로 제공하지 않는다. 그 대신 구조가 단순하고 오버헤드가 작아 지연 시간이 중요한 서비스에 적합하다. DNS, VoIP, 온라인 게임, 실시간 스트리밍, QUIC 기반 HTTP/3 등이 UDP를 활용한다.

TCP와 UDP를 이해하는 것은 네트워크 성능, 장애 분석, 보안 대응, 클라우드 인프라 설계에서 매우 중요하다. 예를 들어 웹 서버의 응답 지연이 TCP 혼잡 제어 때문인지, UDP 기반 서비스가 패킷 손실에 취약한지, 로드 밸런서가 어떤 전송 계층 프로토콜을 지원하는지 판단하려면 두 프로토콜의 차이를 정확히 알아야 한다.

### TCP와 UDP 특징 비교

| 항목 | TCP | UDP |
|---|---|---|
| 연결 방식 | 연결 지향형 | 비연결형 |
| 신뢰성 | 보장 | 기본적으로 보장하지 않음 |
| 순서 보장 | 보장 | 보장하지 않음 |
| 재전송 | 지원 | 지원하지 않음 |
| 흐름 제어 | 지원 | 지원하지 않음 |
| 혼잡 제어 | 지원 | 지원하지 않음 |
| 헤더 크기 | 상대적으로 큼 | 작음 |
| 전송 단위 | 바이트 스트림 | 데이터그램 |
| 대표 사용 사례 | HTTP/1.1, HTTP/2, SSH, FTP, SMTP | DNS, DHCP, VoIP, 게임, QUIC |
| 장점 | 안정적 전송 | 낮은 지연, 단순함 |
| 단점 | 연결 설정 및 제어 오버헤드 | 손실, 중복, 순서 뒤바뀜 가능 |

---

---

## 내부 동작 원리

## TCP와 UDP 내부 동작 원리

### 1. TCP 연결 설정: 3-way Handshake

TCP는 데이터를 전송하기 전에 논리적 연결을 만든다.

```text
Client                                Server
  | -------- SYN --------------------> |
  | <------- SYN + ACK ---------------- |
  | -------- ACK --------------------> |
  |                                    |
  | ======== 데이터 전송 가능 ========= |
```

1. **SYN**  
   클라이언트가 서버에게 연결 요청을 보낸다. 이때 초기 시퀀스 번호를 포함한다.

2. **SYN + ACK**  
   서버는 클라이언트의 SYN을 확인하고, 자신의 초기 시퀀스 번호와 ACK를 보낸다.

3. **ACK**  
   클라이언트가 서버의 SYN을 확인했다는 ACK를 보낸다.

이 과정을 통해 양쪽은 서로의 초기 시퀀스 번호를 알고, 이후 데이터 순서를 추적할 수 있다.

---

### 2. TCP 데이터 전송과 신뢰성 보장

TCP는 데이터를 **바이트 스트림**으로 다룬다. 애플리케이션이 보낸 데이터는 TCP 세그먼트로 나뉘어 전송된다.

```text
Application Data
      |
      v
TCP Stream: [byte 1][byte 2][byte 3]...[byte N]
      |
      v
Segments:
[Seq=1000, Len=500]
[Seq=1500, Len=500]
[Seq=2000, Len=500]
```

TCP의 신뢰성 보장 핵심 요소는 다음과 같다.

#### 시퀀스 번호

각 바이트에는 논리적인 번호가 붙는다. 수신자는 이 번호를 보고 데이터 순서를 맞춘다.

예:

```text
송신:
Segment A: Seq=1000, Len=500
Segment B: Seq=1500, Len=500

수신:
Seq=1500이 먼저 도착해도 Seq=1000 이후에 배치
```

#### ACK

수신자는 정상적으로 받은 데이터에 대해 ACK를 보낸다. TCP의 ACK 번호는 일반적으로 “다음에 기대하는 바이트 번호”를 의미한다.

```text
송신자                              수신자
Seq=1000, Len=500  -------------> 
                     <------------- ACK=1500
```

이는 수신자가 1000부터 1499까지 받았고, 다음에는 1500번 바이트를 기대한다는 의미다.

#### 재전송

송신자는 보낸 세그먼트에 대해 일정 시간 안에 ACK를 받지 못하면 손실로 판단하고 재전송한다.

대표적인 재전송 방식은 다음과 같다.

- **타임아웃 기반 재전송**
  - RTO, Retransmission Timeout이 지나도 ACK가 오지 않으면 재전송
- **빠른 재전송**
  - 동일한 ACK가 반복적으로 오면 특정 세그먼트가 손실되었다고 판단하여 빠르게 재전송

```text
송신자                              수신자
Seq=1000  ----------------------->  수신 성공
Seq=1500  ----X 손실
Seq=2000  ----------------------->  수신했지만 1500이 없음
                     <------------- ACK=1500
                     <------------- ACK=1500
                     <------------- ACK=1500
Seq=1500  ----------------------->  빠른 재전송
```

---

### 3. TCP 흐름 제어

흐름 제어는 **수신자가 처리할 수 있는 양보다 송신자가 더 많이 보내지 않도록 조절하는 기능**이다.

TCP는 수신 측 버퍼 상태를 기반으로 **수신 윈도우, Receive Window**를 사용한다.

```text
Receiver Buffer
+-------------------------------+
| 사용 중 | 사용 가능 공간      |
+-------------------------------+
          ^
          Advertised Window
```

수신자는 ACK에 자신의 남은 버퍼 크기 정보를 포함해 송신자에게 알린다.

```text
Receiver -> Sender: ACK, Window=8000
```

송신자는 이 윈도우 크기 안에서만 데이터를 보낼 수 있다.

#### 흐름 제어의 목적

- 수신 애플리케이션이 느릴 때 버퍼 오버플로 방지
- 수신자의 메모리 상황에 맞춰 전송량 조절
- 데이터 손실과 불필요한 재전송 감소

#### Zero Window

수신 버퍼가 가득 차면 수신자는 윈도우 크기를 0으로 알릴 수 있다.

```text
Receiver -> Sender: ACK, Window=0
```

이 경우 송신자는 전송을 멈추고, 이후 윈도우가 다시 열리는지 확인한다.

---

### 4. TCP 혼잡 제어

혼잡 제어는 **네트워크 경로상의 라우터, 스위치, 링크가 감당할 수 있는 양보다 많은 트래픽이 몰리지 않도록 송신량을 조절하는 기능**이다.

흐름 제어가 “수신자 보호”라면, 혼잡 제어는 “네트워크 보호”에 가깝다.

TCP는 혼잡 윈도우, 즉 **cwnd, congestion window**를 사용한다. 실제 송신 가능한 데이터 양은 대략 다음과 같이 제한된다.

```text
실제 전송 가능량 = min(수신 윈도우 rwnd, 혼잡 윈도우 cwnd)
```

#### 대표적인 혼잡 제어 단계

##### Slow Start

처음에는 네트워크 상태를 모르기 때문에 작은 양부터 시작한다. ACK가 정상적으로 오면 cwnd를 빠르게 증가시킨다.

```text
cwnd: 1 -> 2 -> 4 -> 8 -> 16 ...
```

이름은 Slow Start지만, 실제로는 초기 탐색 구간에서 지수적으로 증가한다.

##### Congestion Avoidance

혼잡 가능성이 커지면 cwnd 증가 속도를 완만하게 조절한다.

```text
cwnd: 16 -> 17 -> 18 -> 19 ...
```

##### 손실 감지 시 감소

패킷 손실은 일반적으로 혼잡의 신호로 해석된다. TCP는 손실을 감지하면 cwnd를 줄인다.

```text
정상 증가:
cwnd = 20

손실 발생:
cwnd 감소

이후 다시 증가
```

##### Fast Retransmit / Fast Recovery

중복 ACK가 반복되면 타임아웃을 기다리지 않고 손실된 세그먼트를 재전송한다. 이후 cwnd를 급격히 초기화하지 않고 일정 수준에서 회복을 시도한다.

---

### 5. UDP 내부 동작

UDP는 TCP와 달리 연결 설정 과정이 없다.

```text
Client                                Server
  | -------- UDP Datagram ----------> |
  | -------- UDP Datagram ----------> |
  | -------- UDP Datagram ----------> |
```

각 UDP 데이터그램은 독립적으로 처리된다.

UDP 헤더에는 대표적으로 다음 정보가 포함된다.

- Source Port
- Destination Port
- Length
- Checksum

UDP는 다음을 기본적으로 보장하지 않는다.

- 데이터 도착 여부
- 데이터 순서
- 중복 제거
- 재전송
- 흐름 제어
- 혼잡 제어

따라서 필요한 경우 애플리케이션 계층에서 직접 구현해야 한다.

예를 들어 QUIC은 UDP 위에서 동작하지만, 자체적으로 연결 관리, 암호화, 재전송, 혼잡 제어 등을 제공한다.

---

---

## 실제 시스템 연결

## 실제 시스템에서의 TCP와 UDP

### 1. Linux에서 TCP/UDP 확인

Linux에서는 `ss`, `netstat`, `tcpdump`, `iptables`, `nftables` 등을 사용해 TCP와 UDP 상태를 확인할 수 있다.

#### TCP 연결 확인

```bash
ss -t
```

LISTEN 상태의 TCP 소켓 확인:

```bash
ss -ltn
```

예상 출력 형태:

```text
State   Recv-Q Send-Q Local Address:Port Peer Address:Port
LISTEN  0      128    0.0.0.0:80        0.0.0.0:*
```

TCP는 연결 상태를 가진다. 대표적인 상태는 다음과 같다.

- LISTEN
- SYN-SENT
- SYN-RECEIVED
- ESTABLISHED
- FIN-WAIT
- TIME-WAIT
- CLOSE-WAIT

#### UDP 소켓 확인

```bash
ss -u
```

LISTEN 중인 UDP 소켓 확인:

```bash
ss -lun
```

UDP는 TCP처럼 ESTABLISHED 기반의 연결 상태를 엄격하게 관리하지 않는다. 다만 커널은 소켓과 포트 정보를 관리한다.

---

### 2. Linux 커널 파라미터

Linux는 TCP 동작을 조정할 수 있는 다양한 커널 파라미터를 제공한다.

예:

```bash
sysctl net.ipv4.tcp_congestion_control
```

현재 사용 중인 TCP 혼잡 제어 알고리즘을 확인할 수 있다.

```bash
sysctl net.ipv4.tcp_available_congestion_control
```

사용 가능한 혼잡 제어 알고리즘 목록을 확인할 수 있다.

자주 언급되는 알고리즘:

- Reno
- CUBIC
- BBR

⚠️ 확인 필요: 특정 Linux 배포판이나 커널 버전에서 기본 혼잡 제어 알고리즘은 환경에 따라 다를 수 있으므로 실제 시스템에서는 `sysctl net.ipv4.tcp_congestion_control`로 확인해야 한다.

---

### 3. Nginx와 TCP

일반적인 HTTP/HTTPS 웹 서버로서 Nginx는 TCP 기반 요청을 처리한다.

```text
Client
  |
  | TCP 3-way handshake
  v
Nginx
  |
  | HTTP request
  v
Upstream Server
```

HTTP/1.1과 HTTP/2는 일반적으로 TCP 위에서 동작한다. HTTPS의 경우 TCP 연결 위에 TLS 핸드셰이크가 추가된다.

```text
TCP 연결 설정
   ↓
TLS 핸드셰이크
   ↓
HTTP 요청/응답
```

Nginx는 `keepalive`를 통해 하나의 TCP 연결을 여러 요청에 재사용할 수 있다. 이는 연결 생성 비용을 줄이는 데 도움이 된다.

---

### 4. DNS와 UDP/TCP

DNS는 일반적으로 UDP를 사용한다. UDP는 짧은 질의-응답에 적합하고 연결 설정 비용이 없다.

```text
Client ---- UDP DNS Query ----> DNS Server
Client <--- UDP DNS Answer ---- DNS Server
```

다만 DNS가 항상 UDP만 사용하는 것은 아니다. 응답 크기, 영역 전송 등 특정 상황에서는 TCP도 사용된다.

대표 예:

- 일반 DNS 질의: 주로 UDP
- DNS 응답이 크거나 잘린 경우: TCP 재시도 가능
- Zone Transfer: TCP 사용

---

### 5. 실시간 서비스와 UDP

VoIP, 영상 회의, 온라인 게임 같은 서비스는 일부 패킷 손실보다 지연 시간을 더 민감하게 본다. 이 경우 TCP의 재전송과 순서 보장이 오히려 지연을 키울 수 있다.

예:

```text
음성 패킷 1, 2, 3, 4 전송

패킷 2 손실

TCP:
패킷 2 재전송 대기 → 이후 데이터 처리 지연 가능

UDP:
패킷 2는 손실되더라도 3, 4를 즉시 처리 가능
```

그래서 실시간 서비스는 UDP를 사용하고, 애플리케이션 계층에서 손실 보정, 지터 버퍼, 순서 처리 등을 구현하는 경우가 많다.

---

---

## 클라우드 연결

## 클라우드 환경에서 TCP와 UDP

### 1. Docker와 TCP/UDP 포트 매핑

Docker 컨테이너는 포트를 노출할 때 TCP와 UDP를 구분한다.

TCP 포트 매핑:

```bash
docker run -p 8080:80 nginx
```

UDP 포트 매핑:

```bash
docker run -p 5353:53/udp some-dns-image
```

명시하지 않으면 일반적으로 TCP 포트 매핑으로 해석된다.

컨테이너 네트워크 문제를 분석할 때는 다음을 확인해야 한다.

- 컨테이너 내부 프로세스가 어떤 프로토콜로 바인딩했는지
- Docker 포트 매핑이 TCP인지 UDP인지
- 호스트 방화벽이 해당 프로토콜을 허용하는지
- NAT 과정에서 소스 포트가 어떻게 변환되는지

---

### 2. Kubernetes Service와 TCP/UDP

Kubernetes Service는 포트 정의에서 프로토콜을 지정할 수 있다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: dns-service
spec:
  selector:
    app: dns
  ports:
    - port: 53
      targetPort: 53
      protocol: UDP
```

TCP 서비스 예:

```yaml
ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
```

Kubernetes에서 기본 프로토콜은 TCP다. UDP를 사용하려면 명시적으로 `protocol: UDP`를 지정하는 것이 안전하다.

Kubernetes 네트워크 디버깅 시 TCP와 UDP의 차이는 중요하다.

- TCP는 연결 성공 여부를 비교적 쉽게 확인 가능
- UDP는 응답이 없으면 방화벽 차단인지, 애플리케이션 미응답인지, 패킷 손실인지 구분이 어려움
- readiness probe, liveness probe 설계 시 TCP/HTTP/exec 방식 선택 필요

---

### 3. AWS와 TCP/UDP

AWS에서는 여러 네트워크 서비스가 TCP와 UDP를 다룬다.

#### Elastic Load Balancing

AWS Network Load Balancer는 TCP, UDP, TLS 등 전송 계층 트래픽을 처리할 수 있다. 따라서 다음과 같은 서비스에 적합하다.

- TCP 기반 API 서버
- TLS 종료 또는 전달이 필요한 서비스
- UDP 기반 게임 서버
- DNS와 유사한 UDP 서비스

Application Load Balancer는 HTTP/HTTPS 같은 애플리케이션 계층 트래픽에 초점을 둔다. 일반적인 UDP 로드 밸런싱에는 NLB가 사용된다.

#### Security Group

Security Group 규칙에서는 프로토콜을 TCP, UDP, ICMP 등으로 구분한다.

예:

```text
Inbound Rule:
Type: HTTP
Protocol: TCP
Port: 80
Source: 0.0.0.0/0
```

DNS 서버를 열려면 UDP 53뿐 아니라 상황에 따라 TCP 53도 고려해야 한다.

---

### 4. GCP와 TCP/UDP

GCP 방화벽 규칙도 프로토콜과 포트를 기준으로 트래픽을 제어한다.

예:

```text
allow tcp:80
allow tcp:443
allow udp:53
```

로드 밸런서 종류에 따라 지원하는 계층과 프로토콜이 다르므로, TCP/UDP 서비스 배포 시 적절한 로드 밸런서를 선택해야 한다.

⚠️ 확인 필요: GCP의 특정 로드 밸런서 제품별 프로토콜 지원 범위는 시간이 지나며 변경될 수 있으므로 실제 설계 시 공식 문서를 확인해야 한다.

---

### 5. 클라우드 네트워크 장애 분석

TCP 문제와 UDP 문제는 증상이 다르게 나타난다.

#### TCP 장애 예

- SYN이 서버까지 도달하지 않음
- SYN-ACK가 돌아오지 않음
- TLS 핸드셰이크 실패
- ESTABLISHED 후 전송 지연
- TIME-WAIT 과다

분석 도구:

```bash
curl -v
telnet host port
nc -vz host port
tcpdump -i eth0 tcp port 443
```

#### UDP 장애 예

- 요청은 보냈지만 응답이 없음
- NAT 또는 방화벽에서 세션 추적 실패
- 애플리케이션이 응답하지 않음
- 패킷 크기 문제로 단편화 또는 손실 가능

분석 도구:

```bash
nc -u host port
dig @server domain.com
tcpdump -i eth0 udp port 53
```

---

---

## 보안 연결

## TCP/UDP와 보안 이슈

### 1. TCP SYN Flood

TCP는 3-way handshake 과정에서 서버가 SYN을 받은 뒤 일정 리소스를 할당한다. 공격자가 대량의 SYN을 보내고 ACK를 완료하지 않으면 서버의 연결 대기 큐가 고갈될 수 있다.

```text
Attacker ---- SYN ----> Server
Attacker ---- SYN ----> Server
Attacker ---- SYN ----> Server
             ...
Server: SYN-RECEIVED 상태 증가
```

대응 방법:

- SYN cookies 사용
- 방화벽 또는 로드 밸런서에서 rate limiting
- 비정상 트래픽 탐지
- 백로그 큐 설정 조정
- DDoS 보호 서비스 사용

Linux 관련 설정 예:

```bash
sysctl net.ipv4.tcp_syncookies
```

⚠️ 확인 필요: 운영 환경에서 커널 파라미터를 변경할 때는 애플리케이션 특성과 트래픽 패턴에 따라 부작용이 있을 수 있으므로 사전 검증이 필요하다.

---

### 2. UDP Amplification Attack

UDP는 연결 확인 없이 응답을 보낼 수 있기 때문에 IP 스푸핑과 결합하면 증폭 공격에 악용될 수 있다.

```text
Attacker spoofs Victim IP
  |
  | UDP request with victim source IP
  v
Open UDP Server
  |
  | Large response
  v
Victim
```

공격에 악용될 수 있는 UDP 기반 서비스 예:

- DNS
- NTP
- SSDP
- Memcached UDP 기능

대응 방법:

- 공개 UDP 서비스 최소화
- 재귀 DNS 서버 접근 제한
- 응답 크기 제한
- rate limiting
- BCP 38과 같은 소스 주소 검증 정책 적용
- 클라우드 DDoS 보호 사용

---

### 3. TCP 연결 고갈 공격

공격자가 다수의 TCP 연결을 열고 유지하면 서버의 파일 디스크립터, 메모리, 스레드 또는 이벤트 루프 리소스가 고갈될 수 있다.

예:

- Slowloris 공격
- Keep-Alive 연결 남용
- 애플리케이션 계층 요청 지연

대응 방법:

- 연결 타임아웃 설정
- 요청 헤더 타임아웃 설정
- 최대 연결 수 제한
- reverse proxy 사용
- WAF 또는 L7 방어 적용

Nginx 관련 설정 예:

```nginx
client_header_timeout 10s;
client_body_timeout 10s;
keepalive_timeout 65s;
limit_conn_zone $binary_remote_addr zone=addr:10m;
```

---

### 4. UDP 서비스 보안

UDP 서비스는 TCP처럼 연결 상태를 기반으로 한 인증 흐름이 없기 때문에 다음 문제가 생길 수 있다.

- 출발지 주소 위조에 취약
- 응답 기반 증폭 가능
- 상태 추적이 어려움
- 방화벽에서 허용 범위를 잘못 설정하기 쉬움

모범 사례:

- 꼭 필요한 UDP 포트만 공개
- 소스 IP 제한
- 애플리케이션 레벨 인증 또는 토큰 사용
- rate limiting
- 비정상 패킷 크기 필터링
- 로그 및 트래픽 모니터링

---

### 5. 암호화와 TCP/UDP

TCP 자체는 암호화를 제공하지 않는다. HTTPS는 TCP 위에 TLS를 올려 암호화한다.

```text
HTTP
TLS
TCP
IP
```

UDP 자체도 암호화를 제공하지 않는다. QUIC은 UDP 위에서 동작하며 TLS 1.3 기반 보안 기능을 통합한다.

```text
HTTP/3
QUIC
UDP
IP
```

즉, TCP냐 UDP냐만으로 보안성이 결정되지는 않는다. 암호화, 인증, 무결성 검증은 상위 계층 프로토콜이나 애플리케이션 설계에 의해 제공된다.

---

---

## 면접 질문

## 면접 질문

**Q1. TCP와 UDP의 가장 큰 차이는 무엇인가요?**  
> 핵심 답변: TCP는 연결 지향형이며 신뢰성, 순서 보장, 재전송, 흐름 제어, 혼잡 제어를 제공한다. UDP는 비연결형이며 이러한 기능을 기본 제공하지 않지만 오버헤드가 작고 지연 시간이 낮아 실시간 서비스에 적합하다.

**Q2. TCP는 어떻게 신뢰성을 보장하나요?**  
> 핵심 답변: 시퀀스 번호로 데이터 순서를 관리하고, ACK로 수신 여부를 확인하며, ACK가 오지 않거나 중복 ACK가 발생하면 손실로 판단해 재전송한다. 체크섬을 통해 오류 검출도 수행한다.

**Q3. TCP의 흐름 제어와 혼잡 제어의 차이는 무엇인가요?**  
> 핵심 답변: 흐름 제어는 수신자의 버퍼가 넘치지 않도록 송신량을 조절하는 기능이며 수신 윈도우를 사용한다. 혼잡 제어는 네트워크 경로의 혼잡을 줄이기 위해 송신량을 조절하는 기능이며 혼잡 윈도우를 사용한다.

**Q4. TCP 3-way handshake 과정을 설명해보세요.**  
> 핵심 답변: 클라이언트가 SYN을 보내고, 서버가 SYN+ACK로 응답하며, 클라이언트가 ACK를 보내 연결이 성립된다. 이 과정에서 양쪽은 초기 시퀀스 번호를 교환하고 이후 신뢰성 있는 데이터 전송을 준비한다.

**Q5. UDP는 신뢰성이 없는데 왜 사용하나요?**  
> 핵심 답변: 연결 설정이 없고 헤더와 제어 오버헤드가 작아 지연 시간이 낮다. 일부 패킷 손실보다 실시간성이 중요한 DNS, VoIP, 게임, 스트리밍 등에 적합하다. 필요한 신뢰성은 애플리케이션 계층에서 직접 구현할 수 있다.

---

---

## 관련 개념

## 관련 개념

- [[OSI 7계층]] - TCP와 UDP는 전송 계층에 해당하며 네트워크 계층의 IP 위에서 동작한다.
- [[IP]] - TCP와 UDP 세그먼트/데이터그램은 IP 패킷에 캡슐화되어 전달된다.
- [[3-way Handshake]] - TCP 연결 설정의 핵심 절차다.
- [[TCP 흐름 제어]] - 수신 윈도우를 이용해 수신자 버퍼를 보호하는 메커니즘이다.
- [[TCP 혼잡 제어]] - 네트워크 혼잡을 줄이기 위해 송신량을 조절하는 알고리즘 집합이다.
- [[Sliding Window]] - TCP가 여러 세그먼트를 연속 전송하고 ACK를 통해 윈도우를 이동시키는 핵심 개념이다.
- [[TLS]] - TCP 또는 QUIC 위에서 암호화와 인증을 제공하는 보안 프로토콜이다.
- [[QUIC]] - UDP 위에서 연결 관리, 암호화, 재전송, 혼잡 제어를 제공하는 전송 프로토콜이다.
- [[HTTP/3]] - QUIC 위에서 동작하는 HTTP 버전으로 UDP를 기반으로 한다.
- [[DNS]] - 주로 UDP를 사용하지만 특정 상황에서는 TCP도 사용하는 대표적인 애플리케이션 프로토콜이다.
- [[NAT]] - TCP/UDP 포트 정보를 이용해 내부와 외부 주소 변환을 수행한다.
- [[로드 밸런서]] - TCP, UDP, HTTP 등 계층별 트래픽 분산 방식이 다르다.
- [[DDoS]] - TCP SYN Flood와 UDP Amplification 같은 공격이 대표적인 네트워크 계층/전송 계층 공격이다.
