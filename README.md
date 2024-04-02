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

**Step 1:** 분류, 키워드, 임베딩 추가된 데이터 가져오기

<img width="400" alt="image" src="https://github.com/seongcheollee/EGG_Data/assets/59824783/dcf54c71-8495-48cd-a669-97cca8306ec9">

<img width="600" alt="image" src="https://github.com/seongcheollee/EGG_Data/assets/59824783/561e00cc-0422-4918-be18-2775059411f8">

**Step 2:** 참조 논문 제목 기준 articleID Explode

<img width="400" alt="image" src="https://github.com/seongcheollee/EGG_Data/assets/59824783/36b0c457-1d42-425e-b077-7823c0bbd6a4">

**Step 3:** 연관관계 테이블 생성

<img width="400" alt="image" src="https://github.com/seongcheollee/EGG_Data/assets/59824783/3cf7ee4d-08b1-491b-a833-118840f1eda7">


**Step 4:** 최종 데이터 산출

<img width="400" alt="image" src="https://github.com/seongcheollee/EGG_Data/assets/59824783/bdefa374-ae22-4555-9f5c-abf1635075b8">

<img width="600" alt="image" src="https://github.com/seongcheollee/EGG_Data/assets/59824783/f9ff1e69-82a3-4224-91f6-200134565be7">



**Step 5:** 연관 관계 데이터 및 networkX 를 통해 논문 그래프 생성

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


