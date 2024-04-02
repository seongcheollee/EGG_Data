# 네트워크 그래프를 통한 논문 탐색 사이트 [Data]

##### 전체 프로젝트 : https://github.com/eeeeeddy/EGG
##### 그래프 데이터 API 서버 : https://github.com/seongcheollee/Egg_Graph_FastAPI
##### 도커 라이징 : https://github.com/seongcheollee/spark-yarn-docker


</div>

### Data PipeLine
<img width="600" alt="image" src="https://github.com/seongcheollee/EGG/assets/59824783/f31494d8-a5ff-4371-b5ff-994af5136b99">


# Data Flow
<img width="600" alt="image" src="https://github.com/seongcheollee/EGG_Data/assets/59824783/8a6ad6f1-cb8f-4c76-a4b2-0ba6f3a1717d">


# Graph Generate Method

Step 1: 분류, 키워드, 임베딩 추가된 데이터 가져오기

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/45f833e0-b4bd-42e9-a0d2-25584d3ffa39/f44c55bd-d208-404c-b0d7-a1e3a093aa7a/Untitled.png)
<img width="600" alt="image" src="https://github.com/seongcheollee/EGG_Data/assets/59824783/561e00cc-0422-4918-be18-2775059411f8">

**Step 2:** 참조 논문 제목 기준 그룹화 맵 생성

<img width="600" alt="image" src="https://github.com/seongcheollee/EGG_Data/assets/59824783/59184850-bd94-4566-807f-5305a1f672c8">

**Step 3:** 참조 논문 맵을 통해 기존 데이터에 연관된 논문 리스트 컬럼을 생성 

<img width="600" alt="image" src="https://github.com/seongcheollee/EGG_Data/assets/59824783/6c83ad49-e93a-4e95-b576-1bc956e2281a">


**Step 4:** networkX 를 통해 논문 그래프 생성

<img width="500" alt="image" src="https://github.com/seongcheollee/EGG_Data/assets/59824783/7939c414-3ef0-4001-b72a-dbac7b3edb51">


**Step 5:** 사용자가 한 논문을 선택할 때 하위 그래프 추출

<img width="500" alt="image" src="https://github.com/seongcheollee/EGG_Data/assets/59824783/7df8c8f8-a13f-4a16-83be-987428b6ed55">


**Step 6:** 사용자가 두 개 이상의 논문을 선택할 때 하위 그래프 추출

<img width="500" alt="image" src="https://github.com/seongcheollee/EGG_Data/assets/59824783/3eaab726-32d8-461f-9b2c-c88566ffb6b4">

**Step 7:** networkX에서 노드, 엣지 데이터 추출 및 전송 클라이언트에 전송



# [Airflow]

**수집 및 전처리**

Cycle : 1 Month

<img width="600" alt="image" src="https://github.com/seongcheollee/EGG_Data/assets/59824783/a80d90fb-2d7a-4920-b83e-b553602c6a9f">


**모델 학습**

Crawling Cycle : 1 day

Model Train Cycle : 1 Month

<img width="600" alt="image" src="https://github.com/seongcheollee/EGG_Data/assets/59824783/a9537180-b761-4531-8869-30172e6d0d2f">


