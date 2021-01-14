# Readme

![Untitled.png](Readme-images/Untitled.png)

## SOFASTCAR - Backend API

---

카셰어링 서비스 [SOCAR](https://www.socar.kr/) 의 백엔드 클론 프로젝트 입니다.

## Architecture

---

![Untitled%201.png](Readme-images/Untitled%201.png)

### Server

- Amazon EC2 - ubuntu 18.04.5 LTS

### Language

- python  3.7.5

### Framework

- Django-RestFramework 3.11

### Deploy

- production : gunicorn
- docker 사용, python 코드 배포 자동화

### Database

- AWS RDS PostgresSQL 12.3-R1

### Storage(StaticFiles)

- Amazon S3

## Tools

---

- Slack
- Google Meet, Hang out
- Drow.io
- Pycharm
- Trello
- Sentry

## 1차 스프린트 (2020.09.03 ~ 2020.09.18)

![Untitled%202.png](Readme-images/Untitled%202.png)


## 2차 스프린트 (2020.09.19 ~ 2020.10.08)
- 팀 구성원의 변경
- 1차 스프린트 미완성분에 대한 보완, 모델 재설계 작업

### MVP development
<p align="center" style="display: flex;justify-content: space-between;">
  <img width="180" height="320" src="./Readme-images/LOGIN_2nd.gif" alt="LOGIN_2nd" style="zoom: 100%;" />
  <img width="180" height="320" src="./Readme-images/SIDEBAR.gif" alt="SIDEBAR" style="zoom: 100%;" />
  <img width="180" height="360" src="./Readme-images/MAIN_2nd.gif" alt="MAIN_2nd" style="zoom: 100%;" />
  <img width="180" height="360" src="./Readme-images/RETURN.gif" alt="RETURN" style="zoom: 100%;" />
</P>

### 결과(영상)
- [로그인, 회원가입](https://youtu.be/W0kjmeD3b3g)
- [메인, 예약](https://youtu.be/RbDSDtoGo4E)
- [사용, 반납](https://youtu.be/wYxdN_Lp_Cs)
- [ARDUINO-리모콘 작동](https://youtu.be/7x6H_rOHzQA)
- [Sidebar](https://youtu.be/IRi1NMKAUaA)


## 회고
### 팀 이슈
- 첫 미팅 이후 코로나19로 인해 자택에서 프로젝트 진행하였다
- 이로 인한 문제점 발생 : 대면으로 진행한 첫 미팅때와 달리, 비대면으로 진행하자 소통이 원활하게 진행되지 않았다(커뮤니케이션의 중요성)
- 단순한 기능 분담으로는 팀워크의 시너지 효과를 기대할 수 없었다
- 프로젝트를 함께 진행하기 보다는 각자 일을 분담하여 진행하다 보니, 서로 맡은 부분에 대한 의존성 발생하여 기다리게 되는 일이 생겼다
- 팀원 개인의 사유로 인한 이탈
- 결국 혼자 백엔드 프로젝트 진행
- 모델을 세부적으로 나누어 재구성하였다
- 요청한 API 기능 완료될 때마다 ios 팀에게 전파(빠른 테스트와 피드백을 위해)
- 슬랙을 통한 실시간 피드백 대응하였다
- API 기능 자체를 개발할 때는 test case만 통과하면, 일단 어떻 기능이 작동 하는것으로 판단하고 ios팀에게 기능을 정리하여 전파하였다. 하지만 개발하다 보니 ios 팀에서 원하는 API의 모습이 따로 있었다(기능 A, B, C가 한번의 쿼리에 다 나오게 해달라 등등)

### 코드 이슈
- 기능 만들기 급급하여 코드의 반복이 많았고 조건문의 depth도 복잡해졌다
- 나중에 완성되고 코드를 나중에 다시 보니, 내가 작성한 코드도 내가 알아보기 힘들었다.
- 나 조차 내 코드를 다시 만지기 싫었다(클린 코드의 중요성)
- 모델을 만들 때 너무 막연했다(어떠한 기준이 없이 생각나는대로 만들었다)
- 기한에 쫓기게 되니 코드가 점점 의식의 흐름대로 작성되었다(코드 최적화는 어디에...)
- 클린한 코드, 남들이 봐도 이해하기 좋은 코드, OOP에 대한 개념이 부족하다는 점을 깨달았다 -> OOP 관련 공부 시작
- Django는거대한 성처럼 커다란 틀이 있어서, 왠만한 기능들이 이미 만들어져 있었다. 나는 공식 문서를 보고 필요한 기능을 찾아 쓰기만 하면 되었다
- 개발 속도는 빠른데, 그 이면에 장고가 어떻게 작동하는지 원리에 대해 알아보기엔 너무 짧은 시간이었다.
- 다른 언어, 프레임워크로 백엔드를 어떻게 개발하는지 궁금하고, 어떤 이유로 그 프레임워크를 선택했는지 비교해보고 싶었다(Express.js, spring 등)
- 결론:  더 공부하고 더 만들어봐야겠다..! 


